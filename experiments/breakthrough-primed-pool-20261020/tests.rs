
#[cfg(test)]mod prime_clean_pool_tests{
 use super::*;
 #[test]fn strict_free_set_regression_remains_active_and_clean_growth_is_primed(){
  let run=|prime|{let mut c=Builder::new();let inputs=c.alloc_qubits(2);if prime{c.research_prime_clean_pool(64);}let before=c.y42_alloc_state();let temporary=c.alloc_qubits(40);for q in temporary.into_iter().rev(){c.release_clean(q);}let(q,b,n)=before.clone();c.y42_alloc_set(&before,&q,b.len(),&[],n);assert_eq!(c.active_qubits(),2);assert_eq!(inputs.len(),2);};
  assert!(std::panic::catch_unwind(||run(false)).is_err());run(true);
 }
 fn trace(prime:bool)->(Vec<[u64;7]>,Vec<u64>){
  let mut c=Builder::new();let inputs=c.alloc_qubits(3);let padding=c.alloc_qubits(5);for &j in &[0usize,2,4]{c.release_clean(padding[j]);}if prime{c.research_prime_clean_pool(96);}let mut held=Vec::new();let mut ids=Vec::new();
  for step in 0..512{if held.len()<2||step%3!=0{let q=c.alloc_qubit();ids.push(q.0);c.cx(inputs[0],q);c.ccx(inputs[0],inputs[1],q);if step%7==0{c.x(q);}held.push(q);}else{c.free(held.pop().unwrap());}if held.len()>20{c.free(held.remove(0));}}
  while let Some(q)=held.pop(){c.free(q);}c.declare_qubit_register(&inputs);let fields=c.take_ops().iter().map(|o|[o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]).collect();(fields,ids)
 }
 #[test]fn priming_preserves_every_emitted_operation_and_future_allocation(){let(a,ai)=trace(false);let(b,bi)=trace(true);assert_eq!(ai,bi);assert_eq!(a,b);}
}
