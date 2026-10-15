// Universal local value contract. Entry quantum/classical values are arbitrary.
// Actual classical writes remain authoritative. Shadow classical writes are only
// used to evaluate the internal-MR=0 quantum action. Each quantum output must
// equal either that deterministic shadow or the actual-guard reset projection.
#[derive(Clone)]
struct ShadowCertificate {
    proved: bool, status: &'static str, quantum_ids: Vec<u64>, choices: Vec<u8>,
    classical_wires: usize, ops: usize, mr: usize, nodes: usize, caps: usize,
    unresolved: usize, seconds: f64,
}
#[derive(Clone)]
struct ShadowState { q: Vec<GlobalPoly>, b: Vec<GlobalPoly>, base: GlobalPoly,
    stack: Vec<GlobalPoly> }
fn shadow_value_contract(ops: &[Op], node_limit: usize, millis: u64) -> ShadowCertificate {
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
    let q:Vec<_>=(0..qs.len()).map(|_|{let id=a.dag.variable(false);GlobalAnf::constant(id)}).collect();
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
    ShadowCertificate{proved:status=="EXACT_PROOF",status,quantum_ids:qs.into_iter().collect(),choices,
        classical_wires:bs.len(),ops:ops.len(),mr,nodes:a.dag.nodes.len(),caps:a.capped,unresolved,seconds:timer.elapsed().as_secs_f64()}
}
#[cfg(test)] mod shadow_tests {
    use super::*;
    fn op(k:OperationType,a:u64,t:u64,bt:u64,c:u64)->Op{Op{kind:k,q_control1:QubitId(a),q_control2:QubitId(u64::MAX),q_target:QubitId(t),c_target:BitId(bt),c_condition:BitId(c),r_target:RegisterId(u64::MAX)}}
    #[test]fn real_deterministic_arithmetic_is_certified(){let n=u64::MAX;let ops=[op(OperationType::CX,0,1,n,n)];let c=shadow_value_contract(&ops,10000,1000);assert!(c.proved);assert_eq!(c.choices,vec![0,0]);}
    #[test]fn measurement_data_update_is_not_certified(){let n=u64::MAX;let ops=[op(OperationType::Hmr,n,1,0,n),op(OperationType::X,n,0,n,0)];assert!(!shadow_value_contract(&ops,10000,1000).proved);}
    #[test]fn arbitrary_dirty_conditional_reset_is_retained(){let n=u64::MAX;let ops=[op(OperationType::Hmr,n,1,0,n),op(OperationType::R,n,0,n,0)];let c=shadow_value_contract(&ops,10000,1000);assert!(c.proved);assert_eq!(c.choices,vec![1,0]);}
    #[test]fn same_measurement_guard_twice_cancels_for_dirty_data(){let n=u64::MAX;let ops=[op(OperationType::Hmr,n,1,0,n),op(OperationType::X,n,0,n,0),op(OperationType::X,n,0,n,0)];let c=shadow_value_contract(&ops,10000,1000);assert!(c.proved);}
    #[test]fn entry_classical_bit_remains_an_arbitrary_parameter(){let n=u64::MAX;let ops=[op(OperationType::X,n,0,n,0)];assert!(shadow_value_contract(&ops,10000,1000).proved);}
    #[test]fn cap_and_scope_errors_are_never_certificates(){let n=u64::MAX;let ops=[op(OperationType::CX,0,1,n,n)];assert!(!shadow_value_contract(&ops,0,1000).proved);let ops=[op(OperationType::PopCondition,n,n,n,n)];assert!(!shadow_value_contract(&ops,10000,1000).proved);}
}
