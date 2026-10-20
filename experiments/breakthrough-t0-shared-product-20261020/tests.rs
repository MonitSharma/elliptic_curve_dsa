
#[cfg(test)]mod t0_shared_product_tests{
 use super::*;use crate::circuit::{Op,OperationType,analyze_ops};use crate::sim::Simulator;use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
 struct Words{bytes:Vec<u8>,pos:usize}impl XofReader for Words{fn read(&mut self,b:&mut[u8]){b.copy_from_slice(&self.bytes[self.pos..self.pos+b.len()]);self.pos+=b.len();}}
 fn draws(ops:&[Op])->usize{ops.iter().filter(|o|matches!(o.kind,OperationType::Hmr|OperationType::R)).count()}
 fn build(n:usize,shared:bool)->(Vec<Op>,Vec<QubitId>,Vec<crate::circuit::BitId>,crate::circuit::BitId,u32){
  let mut c=Builder::new();let x=c.alloc_qubits(n);let e=c.alloc_qubits(3);let nm=c.alloc_qubits(3);let k1=c.alloc_qubit();let k2=c.alloc_qubit();let bits=c.alloc_bits(n);let guard=c.alloc_bit();let input:Vec<_>=x.iter().chain(&e).chain(&nm).copied().chain([k1,k2]).collect();c.declare_qubit_register(&input);c.push_condition(guard);
  let(_,peak)=c.r3_peak(|c|{let mut ph=T0Phase::owned(c,k1,k2,n,bits.clone());let xf:Vec<_>=x.iter().copied().map(l).collect();let ef=[l(e[0]),l(e[1]),l(e[2])];let(w,mut recs)=fold_fwd_forms_borrowed(c,&xf,&ef,[nm[0],nm[1],nm[2]],k1,k2,if shared{ph.t}else{None});for(i,f)in w.iter().enumerate(){ph.z(c,i,f);}pop_chain(c,&mut recs);ph.finish(c);});c.pop_condition();assert_eq!(c.active_qubits(),input.len()as u32);(c.take_ops(),input,bits,guard,peak)
 }
 fn fixture(n:usize,guard:u64,flag:Option<usize>,probe:Option<usize>){
  let old=build(n,false);let new=build(n,true);assert_eq!(old.1,new.1);assert_eq!(old.2,new.2);assert_eq!(old.3,new.3);assert_eq!(old.4,new.4+1);let(nq,nb,_,_)=analyze_ops(old.0.iter().chain(&new.0));let batches:Vec<_>=if probe.is_some(){vec![73]}else{(0..256).collect()};
  for batch in batches{let mut init=vec![0u64;nq as usize];let mut h=Shake256::default();h.update(b"t0-shared-product-upper-v1");h.update(&(batch as u64).to_le_bytes());let mut reader=h.finalize_xof();for &q in &old.1[6..n]{let mut b=[0u8;8];reader.read(&mut b);init[q.0 as usize]=u64::from_le_bytes(b);}let core:Vec<_>=old.1[..6].iter().chain(&old.1[n..]).copied().collect();assert_eq!(core.len(),14);for lane in 0..64{let v=batch*64+lane;for(i,&q)in core.iter().enumerate(){if v>>i&1!=0{init[q.0 as usize]|=1u64<<lane;}}}let flag_words:Vec<u64>=(0..n).map(|i|if let Some(j)=flag{if i==j{u64::MAX}else{0}}else{let mut b=[0u8;8];reader.read(&mut b);u64::from_le_bytes(b)}).collect();let mut phases=Vec::new();let mut counts=Vec::new();
   for item in [&old,&new]{let nd=draws(&item.0);let mut bytes=vec![0u8;nd*8];let mut h=Shake256::default();h.update(b"t0-shared-product-measurements-v1");h.update(&(batch as u64).to_le_bytes());h.finalize_xof().read(&mut bytes);if let Some(p)=probe{for i in 0..nd{bytes[i*8..i*8+8].copy_from_slice(&(if i==p||p==nd{u64::MAX}else{0u64}).to_le_bytes());}}let mut rng=Words{bytes,pos:0};let mut s=Simulator::new(nq as usize,nb as usize,&mut rng);s.qubits.copy_from_slice(&init);s.bits[item.3.0 as usize]=guard;for(i,&bit)in item.2.iter().enumerate(){s.bits[bit.0 as usize]=flag_words[i];}s.apply_iter(item.0.iter());assert_eq!(s.qubits,init,"data n{n} batch{batch}");phases.push(s.phase);counts.push(s.stats.toffoli_gates);drop(s);assert_eq!(rng.pos,nd*8);
   }assert_eq!(phases[0],phases[1],"phase n{n} batch{batch} flag{flag:?} probe{probe:?}");assert_eq!(counts[0],counts[1]+u64::from(guard.count_ones()));
  }
 }
 #[test]fn shared_immutable_letter_product_preserves_forms_oracle_and_saves_one_qubit_and_and(){
  std::env::set_var("PEBBLE_HARD_CAP","1234");for n in[8,56]{for guard in[0,0xA55A_DD33_FF00_1701,u64::MAX]{fixture(n,guard,None,None);}let max=draws(&build(n,false).0).max(draws(&build(n,true).0));for p in 0..=max{fixture(n,0xA55A_DD33_FF00_1701,Some(5),Some(p));}for flag in 0..n{fixture(n,u64::MAX,Some(flag),Some(0));}}
 }
}
