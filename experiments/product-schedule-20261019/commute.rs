//! Cancel inverse Toffolis only across gates proved to commute with them.
mod io;
use quantum_ecc::circuit::{Op,OperationType as K};
use std::collections::{HashMap,HashSet};
const NO:u64=u64::MAX;
#[derive(Clone,Copy,Hash,PartialEq,Eq,Debug)]struct Key(u8,u64,u64,u64);
fn key(o:&Op)->Option<Key>{if o.c_condition.0!=NO{return None;}match o.kind{K::CCX=>Some(Key(0,o.q_control1.0.min(o.q_control2.0),o.q_control1.0.max(o.q_control2.0),o.q_target.0)),K::CCZ=>{let mut q=[o.q_control1.0,o.q_control2.0,o.q_target.0];q.sort();Some(Key(1,q[0],q[1],q[2]))},_=>None}}
fn events(o:&Op)->(Vec<u64>,Vec<u64>){
 let(a,b,t)=(o.q_control1.0,o.q_control2.0,o.q_target.0);
 match o.kind{
 K::X=>(vec![t],vec![]),K::CX=>(vec![t],vec![a]),K::CCX=>(vec![t],vec![a,b]),
 K::Z=>(vec![],vec![t]),K::CZ=>(vec![],vec![a,t]),K::CCZ=>(vec![],vec![a,b,t]),
 K::R|K::Hmr=>(vec![t],vec![t]),K::Swap=>(vec![a,t],vec![a,t]),
 K::Register|K::AppendToRegister|K::Neg|K::PushCondition|K::PopCondition|K::BitStore0|K::BitStore1|K::BitInvert=>(vec![],vec![]),
 // Unknown diagnostics are barriers rather than guessed unitary gates.
 _=>(vec![NO],vec![NO])
 }
}
fn find(v:&[Op])->Vec<(usize,usize)>{
 let nq=v.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;
 let mut writes:Vec<HashSet<usize>>=vec![HashSet::new();nq];let mut reads=writes.clone();
 let mut active:HashMap<Key,usize>=HashMap::new();let mut inverse:HashMap<usize,Key>=HashMap::new();let mut depth=0;let mut pairs=vec![];
 fn remove(id:usize,active:&mut HashMap<Key,usize>,inverse:&mut HashMap<usize,Key>,writes:&mut[HashSet<usize>],reads:&mut[HashSet<usize>]){
  if let Some(k)=inverse.remove(&id){active.remove(&k);writes[k.1 as usize].remove(&id);writes[k.2 as usize].remove(&id);if k.0==0{reads[k.3 as usize].remove(&id);}else{writes[k.3 as usize].remove(&id);}}
 }
 for(i,o)in v.iter().enumerate(){
  if depth==0{if let Some(k)=key(o){if let Some(&first)=active.get(&k){pairs.push((first,i));remove(first,&mut active,&mut inverse,&mut writes,&mut reads);continue;}}}
  let(w,r)=events(o);let mut bad=HashSet::new();
  if w.contains(&NO)||r.contains(&NO){bad.extend(inverse.keys().copied());}else{for q in w{bad.extend(writes[q as usize].iter().copied());}for q in r{bad.extend(reads[q as usize].iter().copied());}}
  for id in bad{remove(id,&mut active,&mut inverse,&mut writes,&mut reads);}
  if depth==0{if let Some(k)=key(o){assert!(active.insert(k,i).is_none());inverse.insert(i,k);writes[k.1 as usize].insert(i);writes[k.2 as usize].insert(i);if k.0==0{reads[k.3 as usize].insert(i);}else{writes[k.3 as usize].insert(i);}}}
  match o.kind{K::PushCondition=>depth+=1,K::PopCondition=>depth-=1,_=>{}}
 }
 assert_eq!(depth,0);pairs
}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),3);let v=io::load_ops(&a[1]);let pairs=find(&v);let delete:HashSet<_>=pairs.iter().flat_map(|&(a,b)|[a,b]).collect();let out:Vec<_>=v.iter().enumerate().filter(|(i,_)|!delete.contains(i)).map(|(_,o)|*o).collect();io::save_ops(&format!("{}.ops.bin",a[2]),&out);
 use sha3::{Digest,Sha3_256};let hash=|v:&[Op]|{let mut h=Sha3_256::new();for o in v{for x in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(x.to_le_bytes());}}format!("{:x}",h.finalize())};
 let result=serde_json::json!({"status":"EXACT_COMMUTING_INVERSE_CANCELLATION_DIAGNOSTIC_NOT_A_SCORE","input":a[1],"input_count":v.len(),"input_sha3_256":hash(&v),"output_count":out.len(),"output_sha3_256":hash(&out),"unconditional_Toffolis_removed":delete.len(),"pairs":pairs});std::fs::write(format!("{}.json",a[2]),serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("removed_Toffolis={} pairs={}",delete.len(),pairs.len());}
#[cfg(test)]mod tests{
 use super::*;use quantum_ecc::circuit::{QubitId,BitId};
 fn gate(k:K,a:u64,b:u64,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(a);o.q_control2=QubitId(b);o.q_target=QubitId(t);o}
 fn ccx()->Op{gate(K::CCX,0,1,2)}
 fn sim(v:&[Op],mut x:u64)->(u64,bool){let mut p=false;for o in v{let q=|n:u64|x>>n&1!=0;match o.kind{K::X=>x^=1<<o.q_target.0,K::CX=>if q(o.q_control1.0){x^=1<<o.q_target.0},K::CCX=>if q(o.q_control1.0)&&q(o.q_control2.0){x^=1<<o.q_target.0},K::Z=>p^=q(o.q_target.0),K::CZ=>p^=q(o.q_control1.0)&&q(o.q_target.0),K::CCZ=>p^=q(o.q_control1.0)&&q(o.q_control2.0)&&q(o.q_target.0),_=>panic!("unsupported")}}(x,p)}
 #[test]fn commuting_common_target_and_control_phases_cancel(){let v=vec![ccx(),gate(K::CX,3,NO,2),gate(K::CZ,0,NO,1),ccx()];assert_eq!(find(&v),vec![(0,3)]);for x in 0..16{assert_eq!(sim(&v,x),sim(&v[1..3],x));}}
 #[test]fn changed_controls_reject(){assert!(find(&[ccx(),gate(K::X,NO,NO,0),ccx()]).is_empty());}
 #[test]fn target_phase_reject(){assert!(find(&[ccx(),gate(K::Z,NO,NO,2),ccx()]).is_empty());}
 #[test]fn target_as_other_gate_control_rejects(){assert!(find(&[ccx(),gate(K::CX,2,NO,3),ccx()]).is_empty());}
 #[test]fn target_measurement_rejects(){let mut h=gate(K::Hmr,NO,NO,2);h.c_target=BitId(0);assert!(find(&[ccx(),h,ccx()]).is_empty());}
 #[test]fn classically_conditioned_endpoint_is_excluded(){let mut o=ccx();o.c_condition=BitId(0);assert!(find(&[ccx(),o]).is_empty());}
 #[test]fn diagonal_toffoli_controls_are_fully_symmetric(){let a=gate(K::CCZ,0,1,2);let b=gate(K::CCZ,2,0,1);let v=vec![a,gate(K::Z,NO,NO,1),b];assert_eq!(find(&v),vec![(0,2)]);for x in 0..8{assert_eq!(sim(&v,x),sim(&v[1..2],x));}}
}
