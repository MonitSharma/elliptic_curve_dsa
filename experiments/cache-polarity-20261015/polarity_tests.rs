#[cfg(test)]
mod polarity_tests {
use super::*;
use crate::circuit::{analyze_ops,RegisterId};
use crate::sim::Simulator;
struct Events {pattern:usize,at:usize}
impl sha3::digest::XofReader for Events {fn read(&mut self,out:&mut[u8]) {
assert_eq!(out.len(),8);let v=if self.pattern>>self.at&1==0{0u64}else{u64::MAX};self.at+=1;out.copy_from_slice(&v.to_le_bytes());}}
fn program()->Vec<Op> {
let mut p=vec![];let mut r=Op::empty();r.kind=K::Register;r.r_target=RegisterId(0);p.push(r);
for q in 0..3 {let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.q_target=QubitId(q);p.push(o);}
for b in 0..5 {let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.c_target=BitId(b);p.push(o);}
// Four polarities, swapped control orientation, independent conditional uses,
// and a surrounding guard whose source bit is changed after being pushed.
for i in 0..4 {
    match i {1|3=>p.push(gate(K::X,None,None,Some(0),None,None)),
      2=>{p.push(gate(K::X,None,None,Some(0),None,None));p.push(gate(K::X,None,None,Some(1),None,None));},_=>{}}
    p.push(push(4));p.push(gate(K::BitInvert,None,None,None,Some(4),None));
    p.push(gate(K::CCX,Some(if i%2==0{0}else{1}),Some(if i%2==0{1}else{0}),Some(2),None,Some(i)));
    p.push(gate(K::BitInvert,None,None,None,Some(4),None));p.push(pop());
}
p
}
fn check(p:&[Op],q:&[Op])->bool {
let(nq,nb,_,_)=analyze_ops(q.iter());let mr=q.iter().filter(|o|o.kind==K::Hmr).count();assert!(mr>0&&mr<=4);
let mut ok=true;let mut savings=0;
for pattern in 0..1usize<<mr {for batch in 0..4 {
let mut xa=Events{pattern:0,at:0};let mut xb=Events{pattern,at:0};
let mut a=Simulator::new(3,5,&mut xa);let mut b=Simulator::new(nq as usize,nb as usize,&mut xb);
for bit in 0..8 {let v=(0..64).fold(0u64,|v,l|v|(((((batch*64+l)>>bit)&1)as u64)<<l));
if bit<3 {a.qubits[bit]=v;b.qubits[bit]=v;}else{a.bits[bit-3]=v;b.bits[bit-3]=v;}}
for x in &mut b.bits[5..] {*x=0xa5a5a5a5a5a5a5a5;}a.phase=0x55aa55aa55aa55aa;b.phase=a.phase;
a.apply_iter(p.iter());b.apply_iter(q.iter());
ok&=a.qubits==b.qubits[..3]&&a.bits==b.bits[..5]&&a.phase==b.phase;
ok&=b.qubits[3..].iter().all(|x|*x==0)&&b.bits[5..].iter().all(|x|*x==0);
assert!(b.stats.toffoli_gates<=a.stats.toffoli_gates);savings+=a.stats.toffoli_gates-b.stats.toffoli_gates;
}} assert!(savings>0);ok
}
#[test] fn complemented_controls_all_states_and_outcomes() {let p=program();let q=optimize(p.clone());assert_eq!(q,optimize(p.clone()));assert!(check(&p,&q));}
#[test] fn complemented_phase_fault_detected() {let p=program();let mut q=optimize(p.clone());let i=q.iter().position(|o|o.kind==K::Z).expect("linear phase correction");q.remove(i);assert!(!check(&p,&q));}
}
