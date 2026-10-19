//! Preserve every captured classical condition in a fresh immutable bit.
//! Pure classical macros; all original quantum operations retain their order.
use crate::circuit::{Op,OperationType as K,BitId};
use std::collections::HashMap;
const NO:u64=u64::MAX;
fn capture(base:u64,condition:u64,ver:&[u64],next:&mut u64,cache:&mut HashMap<(u64,u64,u64),u64>,out:&mut Vec<Op>)->u64{
 assert_ne!(condition,NO);let key=(base,condition,ver[condition as usize]);if let Some(&b)=cache.get(&key){return b;}
 let b=*next;*next+=1;if base!=NO{let mut p=Op::empty();p.kind=K::PushCondition;p.c_condition=BitId(base);out.push(p);}
 let mut s=Op::empty();s.kind=K::BitStore1;s.c_target=BitId(b);s.c_condition=BitId(condition);out.push(s);
 if base!=NO{let mut p=Op::empty();p.kind=K::PopCondition;out.push(p);}cache.insert(key,b);b
}
pub(super) fn run(ops:Vec<Op>)->Vec<Op>{
 let nb=ops.iter().flat_map(|o|[o.c_target.0,o.c_condition.0]).filter(|&b|b!=NO).max().unwrap_or(0)as usize+1;
 let mut ver=vec![0u64;nb];let mut next=nb as u64;let mut cache=HashMap::new();let(mut base,mut stack)=(NO,vec![]);let mut out=Vec::with_capacity(ops.len());
 for o in ops{match o.kind{
 K::PushCondition=>{stack.push(base);base=capture(base,o.c_condition.0,&ver,&mut next,&mut cache,&mut out);},
 K::PopCondition=>base=stack.pop().expect("balanced original condition stack"),
 _=>{let mut g=o;if !matches!(o.kind,K::Register|K::AppendToRegister)&&base!=NO{g.c_condition=BitId(if o.c_condition.0==NO{base}else{capture(base,o.c_condition.0,&ver,&mut next,&mut cache,&mut out)});}g.validate();out.push(g);if matches!(o.kind,K::Hmr|K::BitInvert|K::BitStore0|K::BitStore1){ver[o.c_target.0 as usize]+=1;}}
 }}assert!(stack.is_empty());out
}
#[cfg(test)]mod tests{
 use super::*;use crate::{circuit::{QubitId,RegisterId},sim::Simulator};use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
 fn op(k:K,q:u64,c:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_target=QubitId(q);o.c_target=BitId(c);o}
 fn fixture(nested:bool)->Vec<Op>{let mut v=vec![];let mut qr=op(K::AppendToRegister,0,NO);qr.r_target=RegisterId(0);v.push(qr);let mut cr=op(K::AppendToRegister,NO,0);cr.r_target=RegisterId(1);v.push(cr);let mut push=op(K::PushCondition,NO,NO);push.c_condition=BitId(0);v.push(push);v.push(op(K::X,1,NO));v.push(op(K::BitInvert,NO,0));if nested{v.push(push);}let mut x=op(K::CX,0,NO);x.q_control1=QubitId(1);x.c_condition=BitId(0);v.push(x);v.push(op(K::Hmr,1,0));if nested{v.push(op(K::PopCondition,NO,NO));}v.push(op(K::X,2,NO));v.push(op(K::PopCondition,NO,NO));v.push(op(K::R,2,NO));v}
 fn simulate(v:&[Op],q:u64,c:u64,seed:u64)->(Vec<u64>,u64,u64,u64,[u8;64]){let nb=v.iter().flat_map(|o|[o.c_target.0,o.c_condition.0]).filter(|&b|b!=NO).max().unwrap_or(0)as usize+1;let mut h=Shake256::default();h.update(&seed.to_le_bytes());let mut r=h.finalize_xof();let mut s=Simulator::new(4,nb,&mut r);s.qubits[0]=q;s.bits[0]=c;s.phase=0x5555aaaaffff0000;s.apply_iter(v.iter());let state=(s.qubits.clone(),s.bits[0],s.phase,s.stats.toffoli_gates);drop(s);let mut t=[0;64];r.read(&mut t);(state.0,state.1,state.2,state.3,t)}
 #[test]fn captured_source_mutation_and_measurement_preserve_transcript(){let v=fixture(false);let w=run(v.clone());for q in [0,u64::MAX,0x5555aaaaffff0000]{for c in [0,u64::MAX,0xaaaa5555ffff0000]{for seed in 0..8{assert_eq!(simulate(&v,q,c,seed),simulate(&w,q,c,seed));}}}}
 #[test]fn nested_direct_and_inactive_conditions_preserve_transcript(){let v=fixture(true);let w=run(v.clone());for q in [0,u64::MAX,0x5555aaaaffff0000]{for c in [0,u64::MAX,0xaaaa5555ffff0000]{for seed in 0..8{assert_eq!(simulate(&v,q,c,seed),simulate(&w,q,c,seed));}}}}
}
