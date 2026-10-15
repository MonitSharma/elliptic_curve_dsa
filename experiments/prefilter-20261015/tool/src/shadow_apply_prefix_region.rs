// Prefix-specialized normalization: every accepted replacement is checked by
// exact symbolic XOR=0 against the actual current global input functions.
// Unproved outputs retain the actual execution expression. No local entry
// assumptions or empirical invariants are introduced.
struct PrefixShadowReceipt{mr:usize,chosen_zero:Vec<u64>,chosen_reset:Vec<u64>,retained_rng:Vec<u64>,region_digest:[u8;32]}
// Evaluate a certified region on the current global symbolic state. This keeps
// actual HMR assignments, draws and snapshots, while evaluating a private zero-MR
// classical shadow. The caller selects ONLY outputs covered by the local theorem.
fn shadow_apply_prefix_region(ops:&[Op],a:&mut GlobalAnf,q:&mut[GlobalPoly],b:&mut[GlobalPoly],base:&GlobalPoly)->PrefixShadowReceipt {
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
    let mut chosen_zero=Vec::new();let mut chosen_reset=Vec::new();let mut retained_rng=Vec::new();
    for (id,local) in qs.iter().zip(0..qs.len()) {
        let orig=&actual.q[local];let score=|a:&GlobalAnf,p:&GlobalPoly|p.0.iter().filter(|(k,c)|!k.is_empty()&&a.dag.find(*c)!=0).count();
        let mut value=orig.clone();let mut best=score(a,orig);let mut choice=2;
        if best!=0{let dz=a.xor(orig,&zero.q[local]);if dz.0.iter().all(|(_,c)|a.dag.find(*c)==0){let next=score(a,&zero.q[local]);if next<best{value=zero.q[local].clone();best=next;choice=0;}}
        if best!=0{let dr=a.xor(orig,&reset[local]);if dr.0.iter().all(|(_,c)|a.dag.find(*c)==0){let next=score(a,&reset[local]);if next<best{value=reset[local].clone();choice=1;}}}}
        if choice==0{chosen_zero.push(*id);}else if choice==1{chosen_reset.push(*id);}
        if score(a,&value)!=0{retained_rng.push(*id);}q[*id as usize]=value;
    }
    for (id,local) in bs.iter().zip(0..bs.len()){b[*id as usize]=actual.b[local].clone();}
    PrefixShadowReceipt{mr,chosen_zero,chosen_reset,retained_rng,region_digest:shadow_region_digest(ops)}
}


#[cfg(test)]mod prefix_shadow_tests{use super::*;
 fn op(k:OperationType,a:u64,b:u64,t:u64,bt:u64,c:u64)->Op{Op{kind:k,q_control1:QubitId(a),q_control2:QubitId(b),q_target:QubitId(t),c_target:BitId(bt),c_condition:BitId(c),r_target:RegisterId(u64::MAX)}}
 fn value(a:&GlobalAnf,p:&GlobalPoly,input:u64,random:u64)->bool{p.0.iter().fold(false,|acc,(key,c)|acc^(global_anf_tests::eval(&a.dag,*c,input)&&key.iter().all(|s|random>>s&1!=0)))}
 #[test]fn exact_prefix_alias_and_complement_relations_are_used_without_assumptions(){let n=u64::MAX;for complement in [false,true]{let mut a=GlobalAnf::new(32);let x=a.dag.variable(false);let y=if complement{a.dag.not(x)}else{x};let mut q=vec![GlobalAnf::constant(x),GlobalAnf::constant(y),GlobalAnf::constant(1)];let mut b=vec![GlobalAnf::constant(0)];let mut ops=vec![op(OperationType::Hmr,n,n,2,0,n),op(OperationType::CX,0,n,2,n,0),op(OperationType::CX,1,n,2,n,0)];if complement{ops.push(op(OperationType::X,n,n,2,n,0));}shadow_apply_prefix_region(&ops,&mut a,&mut q,&mut b,&GlobalAnf::constant(1));assert!(q[2].0.is_empty());}}
 #[test]fn exact_prefix_product_relation_is_used(){let n=u64::MAX;let mut a=GlobalAnf::new(32);let x=a.dag.variable(false);let y=a.dag.variable(false);let xy=a.dag.and(x,y);let mut q=vec![GlobalAnf::constant(x),GlobalAnf::constant(y),GlobalAnf::constant(xy),GlobalAnf::constant(1)];let mut b=vec![GlobalAnf::constant(0)];let ops=[op(OperationType::Hmr,n,n,3,0,n),op(OperationType::CX,2,n,3,n,0),op(OperationType::CCX,0,1,3,n,0)];shadow_apply_prefix_region(&ops,&mut a,&mut q,&mut b,&GlobalAnf::constant(1));assert!(q[3].0.is_empty());}
 #[test]fn unrelated_entry_values_keep_real_measurement_dependence(){let n=u64::MAX;let mut a=GlobalAnf::new(32);let x=a.dag.variable(false);let y=a.dag.variable(false);let mut q=vec![GlobalAnf::constant(x),GlobalAnf::constant(y),GlobalAnf::constant(1)];let mut b=vec![GlobalAnf::constant(0)];let ops=[op(OperationType::Hmr,n,n,2,0,n),op(OperationType::CX,0,n,2,n,0),op(OperationType::CX,1,n,2,n,0)];let r=shadow_apply_prefix_region(&ops,&mut a,&mut q,&mut b,&GlobalAnf::constant(1));assert!(r.retained_rng.contains(&2));for input in 0..4{for random in 0..2{assert_eq!(value(&a,&q[2],input,random),((input&1!=0)^(input&2!=0))&&(random&1!=0));}}}
}
