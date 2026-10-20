
#[cfg(test)]mod core_loan_tests{
 use super::*;use crate::circuit::{Op,OperationType,analyze_ops};use crate::sim::Simulator;use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
 thread_local!{static ON:std::cell::Cell<bool>=const{std::cell::Cell::new(false)};static SNAP:std::cell::RefCell<Option<(Vec<Lin>,Vec<Lin>)>>=const{std::cell::RefCell::new(None)};}
 pub(super)fn capture(add:&[Lin],k:&[Lin])->bool{if !ON.with(|x|x.get()){return false;}SNAP.with(|x|*x.borrow_mut()=Some((add.to_vec(),k.to_vec())));true}
 include!("core_loan_certificate.rs");
 struct Words{bytes:Vec<u8>,pos:usize}impl XofReader for Words{fn read(&mut self,b:&mut[u8]){b.copy_from_slice(&self.bytes[self.pos..self.pos+b.len()]);self.pos+=b.len();}}
 fn feature(q:&[QubitId],mask:u64)->Lin{let mut v=Lin::k(mask&1!=0);for i in 1..q.len(){if mask>>i&1!=0{v=v.x(&l(q[i]));}}v}
 fn offset(c:&mut Builder,features:&[QubitId],held:&[QubitId]){for(i,&mask)in CORE_LOAN_OFFSETS.iter().enumerate(){lin_xor_into(c,&feature(features,mask),held[i]);}}
 fn basis(c:&mut Builder,features:&[QubitId],held:&[QubitId],inverse:bool){if inverse{offset(c,features,held);}if inverse{for &(a,b)in CORE_LOAN_BASIS_CX.iter().rev(){c.cx(held[a],held[b]);}}else{for &(a,b)in CORE_LOAN_BASIS_CX{c.cx(held[a],held[b]);}}if !inverse{offset(c,features,held);}}
 fn phase(c:&mut Builder,features:&[QubitId],terms:&[(usize,usize)]){for &(a,b)in terms{match(a,b){(0,0)=>{let q=features[1];c.cz(q,q);c.x(q);c.cz(q,q);c.x(q);},(a,0)|(0,a)=>c.cz(features[a],features[a]),(a,b)=>c.cz(features[a],features[b]),}}}
 fn build(guarded:bool,shuffle:bool)->(Vec<Op>,Vec<QubitId>,Vec<usize>,Vec<QubitId>,crate::circuit::BitId,u32){
  let mut c=Builder::new();let acc=c.alloc_qubits(56);let e=c.alloc_qubits(3);let nm=c.alloc_qubits(3);let k1=c.alloc_qubit();let k2=c.alloc_qubit();let guard=c.alloc_bit();let input:Vec<_>=acc[..6].iter().chain(&e).chain(&nm).copied().chain([k1,k2]).collect();
  if guarded{c.push_condition(guard);}ON.with(|x|x.set(true));fold_fwd_v2(&mut c,&acc,[e[0],e[1],e[2]],[nm[0],nm[1],nm[2]],k1,k2,0,None,false,0);ON.with(|x|x.set(false));let(_,k)=SNAP.with(|x|x.borrow_mut().take()).unwrap();let held:Vec<_>=(64..95).map(QubitId).collect();assert_eq!(c.active_qubits(),95);
  let mut marks=vec![c.op_count()];let a4=k[0].clone();let a5=k[0].x(&k[1]);
  c.cx(held[10],acc[5]);lin_xor_into(&mut c,&a5,acc[5]);c.cx(held[3],acc[4]);lin_xor_into(&mut c,&a4,acc[4]);c.cx(held[2],acc[3]);c.cx(held[1],acc[2]);c.cx(e[2],acc[2]);c.cx(held[0],acc[1]);c.cx(e[1],acc[1]);c.cx(e[0],acc[0]);
  let features:Vec<_>=std::iter::once(k1).chain(input[6..].iter().copied()).chain(acc[..6].iter().copied()).chain(held.iter().copied()).collect();assert_eq!(features.len(),46);
  basis(&mut c,&features,&held,false);
  for &(index,terms)in CORE_LOAN_ERASE{let q=held[index];let bit=c.alloc_bit();c.hmr(q,bit);c.release_clean(q);c.push_condition(bit);phase(&mut c,&features,terms);c.pop_condition();c.free_bit(bit);}
  assert_eq!(c.active_qubits(),84);marks.push(c.op_count());let(_,peak)=c.r3_peak(|c|{if shuffle{let scratch=c.alloc_qubits(11);for q in scratch.into_iter().rev(){c.release_clean(q);}}});if !shuffle{assert_eq!(peak,84);}
  for &(index,linear,products)in CORE_LOAN_REBUILD{let q=held[index];assert!(c.n2_take(q));for &(a,b)in products{lin_and_into(&mut c,q,&feature(&features,a),&feature(&features,b));}lin_xor_into(&mut c,&feature(&features,linear),q);}
  assert_eq!(c.active_qubits(),95);basis(&mut c,&features,&held,true);
  c.cx(e[0],acc[0]);c.cx(e[1],acc[1]);c.cx(held[0],acc[1]);c.cx(e[2],acc[2]);c.cx(held[1],acc[2]);c.cx(held[2],acc[3]);lin_xor_into(&mut c,&a4,acc[4]);c.cx(held[3],acc[4]);lin_xor_into(&mut c,&a5,acc[5]);c.cx(held[10],acc[5]);marks.push(c.op_count());
  if guarded{c.pop_condition();}c.declare_qubit_register(&input);(c.take_ops(),input,marks,held,guard,peak)
 }
 fn run(guarded:bool,shuffle:bool,guard_word:u64,probe:Option<usize>){
  let(ops,input,marks,held,guard,_)=build(guarded,shuffle);let(nq,nb,_,_)=analyze_ops(ops.iter());let nd=ops.iter().filter(|o|matches!(o.kind,OperationType::Hmr|OperationType::R)).count();assert_eq!(nd,11);let batches:Vec<_>=if probe.is_some(){vec![73]}else{(0..256).collect()};
  for batch in batches{let mut h=Shake256::default();h.update(b"core-loan-native-measurements-v1");h.update(&(batch as u64).to_le_bytes());let mut bytes=vec![0u8;nd*8];h.finalize_xof().read(&mut bytes);if let Some(p)=probe{for i in 0..nd{bytes[i*8..i*8+8].copy_from_slice(&(if i==p||p==nd{u64::MAX}else{0u64}).to_le_bytes());}}
   let mut rng=Words{bytes,pos:0};let mut sim=Simulator::new(nq as usize,nb as usize,&mut rng);for lane in 0..64{let x=batch*64+lane;for(i,&q)in input.iter().enumerate(){if x>>i&1!=0{sim.qubits[q.0 as usize]|=1u64<<lane;}}}sim.bits[guard.0 as usize]=guard_word;sim.apply_iter(ops[..marks[0]].iter());let prefix=sim.qubits.clone();let before=sim.stats.toffoli_gates;assert_eq!(sim.phase,0);sim.apply_iter(ops[marks[0]..marks[1]].iter());assert_eq!(sim.phase,0,"erase batch{batch}");assert_eq!(sim.stats.toffoli_gates,before);for &q in &held[20..]{assert_eq!(sim.qubits[q.0 as usize],0);}
   sim.apply_iter(ops[marks[1]..].iter());assert_eq!(sim.phase,0,"roundtrip batch{batch}");assert_eq!(sim.qubits,prefix,"roundtrip data batch{batch}");assert_eq!(sim.stats.toffoli_gates-before,32*(if guarded{guard_word.count_ones()}else{64}));drop(sim);assert_eq!(rng.pos,nd*8);
  }
 }
 #[test]fn all_fourteen_bit_inputs_exact_linear_basis_erasure_reconstruction_and_phase(){for guarded in[false,true]{for shuffle in[false,true]{run(guarded,shuffle,0xA55A_DD33_FF00_1701,None);}}}
 #[test]fn all_measurement_coefficients_false_and_mixed_guards(){for g in[0,0xA55A_DD33_FF00_1701,u64::MAX]{for p in 0..=11{run(true,true,g,Some(p));}}}
}
