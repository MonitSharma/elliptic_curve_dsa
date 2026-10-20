//! Exact phase comparator with adaptive measured-prefix / reversible-tail carries.
//! MAJ(a,b,c): CX(a,b), CX(a,c), CCX(c,b,a); inverse restores all operands.
//! Each omitted measured carry costs one extra native Toffoli. No precision cut.
use super::Builder;
use crate::circuit::QubitId;
pub(super) fn enabled()->bool{std::env::var("EXACT_CMP_COMPACT").is_ok_and(|v|v=="1")}
pub(super) fn max_saving(n:usize)->usize{if n<3{0}else{n-2}}
pub(super) fn try_run(c:&mut Builder,u:&[QubitId],v:&[QubitId],p:Option<QubitId>)->bool{
 if !enabled()||u.len()<3{return false;}
 let cap=super::phase_fit::cap();
 if c.active_qubits() as usize+u.len()-1<=cap{return false;}
 let cuts=c.active_qubits() as usize+u.len()-1-cap;assert!(cuts<=max_saving(u.len()),"compact comparison exceeds proved terminal expansion budget");
 run(c,u,v,p,false,cuts);true
}
fn run(c:&mut Builder,u:&[QubitId],v:&[QubitId],p:Option<QubitId>,fault:bool,cuts:usize){
 let n=u.len();assert_eq!(n,v.len());assert!(n>=3);
 let mut set=std::collections::BTreeSet::new();assert!(u.iter().chain(v).all(|q|set.insert(q.0)),"comparison operands must be disjoint");
 assert!(!p.is_some_and(|q|u.contains(&q)),"seed cannot alias accumulator");
 if p==Some(v[0]){super::compare::cmp_lt_phase_v0(c,&u[1..],&v[1..],p,None);return;}
 assert!((1..=max_saving(n)).contains(&cuts));let operand_seed=p.is_some_and(|q|v[1..].contains(&q));let last=n-1;let m=n-1-cuts;
 let carries=c.alloc_qubits(m);c.x_all(u);
 c.cx(u[0],v[0]);let first=p.map_or(u[0],|q|{c.cx(u[0],q);q});
 c.ccx(first,v[0],carries[0]);if operand_seed{c.cx(u[0],p.unwrap());}c.cx(carries[0],u[0]);
 for i in 1..m{c.cx(u[i],v[i]);c.cx(u[i],u[i-1]);c.ccx(u[i-1],v[i],carries[i]);c.cx(carries[i],u[i]);}
 // Exact in-place MAJ suffix stores carries in operand wires, then reverses.
 for i in m..last{c.cx(u[i],v[i]);c.cx(u[i],u[i-1]);c.ccx(u[i-1],v[i],u[i]);}
 c.cz(u[last],v[last]);c.cz(u[last],u[last-1]);if !fault{c.cz(v[last],u[last-1]);}
 for i in (m..last).rev(){c.ccx(u[i-1],v[i],u[i]);c.cx(u[i],u[i-1]);c.cx(u[i],v[i]);}
 for i in (1..m).rev(){c.cx(carries[i],u[i]);let bit=c.alloc_bit();c.hmr(carries[i],bit);c.cz_if(u[i-1],v[i],bit);c.free_bit(bit);c.cx(u[i],u[i-1]);c.cx(u[i],v[i]);}
 c.cx(carries[0],u[0]);let bit=c.alloc_bit();c.hmr(carries[0],bit);
 if let Some(q)=p{if operand_seed{c.cx(u[0],q);}c.cz_if(q,v[0],bit);c.cx(u[0],q);}else{c.cz_if(u[0],v[0],bit);}
 c.free_bit(bit);c.cx(u[0],v[0]);
 // Preserve the total measurement draw count before returning to the caller.
 // Every carry is now zero. The dummy HMR has identically zero phase.
 // The omitted allocated carry originally consumed BOTH an R and an HMR draw.
 for _ in 0..2*cuts{let bit=c.alloc_bit();c.hmr(carries[0],bit);c.free_bit(bit);}c.free_vec(&carries);c.x_all(u);
}

