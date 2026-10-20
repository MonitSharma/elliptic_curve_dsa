
#[cfg(test)]mod budget_c3_tests{
 use super::*;use crate::circuit::{analyze_ops,Op,OperationType};use crate::sim::Simulator;use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
 thread_local!{static FORCE:std::cell::Cell<Option<bool>>=const{std::cell::Cell::new(None)};}
 pub(super) fn override_value()->Option<bool>{FORCE.with(|x|x.get())}
 struct Words{data:Vec<u8>,pos:usize}impl XofReader for Words{fn read(&mut self,b:&mut[u8]){let end=self.pos+b.len();assert!(end<=self.data.len());b.copy_from_slice(&self.data[self.pos..end]);self.pos=end;}}
 fn draws(ops:&[Op])->usize{ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count()}
 fn build(fin:usize,ttm:bool,budget:usize,loan:bool)->(Vec<Op>,Vec<QubitId>){
  let mut c=Builder::new();let acc=c.alloc_qubits(56);let e=c.alloc_qubits(3);let nm=c.alloc_qubits(3);let k1=c.alloc_qubit();let k2=c.alloc_qubit();
  let will_free=fin.min(2)+usize::from(fin>=3||ttm);let pad_count=1234-budget-(64+31-will_free);let pad=c.alloc_qubits(pad_count);let interface:Vec<_>=acc.iter().chain(&e).chain(&nm).copied().chain([k1,k2]).collect();
  let all:Vec<_>=interface.iter().chain(&pad).copied().collect();c.declare_qubit_register(&all);FORCE.with(|x|x.set(Some(loan)));let((),peak)=c.r3_peak(|c|{fold_fwd_v2(c,&acc,[e[0],e[1],e[2]],[nm[0],nm[1],nm[2]],k1,k2,fin,None,ttm,2);});FORCE.with(|x|x.set(None));
  assert!(peak<=1234,"fin={fin} ttm={ttm} budget={budget} loan={loan} peak={peak}");(c.take_ops(),interface)
 }
 #[test]fn low_budget_c3_loan_matches_full_forward_fold_for_every_small_source_input(){
  std::env::set_var("PEBBLE_HARD_CAP","1234");
  for fin in 0..=3{for ttm in[false,true]{for budget in[6usize,7]{
   let(old,interface)=build(fin,ttm,budget,false);let(new,other)=build(fin,ttm,budget,true);assert_eq!(interface,other);let(nq,nb,_,_)=analyze_ops(old.iter().chain(&new));let mut totals=[0u64;2];
   for batch in 0..256usize{
    let mut initialized=vec![0u64;nq as usize];let mut h=Shake256::default();h.update(b"budget-c3-full-forward-upper-v1");h.update(&(batch as u64).to_le_bytes());let mut input=h.finalize_xof();
    for i in 6..56{let mut b=[0u8;8];input.read(&mut b);initialized[interface[i].0 as usize]=u64::from_le_bytes(b);}
    let core:Vec<_>=interface[..6].iter().chain(&interface[56..]).copied().collect();assert_eq!(core.len(),14);
    for lane in 0..64{let value=batch*64+lane;for(i,&q)in core.iter().enumerate(){if value>>i&1!=0{initialized[q.0 as usize]|=1u64<<lane;}}}
    let mut outputs=Vec::new();
    for(index,ops)in[&old,&new].into_iter().enumerate(){let nr=draws(ops);let mut data=vec![0u8;nr*8];let mut hash=Shake256::default();hash.update(b"budget-c3-full-forward-measurements-v1");hash.update(&(batch as u64).to_le_bytes());hash.finalize_xof().read(&mut data);let mut rng=Words{data,pos:0};let mut s=Simulator::new(nq as usize,nb as usize,&mut rng);s.qubits.copy_from_slice(&initialized);s.apply_iter(ops.iter());
     assert_eq!(s.phase,0,"fin={fin} ttm={ttm} budget={budget} loan={} batch={batch}",index==1);for i in 0..nq as usize{if !interface[..56].iter().any(|q|q.0 as usize==i){assert_eq!(s.qubits[i],initialized[i]);}}
     totals[index]+=s.stats.toffoli_gates as u64;outputs.push(s.qubits.clone());drop(s);assert_eq!(rng.pos,nr*8);
    }assert_eq!(outputs[0],outputs[1],"fin={fin} ttm={ttm} budget={budget} batch={batch}");
   }eprintln!("C3_FULL_FOLD_COMPONENT fin={fin} ttm={ttm} budget={budget} shots=16384 old_t={} loan_t={} diagnostic_delta={}",totals[0],totals[1],(totals[1]as f64-totals[0]as f64)/16384.0);
  }}}
 }
}
