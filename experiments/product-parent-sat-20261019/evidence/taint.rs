//! Conservative causal value difference. Diagonal phase is deliberately outside
//! this theorem; the filter rejects only certainly wrong computational outputs.
mod io;
use quantum_ecc::circuit::{Op,OperationType as K};
const NO:u64=u64::MAX;
fn and(a:Option<bool>,b:Option<bool>)->Option<bool>{match(a,b){(Some(false),_)|(_,Some(false))=>Some(false),(Some(true),x)|(x,Some(true))=>x,_=>None}}
fn select(a:Option<bool>,b:Option<bool>,g:Option<bool>)->Option<bool>{match g{Some(true)=>b,Some(false)=>a,None=>if a==b{a}else{None}}}
fn propagate(v:&[Op],at:usize,wire:u64)->(Vec<bool>,usize){
 let nq=v.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&q|q!=NO).max().unwrap_or(wire)as usize+1;
 let nb=v.iter().flat_map(|o|[o.c_condition.0,o.c_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;
 let mut c=vec![Some(false);nb];for o in v{if o.kind==K::AppendToRegister&&o.c_target.0!=NO{c[o.c_target.0 as usize]=None;}}
 let mut q=vec![false;nq];let mut stack=vec![];let mut guard=Some(true);let mut high=0;
 for(i,o)in v.iter().enumerate(){
  if i==at&&guard!=Some(false){q[wire as usize]=true;}
  if o.kind==K::PushCondition{stack.push(guard);guard=and(guard,c[o.c_condition.0 as usize]);continue;}
  if o.kind==K::PopCondition{guard=stack.pop().unwrap();continue;}
  if matches!(o.kind,K::Register|K::AppendToRegister){continue;}
  let eff=if o.c_condition.0==NO{guard}else{and(guard,c[o.c_condition.0 as usize])};
  if eff==Some(false){continue;}
  let(t,a,b)=(o.q_target.0 as usize,o.q_control1.0 as usize,o.q_control2.0 as usize);
  match o.kind{
   K::CX=>q[t]|=q[a],K::CCX=>q[t]|=q[a]||q[b],
   K::Swap=>if eff==Some(true){q.swap(a,t);}else{let x=q[a]||q[t];q[a]=x;q[t]=x;},
   K::R|K::Hmr=>if eff==Some(true){q[t]=false;},
   // X changes both values equally. Diagonal phase gates do not change basis
   // values. Hmr produces the same freely coupled outcome in both executions.
   K::X|K::Z|K::CZ|K::CCZ|K::Neg|K::DebugPrint|K::BitInvert|K::BitStore0|K::BitStore1=>{},
   _=>panic!("unsupported value-flow operation {:?}",o.kind)
  }
  if o.c_target.0!=NO{let t=o.c_target.0 as usize;let new=match o.kind{K::BitStore0=>Some(false),K::BitStore1=>Some(true),K::BitInvert=>c[t].map(|x|!x),K::Hmr=>None,_=>c[t]};c[t]=select(c[t],new,eff);}
  if i>=at&&i%1000==0{high=high.max(q.iter().filter(|&&x|x).count());}
 }
 assert!(stack.is_empty());(q,high)
}
fn hash(v:&[Op])->String{use sha3::{Digest,Sha3_256};let mut h=Sha3_256::new();for o in v{for x in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(x.to_le_bytes());}}format!("{:x}",h.finalize())}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),3);let v=io::load_ops(&a[1]);assert_eq!(hash(&v),"429af1c31b54064e17e7602be516b519c066c241e218d56f002287ea02b16842");
 let(q,high)=propagate(&v,17876252,10);let mut outputs:Vec<Vec<Option<u64>>>=vec![];
 for o in &v{if o.kind==K::AppendToRegister{let r=o.r_target.0 as usize;if outputs.len()<=r{outputs.resize(r+1,vec![]);}outputs[r].push((o.q_target.0!=NO).then_some(o.q_target.0));}}
 let mut affected=vec![];for(reg,wires)in outputs.iter().take(2).enumerate(){for(bit,wire)in wires.iter().enumerate(){if wire.is_some_and(|w|q[w as usize]){affected.push(reg*256+bit);}}}
 let data=serde_json::json!({"status":"SOURCE_BOUND_ZERO_ROW_CAUSAL_VALUE_CERTIFICATE","parent_sha3_256":hash(&v),"omitted_row_index":17876252,"omitted_row_target":10,"omitted_row_sha3_256":"167c7dad3201c7b11743b8d6bdd1949fa61952ac7201f71692a3a369be305823","affected_output_bits":affected,"unaffected_output_bits":512-affected.len(),"remaining_tainted_quantum_wires":q.iter().enumerate().filter(|(_,x)|**x).map(|(i,_)|i).collect::<Vec<_>>(),"max_sampled_taint_width":high,"scope":"Only computational output values are certified. No phase equivalence is claimed. All quantum inputs and all measurement outcomes are free. Unknown guards never clear taint. Hmr outcomes couple identically; reset removes value influence only when guaranteed executed."});
 std::fs::write(&a[2],serde_json::to_string_pretty(&data).unwrap()).unwrap();println!("affected output bits={}",affected.len());}
#[cfg(test)]mod tests{use super::*;use quantum_ecc::circuit::{QubitId,BitId,RegisterId};
 fn op(k:K,c:u64,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(c);o.q_target=QubitId(t);o}
 #[test]fn nonlinear_reader_propagates_possible_difference(){let mut x=op(K::CCX,0,2);x.q_control2=QubitId(1);let(q,_)=propagate(&[x],0,0);assert!(q[2]);}
 #[test]fn guaranteed_reset_stops_causal_value_difference(){let v=[op(K::R,NO,0),op(K::CX,0,1)];let(q,_)=propagate(&v,0,0);assert!(!q[0]&&!q[1]);}
 #[test]fn unknown_reset_never_stops_causal_difference(){let mut bit=Op::empty();bit.kind=K::AppendToRegister;bit.c_target=BitId(0);bit.r_target=RegisterId(1);let mut reset=op(K::R,NO,0);reset.c_condition=BitId(0);let(q,_)=propagate(&[bit,reset,op(K::CX,0,1)],1,0);assert!(q[0]&&q[1]);}
 #[test]fn diagonal_phase_does_not_create_output_value_difference(){let(q,_)=propagate(&[op(K::CZ,0,1)],0,0);assert!(q[0]&&!q[1]);}
 #[test]fn measurement_resets_value_with_same_free_classical_outcome(){let mut h=op(K::Hmr,NO,0);h.c_target=BitId(0);let mut x=op(K::X,NO,1);x.c_condition=BitId(0);let(q,_)=propagate(&[h,x],0,0);assert!(!q[0]&&!q[1]);}
}
