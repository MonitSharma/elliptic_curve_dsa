#[cfg(test)]
mod lazy_single_tests {
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
}
