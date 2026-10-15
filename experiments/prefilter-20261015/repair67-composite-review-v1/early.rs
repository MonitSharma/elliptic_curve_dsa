fn fill_packet(packet:&mut LazyPacket,curve:&FastCurveC){while packet.ensure(packet.batches.len(),curve){}assert_eq!(packet.next,NUM_TESTS);}
fn exact_early(p:&Compact,packet:&mut CandidatePacket,regs:&[Vec<QubitOrBit>],nq:usize,nb:usize,curve:&FastCurveC)->(&'static str,usize){
 fill_packet(&mut packet.packet,curve);let mut rng=packet.packet.reader.clone();let mut sim=FastSimulator::new(nq,nb,&mut rng);let mut shots=0;
 for points in &packet.packet.batches{sim.clear_for_shot();for(lane,(t,o,_))in points.iter().enumerate(){for(reg,value)in regs[..4].iter().zip([t.0,t.1,o.0,o.1]){sim.set_register(reg,value,lane);}}sim.apply(p);shots+=points.len();
  for(lane,(_,_,expected))in points.iter().enumerate(){if sim.get_register(&regs[0],lane)!=expected.0||sim.get_register(&regs[1],lane)!=expected.1{return("classical",shots);}}
  let mask=if points.len()==64{u64::MAX}else{(1u64<<points.len())-1};if sim.phase&mask!=0{return("phase",shots);}
  for reg in regs{for wire in reg{if let QubitOrBit::Qubit(q)=wire{sim.qubits[q.0 as usize]=0;}}}if sim.qubits.iter().any(|q|q&mask!=0){return("ancilla",shots);}
 }("pass",shots)
}
fn validate_early(ops:&[Op],p:&Compact,prefix:&Shake256,tail:&[Op],regs:&[Vec<QubitOrBit>],nq:usize,nb:usize,curve:&FastCurveC){
 let mut h=prefix.clone();for op in nonce_tail(tail,1){h.update(&record49(&op));}let mut packet=LazyPacket{reader:h.finalize_xof(),next:0,batches:Vec::new()};fill_packet(&mut packet,curve);
 let mut x=packet.reader.clone();let mut y=x.clone();let mut reference=Simulator::new(nq,nb,&mut x);let mut fast=FastSimulator::new(nq,nb,&mut y);let mut shots=0;
 for points in &packet.batches{reference.clear_for_shot();fast.clear_for_shot();for(lane,(t,o,_))in points.iter().enumerate(){for(reg,value)in regs[..4].iter().zip([t.0,t.1,o.0,o.1]){reference.set_register(reg,value,lane);fast.set_register(reg,value,lane);}}reference.apply_iter(ops[..ops.len()-TAIL].iter());fast.apply(p);assert_eq!(reference.qubits,fast.qubits);assert_eq!(reference.bits,fast.bits);assert_eq!(reference.phase,fast.phase);shots+=points.len();}
 drop(reference);drop(fast);let mut a=[0u8;64];let mut b=[0u8;64];XofReader::read(&mut x,&mut a);XofReader::read(&mut y,&mut b);assert_eq!(a,b);assert_eq!(shots,9024);
 eprintln!("EARLY_FULLSTATE_AND_PHYSICAL_RNG9024_PASS nonce=1");
}
