#[cfg(test)]
mod tests{
use super::*;
use crate::circuit::{analyze_ops,RegisterId};
use quantum_ecc::sim::Simulator;
struct Events{pattern:usize,at:usize}
impl sha3::digest::XofReader for Events{fn read(&mut self,out:&mut[u8]){
assert_eq!(out.len(),8);let w=if self.pattern>>self.at&1==0{0u64}else{u64::MAX};
self.at+=1;out.copy_from_slice(&w.to_le_bytes());}}
fn program()->Vec<Op>{
let mut p=vec![];let mut r=Op::empty();r.kind=K::Register;r.r_target=RegisterId(0);p.push(r);
for q in 0..4{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.q_target=QubitId(q);p.push(o);}
for b in 0..4{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.c_target=BitId(b);p.push(o);}
p.extend([
gate(K::CCX,Some(0),Some(1),Some(3),None,Some(0)),
gate(K::CCX,Some(1),Some(2),Some(3),None,Some(1)),
gate(K::X,None,None,Some(0),None,None),
gate(K::X,None,None,Some(0),None,None),
gate(K::CCX,Some(0),Some(1),Some(3),None,Some(2)),
gate(K::CCX,Some(1),Some(2),Some(3),None,Some(3))]);p}
fn check(p:&[Op],q:&[Op])->bool{
let (nq,nb,_,_)=analyze_ops(q.iter());assert!(nq>4);
let mr=q.iter().filter(|o|matches!(o.kind,K::Hmr|K::R)).count();assert_eq!(mr,2);
let mut ok=true;let mut saved=0;
for pattern in 0..4{for batch in 0..4{
let mut xa=Events{pattern:0,at:0};let mut xb=Events{pattern,at:0};
let mut a=Simulator::new(4,4,&mut xa);let mut b=Simulator::new(nq as usize,nb as usize,&mut xb);
for bit in 0..8{let v=(0..64).fold(0u64,|v,l|v|(((((batch*64+l)>>bit)&1)as u64)<<l));
if bit<4{a.qubits[bit]=v;b.qubits[bit]=v;}else{a.bits[bit-4]=v;b.bits[bit-4]=v;}}
for x in &mut b.bits[4..]{*x=0xa5a5a5a5a5a5a5a5;}
a.phase=0x55aa55aa55aa55aa;b.phase=a.phase;
a.apply_iter(p.iter());b.apply_iter(q.iter());
ok&=a.qubits==b.qubits[..4]&&a.bits==b.bits[..4]&&a.phase==b.phase;
ok&=b.qubits[4..].iter().all(|v|*v==0)&&b.bits[4..].iter().all(|v|*v==0);
assert!(b.stats.toffoli_gates<=a.stats.toffoli_gates);saved+=a.stats.toffoli_gates-b.stats.toffoli_gates;
}}
assert!(saved>0);ok}
#[test]fn wide_cache_all_inputs_and_measurements(){let p=program();let q=optimize(p.clone());
assert_eq!(q,optimize(p.clone()));assert!(check(&p,&q));println!("WIDE_NATIVE cases=1024 independent_outcomes=4 clean_new_quantum=true dirty_classical=true");}
#[test]fn wide_cache_phase_fault_detected(){let p=program();let mut q=optimize(p.clone());
let i=q.iter().position(|o|o.kind==K::CZ).unwrap();q.remove(i);assert!(!check(&p,&q));}
}
