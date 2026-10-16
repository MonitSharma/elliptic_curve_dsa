struct RelationObligations{operation_digest:[u8;32],quantum_ids:Vec<u64>,input_nodes:Vec<u32>,differences:Vec<[GlobalPoly;2]>,complete:bool,status:&'static str,dag:Dag,caps:usize}
// Substitute exact declared quantum-entry functions. Classical entry bits and
// all fresh/capped MR symbols remain arbitrary outer variables; requiring every
// substituted coefficient to be zero is sufficient, never a sampled criterion.
fn relation_substitute(local:&RelationObligations,global:&mut Dag,entry:&[u32])->Vec<u32>{
 assert!(local.complete);assert_eq!(entry.len(),local.input_nodes.len());
 let ports:std::collections::HashMap<_,_>=local.input_nodes.iter().zip(entry).filter(|(p,_)|**p>1).map(|(p,r)|(*p,*r)).collect();
 let d=&local.dag;let mut map=vec![u32::MAX;d.nodes.len()];map[0]=0;map[1]=1;
 for i in 2..d.nodes.len(){let id=d.find(i as u32);if id!=i as u32{map[i]=map[id as usize];continue;}let n=d.nodes[i];assert!(!n.random);let raw=match n.kind{
  2=>*ports.get(&(i as u32)).expect("undeclared opaque local input"),
  3|4=>{let a=map[d.find(n.a)as usize];let b=map[d.find(n.b)as usize];assert_ne!(a,u32::MAX);assert_ne!(b,u32::MAX);if n.kind==3{global.xor(a,b)}else{global.and(a,b)}},
  7=>{let t=d.construction[i];let a=map[d.find(t.a)as usize];let b=map[d.find(t.b)as usize];assert_ne!(a,u32::MAX);assert_ne!(b,u32::MAX);let v=match t.kind{3=>global.xor(a,b),4=>global.and(a,b),_=>panic!("missing exact definition")};if t.invert{global.not(v)}else{v}},
  8=>{let mut product=1;for m in[n.a,n.b]{for j in d.monomials[m as usize].iter(){let v=map[d.find(*j)as usize];assert_ne!(v,u32::MAX);product=global.and(product,v);}}product},_=>panic!("missing exact coefficient definition")};map[i]=raw;
 }map
}
fn relation_options(local:&RelationObligations,global:&Dag,map:&[u32])->Vec<[Vec<u32>;2]>{local.differences.iter().map(|pair|std::array::from_fn(|which|{let mut roots:Vec<_>=pair[which].0.iter().map(|(_,c)|global.find(map[local.dag.find(*c)as usize])).filter(|c|*c!=0).collect();roots.sort_unstable();roots.dedup();roots})).collect()}
fn relation_obligations(ops: &[Op], node_limit: usize, millis: u64, known_zero: &std::collections::BTreeSet<u64>) -> RelationObligations {
    use OperationType::*;
    let timer=std::time::Instant::now();
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
    let mut a=GlobalAnf::new(32);
    let q:Vec<_>=qs.iter().map(|wire|{if known_zero.contains(wire){GlobalAnf::constant(0)}else{let id=a.dag.variable(false);GlobalAnf::constant(id)}}).collect();
    let input_nodes:Vec<_>=q.iter().map(|p|p.0.first().map(|(_,c)|*c).unwrap_or(0)).collect();
    let b:Vec<_>=(0..bs.len()).map(|_|a.fresh()).collect();
    let mut actual=ShadowState{q:q.clone(),b,base:GlobalAnf::constant(1),stack:Vec::new()};
    let mut zero=actual.clone(); let mut reset=q; let mut status="EXACT_PROOF";
    for (i,o) in ops.iter().enumerate() {
        if i%128==0&&(a.dag.nodes.len()>node_limit||a.capped>5000||timer.elapsed().as_millis()>millis as u128) {
            status="UNKNOWN_RESOURCE_LIMIT"; break;
        }
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
    let mut choices=Vec::new();let mut unresolved=0;
    if status=="EXACT_PROOF" {
        if !actual.stack.is_empty()||!zero.stack.is_empty(){status="UNKNOWN_UNBALANCED_SCOPE";}
        else {for ((orig,z),r) in actual.q.iter().zip(&zero.q).zip(&reset) {
            let d=a.xor(orig,z);
            if d.0.iter().all(|(_,c)|a.dag.find(*c)==0){choices.push(0);continue;}
            let d=a.xor(orig,r);
            if d.0.iter().all(|(_,c)|a.dag.find(*c)==0){choices.push(1);continue;}
            choices.push(2);unresolved+=1;
        }if unresolved!=0{status="UNKNOWN_DIFFERENCE_NOT_PROVED_ZERO";}}
    }
    let differences=actual.q.iter().zip(&zero.q).zip(&reset).map(|((actual,zero),reset)|[a.xor(actual,zero),a.xor(actual,reset)]).collect();
    RelationObligations{operation_digest:shadow_region_digest(ops),quantum_ids:qs.into_iter().collect(),input_nodes,differences,complete:status=="EXACT_PROOF"||status=="UNKNOWN_DIFFERENCE_NOT_PROVED_ZERO",status,dag:a.dag,caps:a.capped}
}

#[cfg(test)]mod relation_tests{use super::*;
 fn op(k:OperationType,a:u64,t:u64,bt:u64,c:u64)->Op{Op{kind:k,q_control1:QubitId(a),q_control2:QubitId(u64::MAX),q_target:QubitId(t),c_target:BitId(bt),c_condition:BitId(c),r_target:RegisterId(u64::MAX)}}
 #[test]fn exact_entry_alias_cancels_but_wrong_relation_stays_unknown(){let n=u64::MAX;let ops=[op(OperationType::Hmr,n,3,0,n),op(OperationType::CX,1,0,n,0),op(OperationType::CX,2,0,n,0)];let local=relation_obligations(&ops,10000,1000,&Default::default());assert!(local.complete);let mut g=Dag::new();let x=g.variable(false);let y=g.variable(false);let mut entry=vec![x;local.quantum_ids.len()];let m=relation_substitute(&local,&mut g,&entry);assert!(relation_options(&local,&g,&m).iter().all(|options|options[0].is_empty()));entry[local.quantum_ids.iter().position(|q|*q==2).unwrap()]=y;let m=relation_substitute(&local,&mut g,&entry);assert!(relation_options(&local,&g,&m).iter().any(|options|!options[0].is_empty()&&!options[1].is_empty()));}
 #[test]fn complemented_entry_relation_is_proved_exactly(){let n=u64::MAX;let ops=[op(OperationType::Hmr,n,3,0,n),op(OperationType::X,n,0,n,0),op(OperationType::CX,1,0,n,0),op(OperationType::CX,2,0,n,0)];let local=relation_obligations(&ops,10000,1000,&Default::default());let mut g=Dag::new();let x=g.variable(false);let nx=g.not(x);let mut entry=vec![x;local.quantum_ids.len()];entry[local.quantum_ids.iter().position(|q|*q==2).unwrap()]=nx;let m=relation_substitute(&local,&mut g,&entry);assert!(relation_options(&local,&g,&m).iter().all(|options|options[0].is_empty()));}
}
