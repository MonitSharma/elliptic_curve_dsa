// Evaluate a certified region on the current global symbolic state. This keeps
// actual HMR assignments, draws and snapshots, while evaluating a private zero-MR
// classical shadow. The caller selects ONLY outputs covered by the local theorem.
fn shadow_apply_region(ops:&[Op],a:&mut GlobalAnf,q:&mut[GlobalPoly],b:&mut[GlobalPoly],base:&GlobalPoly,certificate:&ShadowCertificate)->usize {
    use OperationType::*;
    let mut qs=std::collections::BTreeSet::new();
    let mut bs=std::collections::BTreeSet::new(); let mut mr=0;
    for o in ops {
        if matches!(o.kind,X|CX|CCX|Swap|R|Hmr) {qs.insert(o.q_target.0);}
        if matches!(o.kind,CX|CCX|Swap) {qs.insert(o.q_control1.0);}
        if o.kind==CCX {qs.insert(o.q_control2.0);}
        if o.c_condition.0!=u64::MAX {bs.insert(o.c_condition.0);}
        if matches!(o.kind,Hmr|BitStore0|BitStore1|BitInvert) {bs.insert(o.c_target.0);}
        mr+=usize::from(matches!(o.kind,Hmr|R));
    }
    let qids:std::collections::HashMap<_,_>=qs.iter().enumerate().map(|(i,x)|(*x,i)).collect();
    let bids:std::collections::HashMap<_,_>=bs.iter().enumerate().map(|(i,x)|(*x,i)).collect();

    assert!(certificate.proved);assert_eq!(certificate.operation_digest,shadow_region_digest(ops),"local certificate/source-region mismatch");assert_eq!(certificate.quantum_ids,qs.iter().copied().collect::<Vec<_>>());
    let inputq:Vec<_>=qs.iter().map(|id|q[*id as usize].clone()).collect();
    let inputb:Vec<_>=bs.iter().map(|id|b[*id as usize].clone()).collect();
    let mut actual=ShadowState{q:inputq.clone(),b:inputb,base:base.clone(),stack:Vec::new()};
    let mut zero=actual.clone();let mut reset=inputq;let mut status="EXACT_PROOF";
    for o in ops.iter() {
        if matches!(o.kind,Neg|Z|CZ|CCZ|Register|AppendToRegister|DebugPrint) {continue;}
        if o.kind==PopCondition {
            if actual.stack.is_empty()||zero.stack.is_empty() {status="UNKNOWN_UNBALANCED_SCOPE";break;}
            actual.base=actual.stack.pop().unwrap();zero.base=zero.stack.pop().unwrap();continue;
        }
        let ca=if o.c_condition.0==u64::MAX {actual.base.clone()}else{a.and(&actual.base,&actual.b[bids[&o.c_condition.0]])};
        let cz=if o.c_condition.0==u64::MAX {zero.base.clone()}else{a.and(&zero.base,&zero.b[bids[&o.c_condition.0]])};
        let random=if matches!(o.kind,Hmr|R){a.fresh()}else{GlobalAnf::constant(0)};
        if matches!(o.kind,Hmr|R) {let t=qids[&o.q_target.0];let nc=a.not(&ca);reset[t]=a.and(&reset[t],&nc);}
        for (s,c,fresh) in [(&mut actual,ca,random),(&mut zero,cz,GlobalAnf::constant(0))] {
            match o.kind {
                CCX=>{let v=a.and(&s.q[qids[&o.q_control1.0]],&s.q[qids[&o.q_control2.0]]);let v=a.and(&v,&c);let t=qids[&o.q_target.0];s.q[t]=a.xor(&s.q[t],&v);},
                CX=>{let v=a.and(&s.q[qids[&o.q_control1.0]],&c);let t=qids[&o.q_target.0];s.q[t]=a.xor(&s.q[t],&v);},
                X=>{let t=qids[&o.q_target.0];s.q[t]=a.xor(&s.q[t],&c);},
                Swap=>{let t=qids[&o.q_target.0];let u=qids[&o.q_control1.0];let v=a.xor(&s.q[t],&s.q[u]);let v=a.and(&v,&c);s.q[t]=a.xor(&s.q[t],&v);s.q[u]=a.xor(&s.q[u],&v);},
                Hmr|R=>{let t=qids[&o.q_target.0];let nc=a.not(&c);s.q[t]=a.and(&s.q[t],&nc);if o.kind==Hmr{let bt=bids[&o.c_target.0];let old=a.and(&s.b[bt],&nc);let new=a.and(&fresh,&c);s.b[bt]=a.xor(&old,&new);}},
                BitStore0=>{let bt=bids[&o.c_target.0];let nc=a.not(&c);s.b[bt]=a.and(&s.b[bt],&nc);},
                BitStore1=>{let bt=bids[&o.c_target.0];let nc=a.not(&c);let old=a.and(&s.b[bt],&nc);s.b[bt]=a.xor(&old,&c);},
                BitInvert=>{let bt=bids[&o.c_target.0];s.b[bt]=a.xor(&s.b[bt],&c);},
                PushCondition=>{s.stack.push(s.base.clone());s.base=c;},_=>unreachable!()
            }
        }
    }

    assert_eq!(status,"EXACT_PROOF");assert!(actual.stack.is_empty()&&zero.stack.is_empty());
    for ((id,choice),local) in qs.iter().zip(&certificate.choices).zip(0..qs.len()) {
        q[*id as usize]=match choice {0=>zero.q[local].clone(),1=>reset[local].clone(),_=>panic!("uncertified shadow output")};
    }
    for (id,local) in bs.iter().zip(0..bs.len()){b[*id as usize]=actual.b[local].clone();}
    mr
}

