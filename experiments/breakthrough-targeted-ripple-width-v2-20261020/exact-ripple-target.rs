//! Bounded, exact measured-prefix/reversible-tail use for plain vented ripples.
use super::Builder;use crate::circuit::QubitId;
pub(super) fn try_run(c:&mut Builder,a:&[QubitId],b:&[QubitId],cin:Option<QubitId>,cout:Option<QubitId>)->bool{
 let Some(cap)=std::env::var("EXACT_RIPPLE_TARGET").ok().and_then(|v|v.parse::<usize>().ok())else{return false;};
 if a.len()!=b.len()||b.len()<3{return false;}
 let mut used=std::collections::BTreeSet::new();if !a.iter().chain(b).copied().chain(cin).chain(cout).all(|q|used.insert(q.0)){return false;}
 let owned=b.len()-1-usize::from(cout.is_none());let missing=(c.active_qubits()as usize+owned).saturating_sub(cap);if missing==0||missing>=owned{return false;}
 let active=c.active_qubits();let before=c.op_count();super::bridge::raw_add(c,a,b,cin,cout,missing);assert_eq!(c.active_qubits(),active);
 // Original plain ripple has one HMR and one release-R per owned carry.
 // Each omitted carry therefore needs two zero-HMR draws for alignment.
 let zero=c.alloc_qubit();for _ in 0..2*missing{let bit=c.alloc_bit();c.hmr(zero,bit);c.free_bit(bit);}c.release_clean(zero);
 assert_eq!(c.active_qubits(),active);eprintln!("EXACT_RIPPLE_TARGET\t{}\t{before}\t{}\t{active}\t{}\t{cap}\t{missing}",c.current_phase(),c.op_count(),b.len());true
}