#[cfg(test)]mod compact_compare_tests{
 use super::*;use crate::circuit::{analyze_ops,Op,OperationType};use crate::sim::Simulator;
 use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
 struct Words{bytes:Vec<u8>,pos:usize}impl XofReader for Words{fn read(&mut self,b:&mut[u8]){b.copy_from_slice(&self.bytes[self.pos..self.pos+b.len()]);self.pos+=b.len();}}
 thread_local!{static CUTS:std::cell::Cell<usize>=const{std::cell::Cell::new(1)};}
 fn draws(ops:&[Op])->usize{ops.iter().filter(|o|matches!(o.kind,OperationType::Hmr|OperationType::R)).count()}
 fn build(n:usize,seed:isize,new:bool,fault:bool)->(Vec<Op>,Vec<QubitId>,Vec<QubitId>,Option<QubitId>,crate::circuit::BitId,u32){
  let mut c=Builder::new();let u=c.alloc_qubits(n);let v=c.alloc_qubits(n);let p=if seed== -2{None}else if seed== -1{Some(c.alloc_qubit())}else{Some(v[seed as usize])};let all:Vec<_>=u.iter().chain(&v).copied().chain(if seed== -1{p}else{None}).collect();c.declare_qubit_register(&all);let guard=c.alloc_bit();c.push_condition(guard);
  std::env::remove_var("EXACT_CMP_COMPACT");std::env::set_var("PEBBLE_HARD_CAP","1536");
  let(_,peak)=c.r3_peak(|c|{if new{run(c,&u,&v,p,fault,CUTS.with(|x|x.get()))}else{super::super::compare::cmp_lt_phase_v0(c,&u,&v,p,None)}});c.pop_condition();(c.take_ops(),u,v,p,guard,peak)
 }
 fn fixture(n:usize,seed:isize,guard:u64,probe:Option<usize>,fault:bool){
  let old=build(n,seed,false,false);let new=build(n,seed,true,fault);assert_eq!(old.1,new.1);assert_eq!(old.2,new.2);assert_eq!(old.3,new.3);assert!(new.5<old.5,"n{n} seed{seed} old{} new{}",old.5,new.5);assert_eq!(draws(&old.0),draws(&new.0));
  let(nq,nb,_,_)=analyze_ops(old.0.iter().chain(&new.0));let bits=2*n+usize::from(seed== -1);let starts:Vec<_>=if probe.is_some(){vec![37]}else if n<=6{(0..1usize<<bits).step_by(64).collect()}else{(0..128).map(|j|j*64).collect()};
  for start in starts{let mut initial=vec![0u64;nq as usize];let mut input=Shake256::default();input.update(b"compact-phase-compare-input-v1");input.update(&(n as u64).to_le_bytes());input.update(&(start as u64).to_le_bytes());let mut rd=input.finalize_xof();for q in old.1.iter().chain(&old.2).copied().chain(if seed== -1{old.3}else{None}){let mut b=[0u8;8];rd.read(&mut b);initial[q.0 as usize]=u64::from_le_bytes(b);}
   if n<=6{for lane in 0..64{let value=start+lane;for(i,q)in old.1.iter().chain(&old.2).copied().chain(if seed== -1{old.3}else{None}).enumerate(){if value>>i&1!=0{initial[q.0 as usize]|=1u64<<lane;}else{initial[q.0 as usize]&=!(1u64<<lane);}}}}
   let mut expected=0u64;for lane in 0..64{let mut carry=old.3.map_or(0,|q|initial[q.0 as usize]>>lane&1);for i in 0..n{let a=1^(initial[old.1[i].0 as usize]>>lane&1);let b=initial[old.2[i].0 as usize]>>lane&1;carry=(a&b)^(a&carry)^(b&carry);}expected|=carry<<lane;}expected&=guard;
   for (idx,item) in [&old,&new].iter().enumerate(){let count=draws(&item.0);let mut bytes=vec![0u8;count*8];let mut h=Shake256::default();h.update(b"compact-phase-compare-measurements-v1");h.update(&(start as u64).to_le_bytes());h.finalize_xof().read(&mut bytes);if let Some(p)=probe{for j in 0..count{bytes[j*8..j*8+8].copy_from_slice(&(if p==j||p==count{u64::MAX}else{0u64}).to_le_bytes());}}
    let mut rng=Words{bytes,pos:0};let mut sim=Simulator::new(nq as usize,nb as usize,&mut rng);sim.qubits.copy_from_slice(&initial);sim.bits[item.4.0 as usize]=guard;sim.apply_iter(item.0.iter());assert_eq!(sim.qubits,initial,"all operand and helper lanes must restore");assert_eq!(sim.bits[item.4.0 as usize],guard);assert_eq!(sim.phase,expected,"native compact phase contract n{n} seed{seed} start{start} new{} probe{probe:?}",idx==1);drop(sim);assert_eq!(rng.pos,count*8);
   }
  }
 }
 #[test]fn exhaustive_phase_values_and_restoration_with_one_less_carry(){for n in 3..=6{for cuts in 1..=max_saving(n){CUTS.with(|x|x.set(cuts));for seed in [-2,-1,1,(n-1)as isize]{for guard in [u64::MAX,0xAA55C39F0678D12B,0]{fixture(n,seed,guard,None,false);}}}}}
 #[test]fn wide_arbitrary_operands_alias_seeds_and_measurement_outcomes(){for n in [8,22,56,128,256]{for cuts in 1..=max_saving(n){CUTS.with(|x|x.set(cuts));for seed in [-2,-1,1,(n-1)as isize]{fixture(n,seed,0x9A65F0C387124BED,None,false);}}}for cuts in 1..=3{CUTS.with(|x|x.set(cuts));for seed in [-2,-1,1,5]{let count=draws(&build(6,seed,false,false).0);for p in 0..count+2{fixture(6,seed,u64::MAX,Some(p),false);}}}}
 #[test]#[should_panic(expected="native compact phase contract")]fn omitted_cubic_phase_is_detected(){CUTS.with(|x|x.set(1));fixture(4,-1,u64::MAX,None,true);}
 #[test]#[should_panic(expected="seed cannot alias accumulator")]fn accumulator_alias_is_rejected(){let mut c=Builder::new();let u=c.alloc_qubits(4);let v=c.alloc_qubits(4);run(&mut c,&u,&v,Some(u[0]),false,1);}
}
