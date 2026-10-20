#[cfg(test)]
mod exact_witness_ripple_tests {
 use super::*;
 use alloy_primitives::U512;
 use crate::{circuit::analyze_ops,sim::Simulator};
 use sha3::digest::{Update,ExtendableOutput};
 fn init(){super::super::clear_process_env();std::env::set_var("PEBBLE_HARD_CAP","1664");super::super::install_skywalk_submission_recipe();std::env::set_var("EXACT_WITNESS_TEST_FAULT","0");}
 fn exercise(n:usize,case:usize,new:bool,fault:bool)->bool{
  init();if fault{std::env::set_var("EXACT_WITNESS_TEST_FAULT","1");}
  let mut c=Builder::new();let reg=c.alloc_qubits(n);let w=c.alloc_qubits(3);let guard=c.alloc_bit();c.push_condition(guard);
  if new{witness_product(&mut c,&reg,&w);}else{for(sft,negative)in[(0usize,false),(4,false),(6,true),(10,false),(32,false)]{let ops:Vec<_>=(sft..n).map(|j|if j-sft<3{Some(w[j-sft])}else{None}).collect();if negative{line(&mut c,&reg[sft..],&ops,None);}else{sub_line(&mut c,&reg[sft..],&ops);}}}
  c.pop_condition();c.declare_qubit_register(&reg);c.declare_qubit_register(&w);let ops=c.take_ops();let(nq,nb,_,_)=analyze_ops(ops.iter());let mut seed=sha3::Shake256::default();seed.update(b"exact-fullwidth-witness-native-20261020-v1");seed.update(&(case as u64).to_le_bytes());let mut rng=seed.finalize_xof();let mut sim=Simulator::new(nq as usize,nb as usize,&mut rng);let mask=(U512::from(1)<<n)-U512::from(1);let guard_mask=if case%3==0{u64::MAX}else if case%3==1{0xaaaa_aaaa_aaaa_aaaa}else{0x5aa5_33cc_ff00_0ff0};sim.bits[guard.0 as usize]=guard_mask;let mut initial=vec![];let mut random=0x9e37_79b9_7f4a_7c15u64^(case as u64);
  for lane in 0..64{let value=if case==0{U512::ZERO}else if case==1{mask}else if case==2{U512::from(1)<<((lane*7)%n)}else{let mut v=U512::ZERO;for j in 0..5{random^=random<<13;random^=random>>7;random^=random<<17;v|=U512::from(random)<<(64*j);}v&mask};let witness=(lane%8)as u64;initial.push((value,witness));for(i,q)in reg.iter().enumerate(){sim.qubits[q.0 as usize]|=(value.bit(i)as u64)<<lane;}for(i,q)in w.iter().enumerate(){sim.qubits[q.0 as usize]|=((witness>>i)&1)<<lane;}}
  sim.apply_iter(ops.iter());let mut okay=sim.phase==0;
  for(lane,(value,witness))in initial.into_iter().enumerate(){let expected=if(guard_mask>>lane)&1!=0{value.wrapping_sub(U512::from(witness)*((U512::from(1)<<32usize)+U512::from(977)))&mask}else{value};for(i,q)in reg.iter().enumerate(){okay&=((sim.qubits[q.0 as usize]>>lane)&1)==expected.bit(i)as u64;}for(i,q)in w.iter().enumerate(){okay&=((sim.qubits[q.0 as usize]>>lane)&1)==((witness>>i)&1);}}
  for(q,&value)in sim.qubits.iter().enumerate(){if !reg.iter().chain(w.iter()).any(|id|id.0 as usize==q){okay&=value==0;}}okay
 }
 #[test]fn polynomial_all8_witnesses_matches_full_modular_translation(){for n in[35,59,64,129,259]{for case in 0..4{assert!(exercise(n,case,true,false),"n{n}case{case}");}}}
 #[test]fn full259_original_and_consolidated_are_phase_clean_under_captured_guards(){for case in 0..16{assert!(exercise(259,case,false,false));assert!(exercise(259,case,true,false));}}
 #[test]fn deliberate_low_product_fault_is_detected(){assert!(!exercise(259,3,true,true));}
}
