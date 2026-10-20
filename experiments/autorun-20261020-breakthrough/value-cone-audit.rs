mod io;
use quantum_ecc::circuit::{Op,OperationType as K,analyze_ops};
use std::collections::BTreeSet;
const NONE:u32=u32::MAX;
struct Cone{keep:Vec<bool>,live_rng:usize,versions:usize,scopes:usize,outputs:Vec<usize>}
fn mark_guard(mut scope:u32,cond:u32,nodes:&[(u32,u32)],seen:&mut[bool],live:&mut[bool]){if cond!=NONE{live[cond as usize]=true;}while scope!=0&&!seen[scope as usize]{seen[scope as usize]=true;let(parent,version)=nodes[scope as usize];live[version as usize]=true;scope=parent;}}
fn cone(ops:&[Op],outputs:Vec<usize>)->Cone{
 let(nq,nb,_,_)=analyze_ops(ops.iter());let no=u64::MAX;let mut current:Vec<_>=(0..nb).collect();let mut versions=nb as usize;let mut nodes=vec![(0,NONE)];let mut scope=0u32;let mut scopes=Vec::with_capacity(ops.len());let mut conds=Vec::with_capacity(ops.len());let mut previous=Vec::with_capacity(ops.len());let mut written=Vec::with_capacity(ops.len());
 for o in ops{scopes.push(scope);conds.push(if o.c_condition.0==no{NONE}else{current[o.c_condition.0 as usize]});let mut old=NONE;let mut new=NONE;
  match o.kind{K::PushCondition=>{nodes.push((scope,current[o.c_condition.0 as usize]));scope=(nodes.len()-1)as u32;},K::PopCondition=>{assert_ne!(scope,0);scope=nodes[scope as usize].0;},K::BitInvert|K::BitStore0|K::BitStore1|K::Hmr=>{let t=o.c_target.0 as usize;old=current[t];new=versions.try_into().unwrap();versions+=1;current[t]=new;},_=>{}}previous.push(old);written.push(new);
 }assert_eq!(scope,0);let mut qlive=vec![false;nq as usize];for &q in &outputs{qlive[q]=true;}let mut clive=vec![false;versions];let mut seen=vec![false;nodes.len()];let mut keep=vec![false;ops.len()];let mut live_rng=0;
 for(i,o)in ops.iter().enumerate().rev(){let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let b=o.q_control2.0 as usize;let unconditional=scopes[i]==0&&conds[i]==NONE;let mut relevant=false;
  match o.kind{
   K::X|K::CX|K::CCX=>{if qlive[t]{relevant=true;if matches!(o.kind,K::CX|K::CCX){qlive[a]=true;}if o.kind==K::CCX{qlive[b]=true;}}},
   K::Swap=>{if qlive[a]||qlive[t]{relevant=true;qlive[a]=true;qlive[t]=true;}},
   K::R|K::Hmr=>{if qlive[t]{relevant=true;if unconditional{qlive[t]=false;}}if o.kind==K::Hmr&&clive[written[i]as usize]{relevant=true;live_rng+=1;if !unconditional{clive[previous[i]as usize]=true;}}},
   K::BitInvert|K::BitStore0|K::BitStore1=>{if clive[written[i]as usize]{relevant=true;if o.kind==K::BitInvert||!unconditional{clive[previous[i]as usize]=true;}}},
   K::Neg|K::Z|K::CZ|K::CCZ|K::Register|K::AppendToRegister|K::PushCondition|K::PopCondition|K::DebugPrint=>{},
  }
  if relevant{keep[i]=true;mark_guard(scopes[i],conds[i],&nodes,&mut seen,&mut clive);}
 }
 Cone{keep,live_rng,versions,scopes:nodes.len()-1,outputs}
}
fn slice(ops:&[Op],c:&Cone)->Vec<Op>{ops.iter().zip(&c.keep).filter(|(o,k)|**k||matches!(o.kind,K::R|K::Hmr|K::PushCondition|K::PopCondition|K::Register|K::AppendToRegister)).map(|(o,_)|*o).collect()}
fn main(){let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),3);let ops=io::load_ops(&args[1]);let outputs:Vec<_>=ops.iter().filter(|o|o.kind==K::AppendToRegister&&o.q_target.0!=u64::MAX).map(|o|o.q_target.0 as usize).collect::<BTreeSet<_>>().into_iter().collect();assert_eq!(outputs.len(),512);let c=cone(&ops,outputs);let retained=ops.iter().zip(&c.keep).filter(|(_,v)|**v).count();let toffoli=ops.iter().filter(|o|matches!(o.kind,K::CCX|K::CCZ)).count();let kept_t=ops.iter().zip(&c.keep).filter(|(o,v)|**v&&matches!(o.kind,K::CCX|K::CCZ)).count();let result=serde_json::json!({"status":"READONLY_CONSERVATIVE_OUTPUT_VALUE_CONE_NOT_A_CANDIDATE_OR_NONCE_SCREEN","input_operations":ops.len(),"registered_quantum_outputs":c.outputs.len(),"retained_value_operations":retained,"native_toffoli_operations":toffoli,"retained_value_toffoli_operations":kept_t,"live_random_measurement_outputs":c.live_rng,"classical_ssa_versions":c.versions,"captured_guard_scopes":c.scopes,"scope":"Classical SSA and captured condition-stack versions; conditional stores/resets preserve prior dependencies. Phase gates excluded only for output-value dependency analysis. No rewritten stream, correctness-gate result, nonce rejection or resource score. A later value-only filter could reject only exact wrong point outputs and must never accept a nonce as fully passing."});std::fs::write(&args[2],serde_json::to_string_pretty(&result).unwrap()+"\n").unwrap();println!("{result}");}
#[cfg(test)]mod tests{
 use super::*;use quantum_ecc::circuit::{QubitId,BitId};use quantum_ecc::sim::Simulator;use sha3::digest::XofReader;
 struct Fixed(u8);impl XofReader for Fixed{fn read(&mut self,b:&mut[u8]){b.fill(self.0);}}
 fn op(k:K,a:u64,b:u64,t:u64,ct:u64,cc:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control2=QubitId(a);o.q_control1=QubitId(b);o.q_target=QubitId(t);o.c_target=BitId(ct);o.c_condition=BitId(cc);o.validate();o}
 fn equal(original:&[Op],changed:&[Op],a_pattern:u8,b_pattern:u8)->bool{let(nq,nb,_,_)=analyze_ops(original.iter().chain(changed));let mut ra=Fixed(a_pattern);let mut rb=Fixed(b_pattern);let mut a=Simulator::new(nq as usize,nb as usize,&mut ra);let mut b=Simulator::new(nq as usize,nb as usize,&mut rb);for lane in 0..64{for q in 0..3{a.qubits[q]|=((lane>>q&1)as u64)<<lane;}for bit in 0..nb as usize{a.bits[bit]|=((lane>>((bit%3)+3)&1)as u64)<<lane;}}b.qubits.clone_from(&a.qubits);b.bits.clone_from(&a.bits);a.apply_iter(original.iter());b.apply_iter(changed.iter());(0..3).all(|q|a.qubits[q]==b.qubits[q])}
 #[test]fn captured_guards_mutations_live_measurements_and_dead_rng_positions(){let n=u64::MAX;let ops=vec![op(K::Hmr,n,n,4,2,n),op(K::PushCondition,n,n,n,n,0),op(K::BitInvert,n,n,n,0,n),op(K::CX,n,0,2,n,n),op(K::PopCondition,n,n,n,n,n),op(K::CCX,0,1,3,n,n),op(K::Hmr,n,n,3,1,n),op(K::X,n,n,2,n,1)];let c=cone(&ops,vec![0,1,2]);assert_eq!(c.live_rng,1);let s=slice(&ops,&c);for p in[0,255,0xa5,0x5a]{assert!(equal(&ops,&s,p,p));}}
 #[test]fn phase_only_rng_outputs_are_dead_and_values_allow_independent_draw_patterns(){let n=u64::MAX;let ops=vec![op(K::CCX,0,1,3,n,n),op(K::Hmr,n,n,3,1,n),op(K::CZ,n,0,1,n,1),op(K::CX,n,1,2,n,n)];let c=cone(&ops,vec![0,1,2]);assert_eq!(c.live_rng,0);assert!(!c.keep[0]);let s=slice(&ops,&c);for a in[0,255,0xa5,0x5a]{for b in[0,255,0xa5,0x5a]{assert!(equal(&ops,&s,a,b));}}}
 #[test]fn conditional_stores_resets_and_swaps_keep_prior_versions(){let n=u64::MAX;let ops=vec![op(K::BitStore0,n,n,n,0,1),op(K::PushCondition,n,n,n,n,0),op(K::Swap,n,0,2,n,n),op(K::R,n,n,2,n,1),op(K::PopCondition,n,n,n,n,n),op(K::BitStore1,n,n,n,2,n),op(K::X,n,n,1,n,2)];let c=cone(&ops,vec![0,1,2]);let s=slice(&ops,&c);for p in[0,255,0xa5,0x5a]{assert!(equal(&ops,&s,p,p));}}
 #[test]fn omitting_guard_definition_is_detected(){let n=u64::MAX;let ops=vec![op(K::BitInvert,n,n,n,0,n),op(K::X,n,n,2,n,0),op(K::R,n,n,3,n,n)];let c=cone(&ops,vec![0,1,2]);assert!(c.keep[0]);let faulty:Vec<_>=slice(&ops,&c).into_iter().filter(|o|o.kind!=K::BitInvert).collect();assert!(!equal(&ops,&faulty,0,0));}
}
