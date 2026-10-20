// Exact zero facts from full-prefix semantic replay release clean helper wires.
// Registered quantum inputs stay pinned. No operation is deleted or reordered.
fn semantic_color(ops:&[Op])->(Vec<Op>,serde_json::Value,Vec<Option<u64>>){
 let no=u64::MAX;let(nq,nb,_,_)=quantum_ecc::circuit::analyze_ops(ops.iter());
 let(nq,nb)=(nq as usize,nb as usize);let mut alg=Algebra{inner:Expr::default()};
 let(mut q,mut c)=initial_inputs(ops,nq,nb,&mut alg);
 let pinned:HashSet<_>=ops.iter().filter(|o|o.kind==K::AppendToRegister&&o.q_target.0!=no).map(|o|o.q_target.0).collect();
 let mut free:BTreeSet<u64>=(0..nq as u64).filter(|x|!pinned.contains(x)).collect();
 let mut map:Vec<Option<u64>>=(0..nq as u64).map(|q|pinned.contains(&q).then_some(q)).collect();
 let(mut current,mut peak,mut peak_at,mut max_id)=(pinned.len(),pinned.len(),0,pinned.iter().copied().max().unwrap_or(0));
 let(mut releases,mut lifetimes)=(0usize,0usize);let mut base=1;let mut stack=vec![];let mut out=Vec::with_capacity(ops.len());
 for(i,o)in ops.iter().enumerate(){
  if o.kind==K::PushCondition{out.push(*o);stack.push(base);base=alg.and(&base,&c[o.c_condition.0 as usize]);continue;}
  if o.kind==K::PopCondition{out.push(*o);base=stack.pop().expect("balanced source");continue;}
  let eff=if o.c_condition.0==no{base}else{alg.and(&base,&c[o.c_condition.0 as usize])};
  let mut used:Vec<_>=[o.q_control2.0,o.q_control1.0,o.q_target.0].into_iter().filter(|&x|x!=no).collect();used.sort_unstable();used.dedup();
  for &logical in &used{if map[logical as usize].is_none(){assert_eq!(q[logical as usize],0,"only provenzero helper may be unmapped");let physical=free.pop_first().expect("original width bounds injective active map");map[logical as usize]=Some(physical);current+=1;lifetimes+=1;max_id=max_id.max(physical);}}
  if current>peak{peak=current;peak_at=i;}
  let get=|logical:u64|if logical==no{no}else{map[logical as usize].unwrap()};let mut renamed=*o;
  renamed.q_control2=QubitId(get(o.q_control2.0));renamed.q_control1=QubitId(get(o.q_control1.0));renamed.q_target=QubitId(get(o.q_target.0));renamed.validate();out.push(renamed);
  let(t,a,b,ct)=(o.q_target.0 as usize,o.q_control1.0 as usize,o.q_control2.0 as usize,o.c_target.0 as usize);
  match o.kind{
   K::X=>q[t]=alg.xor(&q[t],&eff),
   K::CX=>{let v=alg.and(&q[a],&eff);q[t]=alg.xor(&q[t],&v);},
   K::CCX=>{let v=alg.and(&q[a],&q[b]);let v=alg.and(&v,&eff);q[t]=alg.xor(&q[t],&v);},
   K::Swap=>{let v=alg.xor(&q[a],&q[t]);let v=alg.and(&v,&eff);q[a]=alg.xor(&q[a],&v);q[t]=alg.xor(&q[t],&v);},
   K::R|K::Hmr=>{q[t]=alg.select(&q[t],&0,&eff);if o.kind==K::Hmr{let fresh=alg.fresh();c[ct]=alg.select(&c[ct],&fresh,&eff);}},
   K::BitInvert=>c[ct]=alg.xor(&c[ct],&eff),
   K::BitStore0=>c[ct]=alg.select(&c[ct],&0,&eff),
   K::BitStore1=>c[ct]=alg.select(&c[ct],&1,&eff),
   K::Neg|K::Z|K::CZ|K::CCZ|K::Register|K::AppendToRegister|K::DebugPrint=>{},_=>unreachable!()
  }
  for logical in used{if !pinned.contains(&logical)&&q[logical as usize]==0{let physical=map[logical as usize].take().unwrap();assert!(free.insert(physical));current-=1;releases+=1;}}
  if i%1000000==0{eprintln!("SEMANTIC_COLOR_PROGRESS op={i} peak={peak} current={current} semantic_nodes={}",alg.inner.nodes.len());}
 }
 assert!(stack.is_empty());let actual=quantum_ecc::circuit::analyze_ops(out.iter()).0;assert_eq!(actual,max_id+1);
 let stats=serde_json::json!({"status":"EXACT_SEMANTIC_ZERO_LIFETIME_COMPONENT_NOT_SCORED","original_qubits":nq,"emitted_qubits":actual,"peak_active_slots":peak,"peak_at_operation":peak_at,"knownzero_releases":releases,"helper_lifetimes":lifetimes,"remaining_active_slots":current,"semantic_nodes":alg.inner.nodes.len(),"input_records_sha3":hash(ops),"output_records_sha3":hash(&out),"operation_count_unchanged":out.len()==ops.len(),"scope":"Every freed helper is exactly zero for all registered input/measurement values. Active map injective, registered inputs pinned, reused physical slot clean. Every gate/classical guard/RNG event preserved in original order. Component only; full source/development/finalgate/nonce/benchmark required before scored record."});
 (out,stats,map)
}

