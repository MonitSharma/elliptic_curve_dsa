//! One source-bound reversible cache. No new qubit, bit, measurement or reset.
use crate::circuit::{Op,OperationType as K,QubitId};
use sha3::{Digest,Sha3_256};
const FIRST:usize=14_241_681;
const LAST:usize=14_245_297;
const STORAGE:u64=558;
const INPUT_OPS:usize=17_889_539;
const INPUT_HASH:&str="f7fa435b667246a0eb96ab403b557871133c69de3deae09f9680d97e978a028f";
const NO:u64=u64::MAX;
fn fields(o:&Op)->[u64;7]{[o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]}
fn hash(v:&[Op])->String{let mut h=Sha3_256::new();for o in v{for x in fields(o){h.update(x.to_le_bytes());}}format!("{:x}",h.finalize())}
fn cx(a:u64,t:u64)->Op{let mut o=Op::empty();o.kind=K::CX;o.q_control1=QubitId(a);o.q_target=QubitId(t);o.validate();o}
fn rewrite(ops:Vec<Op>,first:usize,last:usize,storage:u64)->Vec<Op>{
 assert!(first<last&&last<ops.len());assert!(storage!=NO);
 let a=ops[first];let b=ops[last];assert_eq!(a.kind,K::CCX);assert_eq!(b.kind,K::CCX);
 assert_eq!(a.c_condition.0,NO);assert_eq!(b.c_condition.0,NO);
 assert!(!ops.iter().any(|o|o.kind==K::AppendToRegister&&o.q_target.0==storage));
 let mut depth=0usize;
 for(i,o)in ops.iter().enumerate(){
  if i==first||i==last{assert_eq!(depth,0,"fixed endpoints must be outside all captured scopes");}
  match o.kind{K::PushCondition=>depth+=1,K::PopCondition=>depth=depth.checked_sub(1).expect("balanced scopes"),_=>{}}
  if(first..=last).contains(&i){assert!(![o.q_control1.0,o.q_control2.0,o.q_target.0].contains(&storage),"storage must have no original quantum touch, including phase gates");}
 }
 assert_eq!(depth,0);
 let mut out=Vec::with_capacity(ops.len()+2);
 for(i,o)in ops.into_iter().enumerate(){
  if i==first{let mut held=o;held.q_target=QubitId(storage);held.validate();out.push(held);out.push(cx(storage,o.q_target.0));}
  else if i==last{out.push(cx(storage,o.q_target.0));out.push(cx(o.q_target.0,storage));}
  else{out.push(o);}
 }
 out
}
pub(super) fn run(ops:Vec<Op>)->Vec<Op>{
 assert_eq!(ops.len(),INPUT_OPS,"frozen parent length");assert_eq!(hash(&ops),INPUT_HASH,"frozen parent contents");
 assert_eq!(fields(&ops[FIRST]),[13,258,724,616,NO,NO,NO]);assert_eq!(fields(&ops[LAST]),[13,724,258,215,NO,NO,NO]);
 let result=rewrite(ops,FIRST,LAST,STORAGE);assert_eq!(result.len(),INPUT_OPS+2);result
}
#[cfg(test)]#[path="tests_copy_cache_one.rs"]mod tests;
