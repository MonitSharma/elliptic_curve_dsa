//! Read-only exact arithmetic and conditional phase observations, one fixed input.
use crate::circuit::{analyze_ops,Op,QubitId,OperationType};
use alloy_primitives::U256;
use std::sync::Mutex;
use sha3::digest::XofReader;
#[derive(Clone)]
struct Mark{at:usize,t:usize,label:&'static str,a:Vec<QubitId>,b:Vec<QubitId>,flags:Vec<QubitId>,seed:Option<QubitId>,bit:usize}
static MARKS:Mutex<Vec<Mark>>=Mutex::new(Vec::new());
pub fn mark(at:usize,t:usize,label:&'static str,a:&[QubitId],b:&[QubitId],flags:&[QubitId],seed:Option<QubitId>,bit:usize){MARKS.lock().unwrap().push(Mark{at,t,label,a:a.to_vec(),b:b.to_vec(),flags:flags.to_vec(),seed,bit});}
struct Outcomes{index:usize,flip:Option<usize>}
impl XofReader for Outcomes{fn read(&mut self,b:&mut[u8]){assert_eq!(b.len(),8);b.fill(if self.flip==Some(self.index){255}else{0});self.index+=1;}}
fn value(q:&[QubitId],words:&[u64])->U256{let mut v=U256::ZERO;for(i,q)in q.iter().enumerate(){if words[q.0 as usize]&1!=0{v|=U256::from(1)<<i;}}v}
pub fn run(ops:&[Op]){
 let all=MARKS.lock().unwrap().clone();let target_at=ops.iter().enumerate().filter(|(_,op)|matches!(op.kind,OperationType::Hmr|OperationType::R)).nth(780824).unwrap().0;
 let selected:Vec<_>=all.iter().filter(|m|m.label=="hmr"&&m.at==target_at&&m.flags[0].0==135&&m.bit==1555).collect();assert_eq!(selected.len(),1);let chosen=selected[0];
 let marks:Vec<_>=all.iter().filter(|m|m.t==chosen.t).collect();let ordinal=ops[..chosen.at].iter().filter(|o|matches!(o.kind,OperationType::Hmr|OperationType::R)).count();assert_eq!(ops[chosen.at].kind,OperationType::Hmr);
 eprintln!("JOINT_SITE t={} raw_op={} raw_random_read={} marks={}",chosen.t,chosen.at,ordinal,marks.len());
 let text=std::fs::read_to_string("/home/hclau/ecdsa_research/arithmetic-repair-20261015/packets/structured.tsv").unwrap();let row:Vec<U256>=text.lines().nth(1).unwrap().split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect();assert_eq!(row[1],row[3]);
 let(nq,nb,_,regs)=analyze_ops(ops.iter());
 for flip in [None,Some(ordinal)]{
  let(mut r0,mut r1)=(Outcomes{index:0,flip},Outcomes{index:0,flip});let mut sim=super::observed_sim::Simulator::new(nq as usize,nb as usize,&mut r0);let mut reference=quantum_ecc::sim::Simulator::new(nq as usize,nb as usize,&mut r1);
  for lane in 0..64{for k in 0..4{sim.set_register(&regs[k],row[k],lane);reference.set_register(&regs[k],row[k],lane);}}
  let mut cursor=0;let mut exact=None;
  sim.apply_observed(ops.iter(),|at,s,_,cond|{if at==chosen.at+1{assert_eq!(s.bits[chosen.bit],if flip.is_some(){u64::MAX}else{0});eprintln!("JOINT_MEASUREMENT_VERIFIED flip={} selected_bit={:#x}",flip.is_some(),s.bits[chosen.bit]);}while cursor<marks.len()&&marks[cursor].at==at{let m=marks[cursor];cursor+=1;let a=value(&m.a,&s.qubits);let b=value(&m.b,&s.qubits);let flags:Vec<_>=m.flags.iter().map(|q|s.qubits[q.0 as usize]&1).collect();let seed=m.seed.map_or(0,|q|s.qubits[q.0 as usize]&1);
   eprintln!("JOINT_STATE flip={} label={} op={} cond={:#x} phase={:#x} width={} a={:#x} b={:#x} flags={:?} seed={}",flip.is_some(),m.label,at,cond,s.phase,m.a.len(),a,b,flags,seed);
   if m.label=="entry"{let s0=if flags[0]==1{!b}else{b};let s1=if flags[1]==1{!b}else{b};let(x0,g0)=a.overflowing_add(s0);let(x1,h1)=x0.overflowing_add(s1<<1);exact=Some((x0,x1,g0 as u64,h1 as u64));eprintln!("JOINT_EXACT x0={x0:#x} x1={x1:#x} g0={} h1={} expected_m0={}",g0,h1,(g0 as u64)^(h1 as u64));}
   if m.label=="after_add1"{let(_,x1,g0,h1)=exact.unwrap();assert_eq!(a,x1);assert_eq!(flags[0],g0^h1^((b>>255usize).to::<u64>()^(flags[2])));}
   if m.label=="cmp"&&cond!=0{let pred=(a<b)||(a==b&&seed!=0);let(x0,_,g0,h1)=exact.unwrap();eprintln!("JOINT_COMPARE pred={} exact_g0={} exact_h1={} expected_window={:#x} actual_window={:#x}",pred,g0,h1,x0>>(256-m.a.len()),a);}
  }});
  assert_eq!(cursor,marks.len());reference.apply_iter(ops.iter());assert_eq!(sim.qubits,reference.qubits);assert_eq!(sim.bits,reference.bits);assert_eq!(sim.phase,reference.phase);assert_eq!(sim.stats.toffoli_gates,reference.stats.toffoli_gates);
  assert_eq!(sim.get_register(&regs[0],0),row[4]);assert_eq!(sim.get_register(&regs[1],0),row[5]);assert_eq!(sim.phase,if flip.is_some(){u64::MAX}else{0});eprintln!("JOINT_OBSERVATION flip={} phase={:#x} observer_equal=true correct_values=true inputs=1 replicated_lanes=64 score=NONE",flip.is_some(),sim.phase);
 }
}