#[cfg(test)]mod shadow_apply_tests{use super::*;
 struct Repeated(u64);impl XofReader for Repeated{fn read(&mut self,out:&mut[u8]){assert_eq!(out.len()%8,0);for c in out.chunks_mut(8){c.copy_from_slice(&self.0.to_le_bytes());}}}
 fn op(k:OperationType,a:u64,t:u64,bt:u64,c:u64)->Op{Op{kind:k,q_control1:QubitId(a),q_control2:QubitId(u64::MAX),q_target:QubitId(t),c_target:BitId(bt),c_condition:BitId(c),r_target:RegisterId(u64::MAX)}}
 fn eval(a:&GlobalAnf,p:&GlobalPoly,r:u64,base:u64)->u64{let d=&a.dag;let mut v=vec![0u64;d.nodes.len()];v[1]=u64::MAX;for(i,n)in d.nodes.iter().enumerate().skip(2){v[i]=match n.kind{2=>base,3=>v[n.a as usize]^v[n.b as usize],4=>v[n.a as usize]&v[n.b as usize],7=>d.large_defs[n.a as usize].iter().fold(0,|x,m|x^d.monomials[*m as usize].iter().fold(u64::MAX,|x,j|x&v[*j as usize])),8=>[n.a,n.b].iter().fold(u64::MAX,|x,m|x&d.monomials[*m as usize].iter().fold(u64::MAX,|x,j|x&v[*j as usize])),_=>panic!()};}p.0.iter().fold(0,|acc,(key,c)|acc^(v[*c as usize]&if key.is_empty(){u64::MAX}else{r}))}
 #[test]fn lifted_shadow_transition_matches_protected_dirty_states_and_mixed_base(){let n=u64::MAX;let cases=vec![vec![op(OperationType::CX,0,1,n,n)],vec![op(OperationType::Hmr,n,1,0,n),op(OperationType::R,n,0,n,0)],vec![op(OperationType::Hmr,n,1,0,n),op(OperationType::X,n,0,n,0),op(OperationType::X,n,0,n,0)],vec![op(OperationType::PushCondition,n,n,n,0),op(OperationType::Hmr,n,1,1,n),op(OperationType::PopCondition,n,n,n,n)]];
 for ops in cases{let cert=shadow_value_contract(&ops,10000,1000);assert!(cert.proved);for entry in 0..16u64{for random in [0,u64::MAX,0xa5967cb3a5967cb3]{for mask in [0,u64::MAX,0x00ff0ff0f00ff00f]{let mut a=GlobalAnf::new(32);let mut q=vec![GlobalAnf::constant((entry&1)as u32),GlobalAnf::constant(((entry>>1)&1)as u32)];let mut b=vec![GlobalAnf::constant(((entry>>2)&1)as u32),GlobalAnf::constant(((entry>>3)&1)as u32)];let base=GlobalAnf::constant(a.dag.variable(false));let mut words=Repeated(random);let mut sim=Simulator::new(2,3,&mut words);for i in 0..2{sim.qubits[i]=if entry>>i&1!=0{u64::MAX}else{0};sim.bits[i]=if entry>>(i+2)&1!=0{u64::MAX}else{0};}sim.bits[2]=mask;let mut wrapped=vec![op(OperationType::PushCondition,n,n,n,2)];wrapped.extend(ops.iter().cloned());wrapped.push(op(OperationType::PopCondition,n,n,n,n));shadow_apply_region(&ops,&mut a,&mut q,&mut b,&base,&cert);sim.apply_iter(wrapped.iter());for i in 0..2{assert_eq!(eval(&a,&q[i],random,mask),sim.qubits[i]);assert_eq!(eval(&a,&b[i],random,mask),sim.bits[i]);}}}}}
 }
 #[test]fn changed_operation_with_same_wire_set_rejects_certificate(){let n=u64::MAX;let original=[op(OperationType::CX,0,1,n,n)];let changed=[op(OperationType::CX,1,0,n,n)];let cert=shadow_value_contract(&original,10000,1000);let mut a=GlobalAnf::new(32);let mut q=vec![GlobalAnf::constant(0);2];let mut b=Vec::new();assert!(std::panic::catch_unwind(std::panic::AssertUnwindSafe(||shadow_apply_region(&changed,&mut a,&mut q,&mut b,&GlobalAnf::constant(1),&cert))).is_err());}
}
