
#[cfg(test)]mod live_core_tests{
 use super::*;use crate::circuit::analyze_ops;use crate::sim::Simulator;use sha3::digest::XofReader;
 thread_local!{static ON:std::cell::Cell<bool>=const{std::cell::Cell::new(false)};static SNAP:std::cell::RefCell<Option<(Vec<Lin>,Vec<Lin>)>>=const{std::cell::RefCell::new(None)};}
 pub(super) fn capture(add:&[Lin],k:&[Lin])->bool{if !ON.with(|x|x.get()){return false;}SNAP.with(|x|*x.borrow_mut()=Some((add.to_vec(),k.to_vec())));true}
 struct Empty;impl XofReader for Empty{fn read(&mut self,_:&mut[u8]){panic!("No measurement/reset is allowed before the active prefix snapshot");}}
 fn parity(s:&Simulator<'_,Empty>,f:&Lin)->u64{f.w.iter().fold(if f.one{u64::MAX}else{0},|x,q|x^s.qubits[q.0 as usize])}
 #[test]fn exact_native_live_forward_prefix_matches_every_independent_fourteen_bit_input(){
  assert!(Y15_CORE_V2&&Y16_CORE);let mut c=Builder::new();let acc=c.alloc_qubits(56);let e=c.alloc_qubits(3);let nm=c.alloc_qubits(3);let k1=c.alloc_qubit();let k2=c.alloc_qubit();let base=c.active_qubits();assert_eq!(base,64);
  let input:Vec<_>=acc[..6].iter().chain(&e).chain(&nm).copied().chain([k1,k2]).collect();assert_eq!(input.len(),14);
  ON.with(|x|x.set(true));let plan=fold_fwd_v2(&mut c,&acc,[e[0],e[1],e[2]],[nm[0],nm[1],nm[2]],k1,k2,0,None,false,0);ON.with(|x|x.set(false));assert!(plan.is_empty());assert_eq!(c.active_qubits(),base+31);
  let(add,k)=SNAP.with(|x|x.borrow_mut().take()).unwrap();assert_eq!(k.len(),8);let fields:Vec<_>=(4..17).chain(std::iter::once(17)).chain(32..39).map(|i|add[i].clone()).collect();assert_eq!(fields.len(),21);
  let all:Vec<_>=(0..base+31).map(|i|QubitId(i as u64)).collect();c.declare_qubit_register(&all);let ops=c.take_ops();let(nq,nb,_,_)=analyze_ops(ops.iter());assert_eq!(nq,95);
  let mut tokens=include_str!("live_core_expected.dat").split_whitespace();assert_eq!(tokens.next(),Some("16384"));assert_eq!(tokens.next(),Some("31"));assert_eq!(tokens.next(),Some("21"));assert_eq!(tokens.next(),Some("8"));
  let mut expected=Vec::new();for _ in 0..60{let name=tokens.next().unwrap();let values:Vec<u64>=(0..256).map(|_|tokens.next().unwrap().parse().unwrap()).collect();expected.push((name,values));}assert!(tokens.next().is_none());
  for batch in 0..256{let mut rng=Empty;let mut s=Simulator::new(nq as usize,nb as usize,&mut rng);for lane in 0..64{let value=batch*64+lane;for(i,&q)in input.iter().enumerate(){if value>>i&1!=0{s.qubits[q.0 as usize]|=1u64<<lane;}}}let original=s.qubits.clone();s.apply_iter(ops.iter());
   for(i,q)in input.iter().enumerate(){assert_eq!(s.qubits[q.0 as usize],original[q.0 as usize],"sourceinput{i}");}
   for i in 0..31{assert_eq!(s.qubits[base as usize+i],expected[i].1[batch],"{} batch{batch}",expected[i].0);}
   for(i,f)in fields.iter().enumerate(){assert_eq!(parity(&s,f),expected[31+i].1[batch],"field{i} batch{batch}");}
   for(i,f)in k.iter().enumerate(){assert_eq!(parity(&s,f),expected[52+i].1[batch],"k{i} batch{batch}");}assert_eq!(s.phase,0);
  }
  eprintln!("LIVE_CORE_NATIVE cases=16384 held=31 fields=21 derived_k=8 all_functions_match=1 no_measurement_prefix=1");
 }
}
