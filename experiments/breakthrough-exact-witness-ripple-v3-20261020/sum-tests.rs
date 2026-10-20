#[cfg(test)]
mod exact_shared_sum_tests {
 use super::*;
 use crate::{circuit::analyze_ops,sim::Simulator};
 use alloy_primitives::U256;
 use sha3::digest::{Update,ExtendableOutput};
 #[test]fn copied_sum_and_free_erase_preserve_live_operands_phase_and_clean_helpers(){
  for m in[1usize,2,3,8,32,64,128]{
   super::super::clear_process_env();std::env::set_var("PEBBLE_HARD_CAP","1664");super::super::install_skywalk_submission_recipe();let mut c=Builder::new();let a=c.alloc_qubits(m);let b=c.alloc_qubits(m);let held=c.alloc_qubits(m);let carry=c.alloc_qubit();let probe=c.alloc_qubits(m+1);let guard=c.alloc_bit();c.push_condition(guard);c.cx_pairs(&b,&held);let mut sum=held.clone();sum.push(carry);add_wide(&mut c,&a,&sum);c.cx_pairs(&sum,&probe);let av:Vec<_>=(0..sum.len()).map(|j|a.get(j).copied()).collect();let bv:Vec<_>=(0..sum.len()).map(|j|b.get(j).copied()).collect();super::super::sqc::erase_sum(&mut c,&sum,&av,&bv);c.pop_condition();c.declare_qubit_register(&a);c.declare_qubit_register(&b);c.declare_qubit_register(&probe);let ops=c.take_ops();let(nq,nb,_,_)=analyze_ops(ops.iter());let mut h=sha3::Shake256::default();h.update(b"exact-sharedsum-native-20261020-v1");let mut rng=h.finalize_xof();let mut sim=Simulator::new(nq as usize,nb as usize,&mut rng);let mut random=0x9e37_79b9_7f4a_7c15u64;
   let mask=(U256::from(1)<<m)-U256::from(1);let mut pairs=vec![];let g=0xff00_f0f0_aaaa_ffffu64;sim.bits[guard.0 as usize]=g;
   for lane in 0..64{let mut values=[U256::ZERO;2];for(k,reg)in[&a,&b].into_iter().enumerate(){let v=if m<=3{U256::from(((lane>>(k*m))&((1<<m)-1))as u64)}else{random^=random<<13;random^=random>>7;random^=random<<17;let lo=random;random^=random<<13;random^=random>>7;random^=random<<17;(U256::from(lo)|(U256::from(random)<<64))&mask};values[k]=v;for(i,q)in reg.iter().enumerate(){sim.qubits[q.0 as usize]|=(v.bit(i)as u64)<<lane;}}pairs.push(values);}
   sim.apply_iter(ops.iter());assert_eq!(sim.phase,0,"m{m}");for(lane,pair)in pairs.into_iter().enumerate(){for(k,reg)in[&a,&b].into_iter().enumerate(){for(i,q)in reg.iter().enumerate(){assert_eq!((sim.qubits[q.0 as usize]>>lane)&1,pair[k].bit(i)as u64);}}let expected=if(g>>lane)&1!=0{pair[0]+pair[1]}else{U256::ZERO};for(i,q)in probe.iter().enumerate(){assert_eq!((sim.qubits[q.0 as usize]>>lane)&1,expected.bit(i)as u64);}}
   for q in held.iter().chain([&carry]){assert_eq!(sim.qubits[q.0 as usize],0);}for(q,&v)in sim.qubits.iter().enumerate(){if!a.iter().chain(b.iter()).chain(probe.iter()).any(|id|id.0 as usize==q){assert_eq!(v,0);}}
  }
 }
}
