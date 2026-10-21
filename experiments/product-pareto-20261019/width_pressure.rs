mod io;
use quantum_ecc::circuit::{Op,OperationType as K};
use std::collections::HashSet;
fn and(a:Option<bool>,b:Option<bool>)->Option<bool>{match(a,b){(Some(false),_)|(_,Some(false))=>Some(false),(Some(true),x)|(x,Some(true))=>x,_=>None}}
fn set(old:Option<bool>,new:Option<bool>,guard:Option<bool>)->Option<bool>{match guard{Some(true)=>new,Some(false)=>old,None=>if old==new{old}else{None}}}
fn profile(ops:&[Op])->serde_json::Value{
 let no=u64::MAX;
 let nq=ops.iter().flat_map(|o|[o.q_target.0,o.q_control1.0,o.q_control2.0]).filter(|x|*x!=no).max().unwrap()as usize+1;
 let nb=ops.iter().flat_map(|o|[o.c_target.0,o.c_condition.0]).filter(|x|*x!=no).max().map_or(0,|x|x as usize+1);
 let mut pinned=HashSet::new();let mut c=vec![Some(false);nb];
 for o in ops{if o.kind==K::AppendToRegister{if o.q_target.0!=no{pinned.insert(o.q_target.0);}if o.c_target.0!=no{c[o.c_target.0 as usize]=None;}}}
 let mut start=vec![None;nq];let mut last=vec![0;nq];let mut spans:Vec<(usize,usize,u64)>=vec![];
 let mut stack=vec![];let mut guard=Some(true);let mut dead=0;
 for(i,o)in ops.iter().enumerate(){
  if matches!(o.kind,K::Register|K::AppendToRegister){continue;}
  if o.kind==K::PushCondition{stack.push(guard);guard=and(guard,c[o.c_condition.0 as usize]);continue;}
  if o.kind==K::PopCondition{guard=stack.pop().unwrap();continue;}
  let eff=if o.c_condition.0==no{guard}else{and(guard,c[o.c_condition.0 as usize])};
  if eff==Some(false){dead+=1;continue;}
  for w in [o.q_control2.0,o.q_control1.0,o.q_target.0]{if w!=no&&!pinned.contains(&w){let w=w as usize;if start[w].is_none(){start[w]=Some(i);}last[w]=i;}}
  if matches!(o.kind,K::R|K::Hmr)&&eff==Some(true)&&!pinned.contains(&o.q_target.0){let w=o.q_target.0 as usize;if let Some(s)=start[w].take(){spans.push((s,i,w as u64));}}
  if o.c_target.0!=no{let t=o.c_target.0 as usize;let new=match o.kind{K::BitStore0=>Some(false),K::BitStore1=>Some(true),K::BitInvert=>c[t].map(|x|!x),K::Hmr=>None,_=>c[t]};c[t]=set(c[t],new,eff);}
 }
 assert!(stack.is_empty());
 // A scratch value without a guaranteed final reset remains live until EOF,
 // including for the protected dirty-ancilla check.
 for(w,s)in start.iter().enumerate(){if let Some(s)=s{spans.push((*s,ops.len(),w as u64));}}
 let mut events:Vec<(usize,i32)>=vec![];for &(s,e,_)in &spans{events.push((s,1));events.push((e+1,-1));}events.sort();
 let mut live=0;let mut peak=0;let mut first_peak=0;let mut x=0;
 while x<events.len(){let at=events[x].0;let mut d=0;while x<events.len()&&events[x].0==at{d+=events[x].1;x+=1;}live+=d;if live>peak{peak=live;first_peak=at;}}
 let active:Vec<_>=spans.iter().filter(|&&(s,e,_)|s<=first_peak&&first_peak<=e).map(|&(s,e,w)|serde_json::json!({"wire":w,"start":s,"end":e})).collect();
 serde_json::json!({"status":"CONSERVATIVE_LIFETIME_DIAGNOSTIC_NOT_A_SCORE","physical_wire_count":nq,"pinned_registered_qubits":pinned.len(),"scratch_lifetime_count":spans.len(),"peak_simultaneous_lifetimes":pinned.len()+peak as usize,"first_peak_op":first_peak,"provably_dead_operations":dead,"scratch_at_first_peak":active,"assumptions":"All registered quantum wires pinned throughout; only guaranteed resets end epochs; unknown conditions never treated as true. Closed intervals overlap at endpoints. Persistent dirty scratch extends to EOF."})
}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),3);let ops=io::load_ops(&a[1]);let mut result=profile(&ops);result["input"]=serde_json::json!(a[1]);std::fs::write(&a[2],serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("wire_count={} conservative_peak={}",result["physical_wire_count"],result["peak_simultaneous_lifetimes"]);}
#[cfg(test)]mod tests{
 use super::*;use quantum_ecc::circuit::{QubitId,BitId,RegisterId};
 fn op(k:K,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_target=QubitId(t);o}
 #[test]fn late_input_metadata_is_pinned_from_start(){let mut r=op(K::AppendToRegister,0);r.r_target=RegisterId(0);let v=profile(&[op(K::X,1),op(K::R,1),r]);assert_eq!(v["peak_simultaneous_lifetimes"],2);}
 #[test]fn unknown_reset_cannot_end_lifetime(){let mut r=Op::empty();r.kind=K::AppendToRegister;r.c_target=BitId(0);r.r_target=RegisterId(2);let mut reset=op(K::R,0);reset.c_condition=BitId(0);let v=profile(&[r,op(K::X,0),reset,op(K::X,1)]);assert_eq!(v["peak_simultaneous_lifetimes"],2);}
 #[test]fn unconditional_reset_allows_reuse(){let v=profile(&[op(K::X,0),op(K::R,0),op(K::X,1),op(K::R,1)]);assert_eq!(v["peak_simultaneous_lifetimes"],1);}
}