#[cfg(test)]mod exact_ripple_target_tests{
 use super::*;use crate::circuit::{Op,OperationType as K,analyze_ops};use crate::sim::Simulator;use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
 struct Words{bytes:Vec<u8>,pos:usize}impl XofReader for Words{fn read(&mut self,out:&mut[u8]){out.copy_from_slice(&self.bytes[self.pos..self.pos+out.len()]);self.pos+=out.len();}}
 fn draws(ops:&[Op])->usize{ops.iter().filter(|o|matches!(o.kind,K::R|K::Hmr)).count()}
 fn build(n:usize,cin_on:bool,cout_on:bool,cut:usize,new:bool)->(Vec<Op>,Vec<QubitId>,crate::circuit::BitId,u32){
  let mut c=Builder::new();let a=c.alloc_qubits(n);let b=c.alloc_qubits(n);let ci=c.alloc_qubit();let out=c.alloc_qubit();let all:Vec<_>=a.iter().chain(&b).copied().chain([ci,out]).collect();c.declare_qubit_register(&all);let guard=c.alloc_bit();let base=c.active_qubits();let owned=n-1-usize::from(!cout_on);
  std::env::set_var("PEBBLE_HARD_CAP","1536");std::env::remove_var("EXACT_RIPPLE_TARGET");c.push_condition(guard);
  let(_,peak)=c.r3_peak(|c|{if new{std::env::set_var("EXACT_RIPPLE_TARGET",(base as usize+owned-cut).to_string());assert!(try_run(c,&a,&b,cin_on.then_some(ci),cout_on.then_some(out)));}else{super::super::modular::ripple_add(c,&a,&b,cin_on.then_some(ci),cout_on.then_some(out));}});c.pop_condition();std::env::remove_var("EXACT_RIPPLE_TARGET");assert_eq!(peak,base+(owned-if new{cut}else{0})as u32);(c.take_ops(),all,guard,peak)
 }
 fn fixture(n:usize,cin_on:bool,cout_on:bool,cut:usize,guard:u64,probe:Option<usize>,fault:bool){
  let old=build(n,cin_on,cout_on,cut,false);let new=build(n,cin_on,cout_on,cut,true);assert_eq!(old.1,new.1);assert_eq!(old.2,new.2);assert_eq!(draws(&old.0),2*(n-1-usize::from(!cout_on)));assert_eq!(draws(&new.0),draws(&old.0));assert_eq!(old.3-new.3,cut as u32);let(nq,nb,_,_)=analyze_ops(old.0.iter().chain(&new.0));
  let batches=if probe.is_some(){1}else if n<=6{(1usize<<(2*n+2)).div_ceil(64)}else{32};
  for batch in 0..batches{let mut initial=vec![0u64;nq as usize];let mut h=Shake256::default();h.update(b"exact-ripple-target-input-v1");h.update(&(n as u64).to_le_bytes());h.update(&(batch as u64).to_le_bytes());let mut rd=h.finalize_xof();for &q in &old.1{let mut word=[0u8;8];rd.read(&mut word);initial[q.0 as usize]=u64::from_le_bytes(word);}
   if n<=6{for lane in 0..64{let value=batch*64+lane;for(i,&q)in old.1.iter().enumerate(){initial[q.0 as usize]&=!(1u64<<lane);initial[q.0 as usize]|=((value>>i&1)as u64)<<lane;}}}
   let mut expected=initial.clone();for lane in 0..64{if guard>>lane&1==0{continue;}let mut carry=u64::from(cin_on)&(initial[old.1[2*n].0 as usize]>>lane&1);for i in 0..n{let a=initial[old.1[i].0 as usize]>>lane&1;let b=initial[old.1[n+i].0 as usize]>>lane&1;let sum=a^b^carry;carry=(a&b)^(a&carry)^(b&carry);expected[old.1[n+i].0 as usize]&=!(1u64<<lane);expected[old.1[n+i].0 as usize]|=sum<<lane;}if cout_on{expected[old.1[2*n+1].0 as usize]^=carry<<lane;}}
   let mut costs=[0u64;2];for(index,item)in [&old,&new].iter().enumerate(){let count=draws(&item.0);let mut bytes=vec![0u8;8*count];let mut h=Shake256::default();h.update(b"exact-ripple-target-measurements-v1");h.update(&(batch as u64).to_le_bytes());h.finalize_xof().read(&mut bytes);if let Some(p)=probe{for j in 0..count{bytes[j*8..j*8+8].copy_from_slice(&(if p==j||p==count{u64::MAX}else{0u64}).to_le_bytes());}}
    let mut rng=Words{bytes,pos:0};let mut s=Simulator::new(nq as usize,nb as usize,&mut rng);s.qubits.clone_from(&initial);s.bits[item.2.0 as usize]=guard;
    let ops:Vec<_>=item.0.iter().filter(|o|!(fault&&index==1&&o.kind==K::CZ&&o.c_condition.0!=u64::MAX)).copied().collect();s.apply_iter(ops.iter());assert_eq!(s.qubits,expected,"complete value/source/carry/helper contract");assert_eq!(s.phase,0,"exact ripple phase contract n{n} cin{cin_on} cut{cut} batch{batch}");assert_eq!(s.bits[item.2.0 as usize],guard);costs[index]=s.stats.toffoli_gates as u64;drop(s);assert_eq!(rng.pos,count*8,"exact ripple RNG contract");
   }assert_eq!(costs[1]-costs[0],cut as u64*guard.count_ones()as u64,"one extra executed Toffoli per omitted helper");
  }
 }
 #[test]fn exhaustive_values_phase_width_and_exact_extra_toffoli_cost(){for n in 3..=6{for co in [false,true]{let owned=n-1-usize::from(!co);for cut in 1..owned{for ci in [false,true]{for guard in [0,u64::MAX,0xA5C39F012DE4876B]{fixture(n,ci,co,cut,guard,None,false);}}}}}}
 #[test]fn wide_inputs_all_cuts_and_source_carry_restoration(){for n in [7,22,56,128,256]{for co in [false,true]{let owned=n-1-usize::from(!co);for cut in 1..owned{for ci in [false,true]{fixture(n,ci,co,cut,0x9C36A50FE1D2784B,None,false);}}}}}
 #[test]fn every_measurement_and_reset_outcome(){for co in [false,true]{let owned=5-usize::from(!co);for cut in 1..owned{for ci in [false,true]{for probe in 0..12{fixture(6,ci,co,cut,u64::MAX,Some(probe),false);}}}}}
 #[test]#[should_panic(expected="exact ripple phase contract")]fn omitted_phase_repair_is_detected(){fixture(5,true,true,2,u64::MAX,None,true);}
 #[test]fn unsupported_aliases_and_budgets_emit_no_ops(){let mut c=Builder::new();let a=c.alloc_qubits(4);let b=c.alloc_qubits(4);let out=c.alloc_qubit();std::env::set_var("PEBBLE_HARD_CAP","1536");std::env::set_var("EXACT_RIPPLE_TARGET","10");let before=c.op_count();assert!(!try_run(&mut c,&a,&b,Some(a[0]),Some(out)));assert_eq!(c.op_count(),before);std::env::set_var("EXACT_RIPPLE_TARGET","1");assert!(!try_run(&mut c,&a,&b,None,Some(out)));assert_eq!(c.op_count(),before);std::env::remove_var("EXACT_RIPPLE_TARGET");}
}