#[cfg(test)]mod semantic_color_tests{
 use super::*;use quantum_ecc::circuit::RegisterId;use quantum_ecc::sim::Simulator;use sha3::digest::XofReader;
 struct Words(u8);impl XofReader for Words{fn read(&mut self,b:&mut[u8]){b.fill(self.0);}}
 fn metadata()->Vec<Op>{let mut v=vec![];for q in 0..4{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.q_target=QubitId(q);v.push(o);}for c in 0..2{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(1);o.c_target=BitId(c);v.push(o);}v}
 fn check(ops:&[Op])->serde_json::Value{let(out,stats,map)=semantic_color(ops);assert_eq!(ops.len(),out.len());for pattern in[0,255,0xa5,0x5a]{let(mut ra,mut rb)=(Words(pattern),Words(pattern));let(mut a,mut b)=(Simulator::new(6,3,&mut ra),Simulator::new(6,3,&mut rb));for lane in 0..64{for q in 0..4{a.qubits[q]|=((lane>>q&1)as u64)<<lane;}for bit in 0..2{a.bits[bit]|=((lane>>(bit+4)&1)as u64)<<lane;}}b.qubits.clone_from(&a.qubits);b.bits.clone_from(&a.bits);a.apply_iter(ops.iter());b.apply_iter(out.iter());let mut assigned=HashSet::new();for(logical,physical)in map.iter().enumerate(){if let Some(physical)=physical{assert!(assigned.insert(*physical));assert_eq!(a.qubits[logical],b.qubits[*physical as usize],"logical{logical}");}else{assert_eq!(a.qubits[logical],0);}}for physical in 0..6{if !assigned.contains(&(physical as u64)){assert_eq!(b.qubits[physical],0);}}assert_eq!(a.bits,b.bits);assert_eq!(a.phase,b.phase);assert_eq!(a.stats.toffoli_gates,b.stats.toffoli_gates);}stats}
 #[test]fn exact_uncompute_frees_helper_before_reset(){let n=u64::MAX;let mut ops=metadata();ops.extend([make(K::CX,n,0,4,n,n),make(K::CX,n,0,4,n,n),make(K::CX,n,1,5,n,n),make(K::CCZ,0,1,5,n,0)]);let s=check(&ops);assert_eq!(s["original_qubits"],6);assert_eq!(s["emitted_qubits"],5);}
 #[test]fn conditional_semantic_reset_and_classical_mutation_keep_absolute_phase(){let n=u64::MAX;let mut ops=metadata();ops.extend([make(K::X,n,n,4,n,0),make(K::Hmr,n,n,4,2,0),make(K::BitInvert,n,n,n,0,n),make(K::PushCondition,n,n,n,n,1),make(K::CX,n,0,5,n,0),make(K::CCZ,0,1,5,n,n),make(K::Hmr,n,n,5,2,0),make(K::PopCondition,n,n,n,n,n)]);let s=check(&ops);assert_eq!(s["emitted_qubits"],5);}
 #[test]fn live_dirty_helper_is_never_loaned_to_another_logical_wire(){let n=u64::MAX;let mut ops=metadata();ops.extend([make(K::CX,n,0,4,n,n),make(K::CX,n,1,5,n,n),make(K::CCZ,4,5,2,n,n)]);let s=check(&ops);assert_eq!(s["emitted_qubits"],6);}
 #[test]fn randomized_complete_protected_phase_values_classical_rng_and_executed_counts(){let n=u64::MAX;let mut seed=0xa8d7135f23649b01u64;for _ in 0..16{let mut ops=metadata();for step in 0..100{seed=seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);let t=(seed>>8)%6;let a=(t+1+(seed>>16)%5)%6;let b=(0..6).find(|&x|x!=a&&x!=t).unwrap();let cc=if seed&8!=0{n}else{(seed>>24)%3};ops.push(match seed%7{0=>make(K::X,n,n,t,n,cc),1=>make(K::CX,n,a,t,n,cc),2=>make(K::CCX,b,a,t,n,cc),3=>make(K::CCZ,b,a,t,n,cc),4=>make(K::Swap,n,a,t,n,cc),5=>make(K::R,n,n,t,n,cc),_=>make(K::BitInvert,n,n,n,(seed>>32)%3,cc)});if step%17==0{ops.push(make(K::Hmr,n,n,5,2,cc));}}check(&ops);}}
}
