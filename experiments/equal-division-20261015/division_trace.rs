//! Raw control division probe: reset only payload at a verified empty-condition boundary.
use crate::circuit::{analyze_ops,Op,QubitId,OperationType};
use alloy_primitives::U256;
use std::sync::Mutex;
use sha3::digest::XofReader;
#[derive(Clone)]
struct Mark{at:usize,label:&'static str,t:usize,a:Vec<QubitId>,b:Vec<QubitId>,letter:Vec<QubitId>}
static MARKS:Mutex<Vec<Mark>>=Mutex::new(Vec::new());
pub fn mark(at:usize,label:&'static str,t:usize,a:&[QubitId],b:&[QubitId],letter:&[QubitId]){MARKS.lock().unwrap().push(Mark{at,label,t,a:a.to_vec(),b:b.to_vec(),letter:letter.to_vec()});}
struct Zero;
impl XofReader for Zero{fn read(&mut self,b:&mut[u8]){b.fill(0);}}
fn value(q:&[QubitId],words:&[u64])->U256{let mut v=U256::ZERO;for(i,q)in q.iter().enumerate(){if words[q.0 as usize]&1!=0{v|=U256::from(1)<<i;}}v}
pub fn run(ops:&[Op]){
 let marks=MARKS.lock().unwrap().clone();let begin=marks.iter().find(|m|m.label=="input").unwrap();let end=marks.iter().find(|m|m.label=="output").unwrap();
 for limit in [begin.at,end.at]{let mut depth=0isize;for op in &ops[..limit]{match op.kind{OperationType::PushCondition=>depth+=1,OperationType::PopCondition=>depth-=1,_=>{}}assert!(depth>=0);}assert_eq!(depth,0);}
 let text=std::fs::read_to_string("/home/hclau/ecdsa_research/arithmetic-repair-20261015/packets/structured.tsv").unwrap();let row:Vec<U256>=text.lines().nth(1).unwrap().split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect();let(nq,nb,_,regs)=analyze_ops(ops.iter());
 for case in ["equal","zero","one","pminus1"]{
  let(mut r0,mut r1)=(Zero,Zero);let mut sim=super::observed_sim::Simulator::new(nq as usize,nb as usize,&mut r0);let mut reference=quantum_ecc::sim::Simulator::new(nq as usize,nb as usize,&mut r1);
  for lane in 0..64{for k in 0..4{sim.set_register(&regs[k],row[k],lane);reference.set_register(&regs[k],row[k],lane);}}
  sim.apply_iter(ops[..begin.at].iter());reference.apply_iter(ops[..begin.at].iter());assert_eq!(sim.qubits,reference.qubits);assert_eq!(sim.bits,reference.bits);assert_eq!(sim.phase,reference.phase);
  let x=value(&begin.b,&sim.qubits);let y=match case{"equal"=>x,"zero"=>U256::ZERO,"one"=>U256::from(1),_=>U256::MAX-U256::from(0x1000003d1u64)};
  for(i,q)in begin.a.iter().enumerate(){let v=if y.bit(i){u64::MAX}else{0};sim.qubits[q.0 as usize]=v;reference.qubits[q.0 as usize]=v;}
  eprintln!("DIVISION_INPUT case={case} x={x:#x} y={y:#x} input_op={} output_op={} held_wrapper_flags=0",begin.at,end.at);
  let relevant:Vec<_>=marks.iter().filter(|m|m.at>=begin.at&&m.at<end.at).collect();let mut cursor=0;
  sim.apply_observed(ops[begin.at..end.at].iter(),|at,s,_,cond|{let at=at+begin.at;while cursor<relevant.len()&&relevant[cursor].at==at{let m=relevant[cursor];cursor+=1;if case=="equal" {let a=value(&m.a,&s.qubits);let b=value(&m.b,&s.qubits);let letter:Vec<_>=m.letter.iter().map(|q|s.qubits[q.0 as usize]&1).collect();eprintln!("DIVISION_TICK label={} tick={} op={at} cond={cond:#x} a={a:#x} b={b:#x} letter={letter:?}",m.label,m.t);}}});
  assert_eq!(cursor,relevant.len());reference.apply_iter(ops[begin.at..end.at].iter());assert_eq!(sim.qubits,reference.qubits);assert_eq!(sim.bits,reference.bits);assert_eq!(sim.phase,reference.phase);assert_eq!(sim.stats.toffoli_gates,reference.stats.toffoli_gates);
  eprintln!("DIVISION_OUTPUT case={case} x={:#x} y={:#x} phase={:#x} observer_equal=true score=NONE",value(&end.b,&sim.qubits),value(&end.a,&sim.qubits),sim.phase);
 }
}
