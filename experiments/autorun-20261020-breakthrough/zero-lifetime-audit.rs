//! Read-only nominal lifetime/color audit. Does not emit a replacement circuit.
mod io;
use quantum_ecc::circuit::{OperationType as K,Op,analyze_ops};
use sha3::{Digest,Sha3_256};
use std::collections::{BTreeSet,HashSet};
fn qs(o:&Op)->Vec<u64>{let mut q=vec![o.q_control2.0,o.q_control1.0,o.q_target.0];q.retain(|x|*x!=u64::MAX);q.sort_unstable();q.dedup();q}
fn prefix(a:&[usize],b:&[usize])->bool{a.len()<=b.len()&&a==&b[..a.len()]}
fn main(){
 let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),3);let ops=io::load_ops(&a[1]);let(nq,nb,_,_)=analyze_ops(ops.iter());
 let pinned:HashSet<_>=ops.iter().filter(|o|matches!(o.kind,K::Register|K::AppendToRegister)).flat_map(qs).collect();
 let mut free:BTreeSet<_>=(0..nq).filter(|q|!pinned.contains(q)).collect();
 let mut map:Vec<_>=(0..nq).map(|q|if pinned.contains(&q){Some(q)}else{None}).collect();
 let mut dom:Vec<Option<Vec<usize>>>=vec![None;nq as usize];let mut stack=Vec::new();
 let(mut current,mut peak,mut max_id)=(pinned.len(),pinned.len(),pinned.iter().copied().max().unwrap_or(0));
 let(mut resets,mut guarded_closes,mut zero_releases,mut lifetimes,mut blocked)=(0usize,0usize,0usize,0usize,0usize);let mut hash=Sha3_256::new();let mut peak_at=0;
 for(i,o)in ops.iter().enumerate(){
  if o.kind==K::PushCondition{stack.push(i);}else if o.kind==K::PopCondition{assert!(stack.pop().is_some());}
  let used=qs(o);
  for &q in &used{if map[q as usize].is_none(){let color=free.pop_first().expect("original qubit bound suffices for injective active mapping");map[q as usize]=Some(color);current+=1;lifetimes+=1;max_id=max_id.max(color);}}
  if current>peak{peak=current;peak_at=i;}
  let target=o.q_target.0;
  let writes:Vec<_>=match o.kind{K::X|K::CX|K::CCX=>vec![target],K::Swap=>used.clone(),_=>vec![]};
  for q in writes{if pinned.contains(&q){continue;}let d=&mut dom[q as usize];if let Some(old)=d{let len=old.iter().zip(&stack).take_while(|(a,b)|a==b).count();old.truncate(len);}else{*d=Some(stack.clone());}}
  if matches!(o.kind,K::R|K::Hmr)&&!pinned.contains(&target){
   let can=dom[target as usize].as_ref().is_none_or(|d|o.c_condition.0==u64::MAX&&prefix(&stack,d));
   if can{dom[target as usize]=None;resets+=1;if !stack.is_empty(){guarded_closes+=1;}}else{blocked+=1;}
  }
  let get=|q:u64|if q==u64::MAX{q}else{map[q as usize].unwrap()};
  for v in [o.kind as u64,get(o.q_control2.0),get(o.q_control1.0),get(o.q_target.0),o.c_target.0,o.c_condition.0,o.r_target.0]{hash.update(v.to_le_bytes());}
  for q in used{if !pinned.contains(&q)&&dom[q as usize].is_none(){let color=map[q as usize].take().unwrap();assert!(free.insert(color));current-=1;zero_releases+=1;}}
 }
 assert!(stack.is_empty());let remaining=map.iter().filter(|m|m.is_some()).count();assert_eq!(remaining,current);
 let result=serde_json::json!({"status":"READ_ONLY_DOMINATED_RESET_ZERO_LIFETIME_COLOR_AUDIT_NOT_PROVED_REWRITE_OR_SCORE","input":a[1],"operations":ops.len(),"original_qubits":nq,"classical_bits":nb,"registered_pinned_qubits":pinned.len(),"max_pinned_id":pinned.iter().max(),"provisional_max_physical_id_plus_one":max_id+1,"provisional_peak_active_slots":peak,"peak_at_operation":peak_at,"lifetimes":lifetimes,"proved_dominated_reset_closures":resets,"guarded_closures":guarded_closes,"known_zero_slot_releases":zero_releases,"resets_not_covering_all_prior_write_scopes":blocked,"remaining_live_slots":remaining,"provisional_renamed_records_sha3":format!("{:x}",hash.finalize()),"scope":"Read-only audit. Helper begins zero; value-write scopes tracked by exact lexical Push identity common-prefix. R/HMR closes only when unconditional-per-op reset scope dominates all possible nonzero write scopes. Knownzero reads can release after record. Registered inputs pinned. No gates, conditions, classical bits or RNG draws changed, but provisional mapping requires independent native phase/value/RNG/fault proof before any emitted candidate or score claim."});std::fs::write(&a[2],serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("{result}");
}
