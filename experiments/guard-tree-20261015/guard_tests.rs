#[cfg(test)]
mod guard_tree_tests {
 use super::*;
 use quantum_ecc::circuit::{analyze_ops,NO_BIT};
 use quantum_ecc::sim::Simulator;
 struct Words(u64);
 impl sha3::digest::XofReader for Words{fn read(&mut self,out:&mut[u8]){assert_eq!(out.len(),8);out.copy_from_slice(&self.0.to_le_bytes());}}
 fn program(nested:bool)->Vec<Op>{
  let mut p=vec![];let mut r=Op::empty();r.kind=K::Register;r.r_target=RegisterId(0);p.push(r);
  for q in [0,1,3]{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.q_target=QubitId(q);p.push(o);}
  for b in 0..2{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.c_target=BitId(b);p.push(o);}
  let list=[L{kind:K_CCX,c2:1,c1:0,t:2,ct:NQ,cc:NQ,rt:NQ},
    op(K_CX,2,3,0),op(K_CX,2,3,1),
    L{kind:K_HMR,c2:NQ,c1:NQ,t:2,ct:2,cc:NQ,rt:NQ},op(K_CZ,0,1,2)];
  p.extend(list.iter().map(from_l));
  if nested {let base=6;p.insert(base+1,from_l(&op(K_CX,0,1,NQ)));let h=p.iter().position(|o|o.kind==K::Hmr).unwrap();p.insert(h,from_l(&op(K_CX,0,1,NQ)));}
  p
 }
 fn check(p:&[Op],q:&[Op])->bool{
  let(nq,nb,_,_)=analyze_ops(p.iter());let(rq,rb,_,_)=analyze_ops(q.iter());assert_eq!(nq,rq);assert!(rb>nb);
  let mut equal=true;let mut saving=0;
  for random in [0,u64::MAX]{
   let mut ra=Words(random);let mut rbng=Words(random);let mut a=Simulator::new(nq as usize,nb as usize,&mut ra);let mut b=Simulator::new(rq as usize,rb as usize,&mut rbng);
   for bit in 0..5{let v=(0..64).fold(0u64,|v,l|v|((((l>>bit)&1)as u64)<<l));match bit{0|1=>{a.qubits[bit]=v;b.qubits[bit]=v;},2=>{a.qubits[3]=v;b.qubits[3]=v;},_=>{a.bits[bit-3]=v;b.bits[bit-3]=v;}}}
   if p.iter().any(|o|o.kind==K::AppendToRegister&&o.q_target==QubitId(2)){let v=(0..64).fold(0u64,|v,l|v|((((l>>5)&1)as u64)<<l));a.qubits[2]=v;b.qubits[2]=v;}
   for v in &mut b.bits[nb as usize..]{*v=0xa5a5a5a5a5a5a5a5;}
   a.phase=0x55aa55aa55aa55aa;b.phase=a.phase;
   a.apply_iter(p.iter());b.apply_iter(q.iter());
   equal&=a.qubits==b.qubits&&a.bits==b.bits[..nb as usize]&&a.phase==b.phase&&b.bits[nb as usize..].iter().all(|v|*v==0);
   saving+=a.stats.toffoli_gates as i64-b.stats.toffoli_gates as i64;
  }
  assert!(saving>0);equal
 }
 #[test]fn lazy_single_all_inputs_and_measurements(){let p=program(false);let q=lazy_single(p.clone());assert!(check(&p,&q));}
 #[test]fn lazy_single_nested_affine_hosts(){let p=program(true);let q=lazy_single(p.clone());assert!(check(&p,&q));}
 #[test]fn lazy_single_missing_twin_guard_is_detected(){let p=program(false);let mut q=lazy_single(p.clone());let j=q.iter().position(|o|o.kind==K::CZ&&o.c_condition!=NO_BIT).unwrap();assert_eq!(q[j-1].kind,K::PushCondition);assert_eq!(q[j+1].kind,K::PopCondition);q.remove(j+1);q.remove(j-1);assert!(!check(&p,&q));}
 struct Sequence{words:Vec<u64>,at:usize}
 impl sha3::digest::XofReader for Sequence{fn read(&mut self,out:&mut[u8]){assert_eq!(out.len(),8);out.copy_from_slice(&self.words[self.at].to_le_bytes());self.at+=1;}}
 fn exhaustive(p:&[Op],q:&[Op]){
  let(nq,nb,_,_)=analyze_ops(p.iter());let(rq,rb,_,_)=analyze_ops(q.iter());assert_eq!(nq,rq);assert!(rb>nb);
  let count=p.iter().filter(|o|matches!(o.kind,K::Hmr|K::R)).count();assert_eq!(count,q.iter().filter(|o|matches!(o.kind,K::Hmr|K::R)).count());assert!(count<=4);
  let mut saved=0;
  for assignment in 0..1usize<<count{for dirty in [0,u64::MAX,0xa5a5a5a5a5a5a5a5]{
   let words:Vec<_>=(0..count).map(|i|if assignment>>i&1==0{0}else{u64::MAX}).collect();let mut ra=Sequence{words:words.clone(),at:0};let mut rr=Sequence{words,at:0};
   let mut a=Simulator::new(nq as usize,nb as usize,&mut ra);let mut b=Simulator::new(rq as usize,rb as usize,&mut rr);
   for bit in 0..5{let v=(0..64).fold(0u64,|v,l|v|((((l>>bit)&1)as u64)<<l));match bit{0|1=>{a.qubits[bit]=v;b.qubits[bit]=v;},2=>{a.qubits[3]=v;b.qubits[3]=v;},_=>{a.bits[bit-3]=v;b.bits[bit-3]=v;}}}
   if p.iter().any(|o|o.kind==K::AppendToRegister&&o.q_target==QubitId(2)){let v=(0..64).fold(0u64,|v,l|v|((((l>>5)&1)as u64)<<l));a.qubits[2]=v;b.qubits[2]=v;}
   for x in &mut b.bits[nb as usize..]{*x=dirty;}a.phase=0x55aa55aa55aa55aa;b.phase=a.phase;
   a.apply_iter(p.iter());b.apply_iter(q.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.bits,&b.bits[..nb as usize]);assert_eq!(a.phase,b.phase);assert!(b.bits[nb as usize..].iter().all(|x|*x==0));saved+=a.stats.toffoli_gates as i64-b.stats.toffoli_gates as i64;
   drop(a);drop(b);assert_eq!(ra.at,rr.at);assert_eq!(ra.at,count);
  }}assert!(saved>0);
 }
 #[test]fn guard_tree_derived_outcome_and_extra_data_phase_uses(){
  let mut p=program(false);let j=p.iter().position(|o|o.kind==K::Hmr).unwrap()+1;
  let extra=[L{kind:K_BS1,c2:NQ,c1:NQ,t:NQ,ct:3,cc:NQ,rt:NQ},L{kind:K_BINV,c2:NQ,c1:NQ,t:NQ,ct:3,cc:2,rt:NQ},op(K_CX,0,3,3),op(K_Z,NQ,3,2)];p.splice(j..j,extra.iter().map(from_l));
  let l:Vec<_>=p.iter().map(to_l).collect();let a=analyze(&l);assert!(a.contribs.iter().any(|c|c.end_kind==E_HMR&&a.bderived[c.end_bit as usize]));let q=lazy_single(p.clone());exhaustive(&p,&q);
 }
 #[test]fn guard_tree_alias_survives_original_control_measurement(){
  let mut p=program(false);let prod=p.iter().position(|o|o.kind==K::CCX).unwrap();p.insert(prod,from_l(&op(K_CX,0,4,NQ)));
  let prod=p.iter().position(|o|o.kind==K::CCX).unwrap();p.insert(prod+1,from_l(&L{kind:K_HMR,c2:NQ,c1:NQ,t:0,ct:3,cc:NQ,rt:NQ}));
  let fix=p.iter_mut().find(|o|o.kind==K::CZ).unwrap();fix.q_control1=QubitId(4);
  let q=lazy_single(p.clone());exhaustive(&p,&q);
 }
 #[test]fn guard_tree_dirty_quantum_target_all_inputs_and_measurements(){
  let mut p=program(false);let mut app=Op::empty();app.kind=K::AppendToRegister;app.r_target=RegisterId(0);app.q_target=QubitId(2);p.insert(4,app);
  let l:Vec<_>=p.iter().map(to_l).collect();let a=analyze(&l);assert!(a.contribs.iter().any(|c|c.end_kind==E_HMR&&!c.end_sole));let q=lazy_single(p.clone());exhaustive(&p,&q);
 }
 #[test]fn guard_tree_conditional_producer_captured_before_mutation(){
  let mut p=program(false);let prod=p.iter().position(|o|o.kind==K::CCX).unwrap();p[prod].c_condition=BitId(0);
  for o in p.iter_mut().filter(|o|o.kind==K::CX&&o.q_control1==QubitId(2)){o.c_condition=BitId(1);}
  p.splice(prod..prod,[L{kind:K_BS0,c2:NQ,c1:NQ,t:NQ,ct:3,cc:NQ,rt:NQ},L{kind:K_BINV,c2:NQ,c1:NQ,t:NQ,ct:3,cc:0,rt:NQ}].iter().map(from_l));
  let prod=p.iter().position(|o|o.kind==K::CCX).unwrap();p.insert(prod+1,from_l(&L{kind:K_BINV,c2:NQ,c1:NQ,t:NQ,ct:0,cc:NQ,rt:NQ}));
  let fix=p.iter().position(|o|o.kind==K::CZ).unwrap();p.insert(fix,from_l(&L{kind:K_PUSH,c2:NQ,c1:NQ,t:NQ,ct:NQ,cc:3,rt:NQ}));p.push(from_l(&L{kind:K_POP,c2:NQ,c1:NQ,t:NQ,ct:NQ,cc:NQ,rt:NQ}));
  let q=lazy_single(p.clone());exhaustive(&p,&q);
 }
}
