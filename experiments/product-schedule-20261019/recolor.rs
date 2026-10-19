//! Conservative exact lifetime coloring. Reset is the only release boundary.
mod io;
use quantum_ecc::circuit::{Op,OperationType as K,QubitId};
use std::collections::{BTreeSet,HashSet};
const NO:u64=u64::MAX;
fn and(a:Option<bool>,b:Option<bool>)->Option<bool>{match(a,b){(Some(false),_)|(_,Some(false))=>Some(false),(Some(true),x)|(x,Some(true))=>x,_=>None}}
fn select(a:Option<bool>,b:Option<bool>,g:Option<bool>)->Option<bool>{match g{Some(true)=>b,Some(false)=>a,None=>if a==b{a}else{None}}}
fn color(v:&[Op])->(Vec<Op>,serde_json::Value){
 let nq=v.iter().flat_map(|o|[o.q_control2.0,o.q_control1.0,o.q_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;
 let nb=v.iter().flat_map(|o|[o.c_condition.0,o.c_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;
 let mut c=vec![Some(false);nb];let mut pinned=HashSet::new();
 for o in v{if o.kind==K::AppendToRegister{if o.q_target.0!=NO{pinned.insert(o.q_target.0);}if o.c_target.0!=NO{c[o.c_target.0 as usize]=None;}}}
 let mut free:BTreeSet<u64>=(0..nq as u64).filter(|q|!pinned.contains(q)).collect();
 let mut map=vec![NO;nq];for &q in &pinned{map[q as usize]=q;}
 let mut stack=vec![];let mut guard=Some(true);let mut out=Vec::with_capacity(v.len());let mut peak=pinned.iter().max().map_or(0,|q|q+1);let mut epochs=0;let mut dead=0;
 for original in v{
  let mut o=*original;
  if matches!(o.kind,K::Register|K::AppendToRegister){out.push(o);continue;}
  if o.kind==K::PushCondition{stack.push(guard);guard=and(guard,c[o.c_condition.0 as usize]);out.push(o);continue;}
  if o.kind==K::PopCondition{guard=stack.pop().unwrap();out.push(o);continue;}
  let eff=if o.c_condition.0==NO{guard}else{and(guard,c[o.c_condition.0 as usize])};
  if eff==Some(false){dead+=1;continue;}
  for q in [o.q_control2.0,o.q_control1.0,o.q_target.0]{if q!=NO&&map[q as usize]==NO{let p=free.pop_first().expect("coloring ran out of physical wires");map[q as usize]=p;epochs+=1;}}
  for q in [&mut o.q_control2,&mut o.q_control1,&mut o.q_target]{if q.0!=NO{q.0=map[q.0 as usize];peak=peak.max(q.0+1);}}
  o.validate();out.push(o);
  if matches!(original.kind,K::R|K::Hmr)&&eff==Some(true)&&!pinned.contains(&original.q_target.0){let q=original.q_target.0 as usize;assert!(free.insert(map[q]));map[q]=NO;}
  if original.c_target.0!=NO{let t=original.c_target.0 as usize;let new=match original.kind{K::BitStore0=>Some(false),K::BitStore1=>Some(true),K::BitInvert=>c[t].map(|x|!x),K::Hmr=>None,_=>c[t]};c[t]=select(c[t],new,eff);}
 }
 assert!(stack.is_empty());
 (out,serde_json::json!({"status":"EXACT_CONSERVATIVE_RECOLOR_DIAGNOSTIC","original_physical_Q":nq,"recolored_physical_Q":peak,"pinned_qubits":pinned.len(),"scratch_epochs":epochs,"provably_dead_operations_removed":dead,"release_rule":"Only guaranteed unconditional-in-context R/Hmr resets. Unknown guards never release a wire. Register wires pinned from op zero."}))
}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),3);let v=io::load_ops(&a[1]);let(out,mut data)=color(&v);io::save_ops(&format!("{}.ops.bin",a[2]),&out);data["input"]=serde_json::json!(a[1]);data["input_count"]=serde_json::json!(v.len());data["output_count"]=serde_json::json!(out.len());std::fs::write(format!("{}.json",a[2]),serde_json::to_string_pretty(&data).unwrap()).unwrap();println!("{}",data);}
#[cfg(test)]mod tests{
 use super::*;use quantum_ecc::circuit::{BitId,RegisterId};
 fn op(k:K,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_target=QubitId(t);o}
 fn reg(q:u64)->Op{let mut o=op(K::AppendToRegister,q);o.r_target=RegisterId(0);o}
 #[test]fn unconditional_reset_allows_physical_reuse(){let(v,d)=color(&[reg(0),op(K::X,4),op(K::R,4),op(K::X,3),op(K::R,3)]);assert_eq!(d["recolored_physical_Q"],2);assert_eq!(v[1].q_target,v[3].q_target);}
 #[test]fn late_registered_input_is_pinned(){let(v,d)=color(&[op(K::X,2),op(K::R,2),reg(0)]);assert_eq!(d["recolored_physical_Q"],2);assert_eq!(v[2].q_target,QubitId(0));assert_eq!(v[0].q_target,QubitId(1));}
 #[test]fn unknown_reset_does_not_release(){let mut bit=Op::empty();bit.kind=K::AppendToRegister;bit.c_target=BitId(0);bit.r_target=RegisterId(1);let mut reset=op(K::R,2);reset.c_condition=BitId(0);let(v,d)=color(&[reg(0),bit,op(K::X,2),reset,op(K::X,3)]);assert_eq!(d["recolored_physical_Q"],3);assert_ne!(v[2].q_target,v[4].q_target);}
 #[test]fn false_guard_drops_only_unexecuted_operation(){let mut x=op(K::X,3);x.c_condition=BitId(0);let(v,d)=color(&[reg(0),x,op(K::X,2)]);assert_eq!(d["provably_dead_operations_removed"],1);assert_eq!(v.len(),2);assert_eq!(d["recolored_physical_Q"],2);}
}
