//! Release every logical wire only on guaranteed resets or proved zero events.
//! Registered inputs start at their original positions; swaps restore outputs.
mod io;
use quantum_ecc::circuit::{Op,OperationType as K,QubitId};
use std::collections::{BTreeSet,HashMap,HashSet};
const NO:u64=u64::MAX;
fn and(a:Option<bool>,b:Option<bool>)->Option<bool>{match(a,b){(Some(false),_)|(_,Some(false))=>Some(false),(Some(true),x)|(x,Some(true))=>x,_=>None}}
fn select(a:Option<bool>,b:Option<bool>,g:Option<bool>)->Option<bool>{match g{Some(true)=>b,Some(false)=>a,None=>if a==b{a}else{None}}}
fn color(v:&[Op],events:&[(usize,u64)])->(Vec<Op>,serde_json::Value){
 let nq=v.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;
 let nb=v.iter().flat_map(|o|[o.c_condition.0,o.c_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;
 let mut c=vec![Some(false);nb];let mut registered=BTreeSet::new();
 for o in v{if o.kind==K::AppendToRegister{if o.q_target.0!=NO{registered.insert(o.q_target.0);}if o.c_target.0!=NO{c[o.c_target.0 as usize]=None;}}}
 let mut free:BTreeSet<u64>=(0..nq as u64).collect();let mut map=vec![NO;nq];let mut owner=vec![NO;nq];
 for &q in &registered{map[q as usize]=q;owner[q as usize]=q;free.remove(&q);}
 let mut z:HashMap<usize,Vec<u64>>=HashMap::new();for &(i,q)in events{assert!(i<v.len()&&q<nq as u64);z.entry(i).or_default().push(q);}
 let mut stack=vec![];let mut guard=Some(true);let mut out=Vec::with_capacity(v.len());let mut peak=registered.iter().max().map_or(0,|q|q+1);let mut epochs=0;let mut dead=0;let mut zero_releases=0;let mut registered_releases=0;let mut full_regions:Vec<(usize,usize)>=vec![];let mut live_peak=registered.len();let mut output_allocations=0;let mut zero_skips=0;let mut zero_kinds=[0usize;18];let mut zero_t_always=0;let mut zero_t_conditional=0;
 let release=|q:u64,map:&mut Vec<u64>,owner:&mut Vec<u64>,free:&mut BTreeSet<u64>|{let p=map[q as usize];if p!=NO{assert_eq!(owner[p as usize],q);assert!(free.insert(p));map[q as usize]=NO;owner[p as usize]=NO;true}else{false}};
 for(i,original)in v.iter().enumerate(){let mut o=*original;
  if matches!(o.kind,K::Register|K::AppendToRegister){out.push(o);continue;}
  if o.kind==K::PushCondition{stack.push(guard);guard=and(guard,c[o.c_condition.0 as usize]);out.push(o);continue;}
  if o.kind==K::PopCondition{guard=stack.pop().unwrap();out.push(o);continue;}
  let eff=if o.c_condition.0==NO{guard}else{and(guard,c[o.c_condition.0 as usize])};
  // R and Hmr consume RNG even behind a false guard. Keep every such event.
  if eff!=Some(false)||matches!(o.kind,K::R|K::Hmr){
   let is_zero=|q:u64|q!=NO&&map[q as usize]==NO;
   let trivial=match o.kind{
    K::Z=>is_zero(o.q_target.0),
    K::CX=>is_zero(o.q_control1.0),
    K::CZ=>is_zero(o.q_control1.0)||is_zero(o.q_target.0),
    K::Swap=>is_zero(o.q_control1.0)&&is_zero(o.q_target.0),
    _=>false};
   if trivial{zero_skips+=1;zero_kinds[o.kind as usize]+=1;if matches!(o.kind,K::CCX|K::CCZ){if eff==Some(true){zero_t_always+=1;}else{zero_t_conditional+=1;}}}else{
   for q in [o.q_control2.0,o.q_control1.0,o.q_target.0]{if q!=NO&&map[q as usize]==NO{let p=free.pop_first().expect("out of physical lanes");assert_eq!(owner[p as usize],NO);map[q as usize]=p;owner[p as usize]=q;epochs+=1;}}
   for q in [&mut o.q_control2,&mut o.q_control1,&mut o.q_target]{if q.0!=NO{q.0=map[q.0 as usize];peak=peak.max(q.0+1);}}
   live_peak=live_peak.max(nq-free.len());
   if free.is_empty(){if let Some(last)=full_regions.last_mut(){if last.1+1==i{last.1=i;}else{full_regions.push((i,i));}}else{full_regions.push((i,i));}}
   o.validate();out.push(o);
   if matches!(original.kind,K::R|K::Hmr)&&eff==Some(true){let q=original.q_target.0;if release(q,&mut map,&mut owner,&mut free)&&registered.contains(&q){registered_releases+=1;}}
   if original.c_target.0!=NO{let t=original.c_target.0 as usize;let new=match original.kind{K::BitStore0=>Some(false),K::BitStore1=>Some(true),K::BitInvert=>c[t].map(|x|!x),K::Hmr=>None,_=>c[t]};c[t]=select(c[t],new,eff);}
   }
  }else{dead+=1;}
  if let Some(wires)=z.get(&i){assert!(stack.is_empty(),"zero certificate must be at unconditional scope");for &q in wires{if release(q,&mut map,&mut owner,&mut free){zero_releases+=1;if registered.contains(&q){registered_releases+=1;}}}}
 }
 assert!(stack.is_empty());
 // Output metadata names the initial lanes. Missing roles are exactly zero;
 // allocate clean lanes, then permute the logical output roles back in place.
 for &q in &registered{if map[q as usize]==NO{let p=free.pop_first().expect("no lane for zero output role");map[q as usize]=p;owner[p as usize]=q;peak=peak.max(p+1);output_allocations+=1;}}
 let mut swaps=0;
 for &q in &registered{let p=map[q as usize];if p!=q{let other=owner[q as usize];let mut s=Op::empty();s.kind=K::Swap;s.q_control1=QubitId(p);s.q_target=QubitId(q);s.validate();out.push(s);owner[q as usize]=q;map[q as usize]=q;owner[p as usize]=other;if other!=NO{map[other as usize]=p;}swaps+=1;}}
 assert!(registered.iter().all(|&q|map[q as usize]==q));
 let result=serde_json::json!({"status":"EXACT_DYNAMIC_LANE_COLORING_DIAGNOSTIC_NOT_A_SCORE","original_physical_Q":nq,"recolored_physical_Q":peak,"registered_qubits":registered.len(),"registered_releases":registered_releases,"proved_zero_releases":zero_releases,"provably_zero_identity_gates_removed":zero_skips,"zero_identity_removed_by_kind":zero_kinds,"zero_Toffolis_always_executed":zero_t_always,"zero_Toffolis_conditionally_executed":zero_t_conditional,"scratch_epochs":epochs,"provably_dead_operations_removed":dead,"final_output_swaps":swaps,"final_zero_output_allocations":output_allocations,"arithmetic_live_peak":live_peak,"full_width_regions":full_regions,"input_count":v.len(),"output_count":out.len()});(out,result)
}
fn hash(v:&[Op])->String{use sha3::{Digest,Sha3_256};let mut h=Sha3_256::new();for o in v{for x in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(x.to_le_bytes());}}format!("{:x}",h.finalize())}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),4);let v=io::load_ops(&a[1]);let events=if a[2]=="none"{vec![]}else{let d:serde_json::Value=serde_json::from_str(&std::fs::read_to_string(&a[2]).unwrap()).unwrap();assert_eq!(d["input_count"],v.len());assert_eq!(d["input_sha3_256"],hash(&v));serde_json::from_value(d["zero_events"].clone()).unwrap()};let(out,mut d)=color(&v,&events);d["input_sha3_256"]=serde_json::json!(hash(&v));d["output_sha3_256"]=serde_json::json!(hash(&out));io::save_ops(&format!("{}.ops.bin",a[3]),&out);std::fs::write(format!("{}.json",a[3]),serde_json::to_string_pretty(&d).unwrap()).unwrap();println!("{d}");}
#[cfg(test)]mod tests{
 use super::*;use quantum_ecc::circuit::{RegisterId,BitId};
 fn op(k:K,c:u64,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(c);o.q_target=QubitId(t);o}
 fn reg(q:u64)->Op{let mut o=op(K::AppendToRegister,NO,q);o.r_target=RegisterId(0);o}
 fn simulate(v:&[Op],mut x:u64)->u64{for o in v{let b=|i:u64|x>>i&1!=0;match o.kind{K::X=>x^=1<<o.q_target.0,K::CX=>if b(o.q_control1.0){x^=1<<o.q_target.0},K::Swap=>if b(o.q_control1.0)!=b(o.q_target.0){x^=(1<<o.q_control1.0)|(1<<o.q_target.0)},K::R=>{assert!(!b(o.q_target.0));},K::Register|K::AppendToRegister=>{},_=>panic!("unsupported")}}x}
 #[test]fn zero_register_lanes_can_be_reused_then_outputs_are_restored(){let v=vec![reg(0),reg(1),op(K::X,NO,0),op(K::R,NO,0),op(K::X,NO,3),op(K::X,NO,0),op(K::R,NO,1)];let(w,d)=color(&v,&[]);assert_eq!(d["recolored_physical_Q"],3);assert!(d["final_output_swaps"].as_u64().unwrap()>0);let x=1;let y=simulate(&v,x);let z=simulate(&w,x);assert_eq!(y&3,z&3);assert_eq!((y>>2).count_ones(),(z>>2).count_ones());}
 #[test]fn certified_unitary_zero_ends_a_lifetime_without_adding_reset(){let v=vec![reg(0),op(K::CX,0,1),op(K::CX,0,1),op(K::CX,0,2)];let(w,d)=color(&v,&[(2,1)]);assert_eq!(d["recolored_physical_Q"],2);assert_eq!(w.len(),v.len());for x in 0..2{let y=simulate(&v,x);let z=simulate(&w,x);assert_eq!(y&1,z&1);assert_eq!((y>>1).count_ones(),(z>>1).count_ones());}}
 #[test]fn unknown_reset_never_releases_a_lane(){let mut bit=Op::empty();bit.kind=K::AppendToRegister;bit.c_target=BitId(0);bit.r_target=RegisterId(1);let mut reset=op(K::R,NO,0);reset.c_condition=BitId(0);let(_,d)=color(&[reg(0),bit,reset,op(K::X,NO,1)],&[]);assert_eq!(d["registered_releases"],0);assert_eq!(d["recolored_physical_Q"],2);}
 #[test]fn output_permutation_does_not_need_new_quantum_lane(){let(_,d)=color(&[reg(0),reg(1),op(K::R,NO,0),op(K::X,NO,2)],&[]);assert_eq!(d["recolored_physical_Q"],3);}
 #[test]fn reset_of_zero_is_retained_for_rng_consumption(){let(v,d)=color(&[reg(0),op(K::R,NO,2)],&[]);assert_eq!(d["recolored_physical_Q"],2);assert_eq!(d["provably_zero_identity_gates_removed"],0);assert_eq!(v.len(),2);assert_eq!(v[1].kind,K::R);}
 #[test]fn zero_control_does_not_allocate_or_change_a_target(){let(v,d)=color(&[reg(0),op(K::CX,2,0)],&[]);assert_eq!(d["recolored_physical_Q"],1);assert_eq!(v.len(),1);for x in 0..2{assert_eq!(simulate(&v,x),x);}}
 #[test]fn zero_measurement_still_produces_a_random_classical_bit(){let mut h=op(K::Hmr,NO,2);h.c_target=BitId(0);let(v,_)=color(&[reg(0),h],&[]);assert_eq!(v.iter().filter(|o|o.kind==K::Hmr).count(),1);assert_eq!(v[1].c_target,BitId(0));}
 #[test]fn false_guard_measurements_and_resets_still_consume_rng(){let mut h=op(K::Hmr,NO,2);h.c_target=BitId(1);h.c_condition=BitId(0);let mut r=op(K::R,NO,3);r.c_condition=BitId(0);let(v,_)=color(&[reg(0),h,r],&[]);assert_eq!(v.iter().filter(|o|matches!(o.kind,K::R|K::Hmr)).count(),2);assert_eq!(v[1].c_condition,BitId(0));assert_eq!(v[2].c_condition,BitId(0));}
}
