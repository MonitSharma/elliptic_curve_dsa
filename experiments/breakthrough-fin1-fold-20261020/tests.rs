
#[cfg(test)]mod fin1_fold_tests{
 use super::*;use crate::circuit::{Op,OperationType,analyze_ops};use crate::sim::Simulator;use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
 struct Words{bytes:Vec<u8>,pos:usize}impl XofReader for Words{fn read(&mut self,b:&mut[u8]){b.copy_from_slice(&self.bytes[self.pos..self.pos+b.len()]);self.pos+=b.len();}}
 fn draws(ops:&[Op])->usize{ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count()}
 fn build(budget:usize,ttm:bool,new:bool)->(Vec<Op>,Vec<QubitId>,crate::circuit::BitId,u32){
  let mut c=Builder::new();let acc=c.alloc_qubits(56);let e=c.alloc_qubits(3);let nm=c.alloc_qubits(3);let k1=c.alloc_qubit();let k2=c.alloc_qubit();let guard=c.alloc_bit();let pad=c.alloc_qubits(1232-budget-(64+30));let interface:Vec<_>=acc.iter().chain(&e).chain(&nm).copied().chain([k1,k2]).collect();let all:Vec<_>=interface.iter().chain(&pad).copied().collect();c.declare_qubit_register(&all);
  std::env::set_var("PEBBLE_HARD_CAP",if new{"1232"}else{"1234"});core_loans_fin1::force(Some(new));c.push_condition(guard);let(_,peak)=super::super::super::pingpong::with_phase_cap(Some(if new{1232}else{1250}),||c.r3_peak(|c|fold_fwd_v2(c,&acc,[e[0],e[1],e[2]],[nm[0],nm[1],nm[2]],k1,k2,1,None,ttm,2)));c.pop_condition();core_loans_fin1::force(None);std::env::set_var("PEBBLE_HARD_CAP","1234");assert!(peak<=if new{1232}else{1250},"budget{budget} ttm{ttm} new{new} peak{peak}");(c.take_ops(),interface,guard,peak)
 }
 fn fixture(budget:usize,ttm:bool,guard_word:u64,probe:Option<usize>){
  let old=build(budget,ttm,false);let new=build(budget,ttm,true);assert_eq!(old.1,new.1);assert_eq!(old.2,new.2);let(nq,nb,_,_)=analyze_ops(old.0.iter().chain(&new.0));let batches:Vec<_>=if probe.is_some(){vec![73]}else{(0..256).collect()};let mut totals=[0u64;2];
  for batch in batches{let mut initialized=vec![0u64;nq as usize];let mut h=Shake256::default();h.update(b"core-loan-full-fold-upper-v1");h.update(&(batch as u64).to_le_bytes());let mut upper=h.finalize_xof();for &q in &old.1[6..56]{let mut b=[0u8;8];upper.read(&mut b);initialized[q.0 as usize]=u64::from_le_bytes(b);}let core:Vec<_>=old.1[..6].iter().chain(&old.1[56..]).copied().collect();for lane in 0..64{let value=batch*64+lane;for(i,&q)in core.iter().enumerate(){if value>>i&1!=0{initialized[q.0 as usize]|=1u64<<lane;}}}
   let mut outputs=Vec::new();for(index,item)in[&old,&new].into_iter().enumerate(){let n=draws(&item.0);let mut bytes=vec![0u8;n*8];let mut h=Shake256::default();h.update(b"core-loan-full-fold-measurements-v1");h.update(&(batch as u64).to_le_bytes());h.finalize_xof().read(&mut bytes);if let Some(p)=probe{for j in 0..n{bytes[j*8..j*8+8].copy_from_slice(&(if j==p||p==n{u64::MAX}else{0u64}).to_le_bytes());}}let mut rng=Words{bytes,pos:0};let mut s=Simulator::new(nq as usize,nb as usize,&mut rng);s.qubits.copy_from_slice(&initialized);s.bits[item.2.0 as usize]=guard_word;s.apply_iter(item.0.iter());assert_eq!(s.phase,0,"budget{budget} ttm{ttm} new{} batch{batch} probe{probe:?}",index==1);for i in 0..nq as usize{if !item.1[..56].iter().any(|q|q.0 as usize==i){assert_eq!(s.qubits[i],initialized[i],"nonoutput wire{i}");}}totals[index]+=s.stats.toffoli_gates;outputs.push(s.qubits.clone());drop(s);assert_eq!(rng.pos,n*8);
   }assert_eq!(outputs[0],outputs[1],"budget{budget} ttm{ttm} batch{batch}");
  }if probe.is_none(){eprintln!("FIN1_COMPLETE_FOLD budget{budget} ttm{ttm} guard{guard_word:016x} shots16384 old_peak{} new_peak{} old_t{} new_t{} diagnostic_delta{}",old.3,new.3,totals[0],totals[1],(totals[1]as f64-totals[0]as f64)/16384.0);}
 }
 #[test]fn complete_forward_fold_with_eleven_helper_loans_all_small_inputs_guards_and_measurements(){
  for budget in 0..=6{for ttm in[false]{for guard in[0,0xA55A_DD33_FF00_1701,u64::MAX]{fixture(budget,ttm,guard,None);}}}
  let max=draws(&build(0,false,false).0).max(draws(&build(0,false,true).0));for p in 0..=max{fixture(0,false,0xA55A_DD33_FF00_1701,Some(p));}
 }
}
