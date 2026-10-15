//! Read actual wrapper interfaces on one preserved zero-slope input.
use crate::circuit::{analyze_ops,Op,QubitId};
use alloy_primitives::U256;
use std::sync::Mutex;
use sha3::digest::XofReader;
#[derive(Clone)]
struct Mark{at:usize,divide:bool,label:&'static str,y:Vec<QubitId>,x:Vec<QubitId>,flags:Vec<QubitId>}
static MARKS:Mutex<Vec<Mark>>=Mutex::new(Vec::new());
pub fn mark(at:usize,divide:bool,label:&'static str,y:&[QubitId],x:&[QubitId],flags:&[QubitId]){MARKS.lock().unwrap().push(Mark{at,divide,label,y:y.to_vec(),x:x.to_vec(),flags:flags.to_vec()});}
struct Zero;
impl XofReader for Zero{fn read(&mut self,b:&mut[u8]){b.fill(0);}}
fn value(q:&[QubitId],words:&[u64])->U256{let mut v=U256::ZERO;for(i,q)in q.iter().enumerate(){if words[q.0 as usize]&1!=0{v|=U256::from(1)<<i;}}v}
pub fn run(ops:&[Op]){
 let text=std::fs::read_to_string("/home/hclau/ecdsa_research/arithmetic-repair-20261015/packets/structured.tsv").unwrap();let row:Vec<U256>=text.lines().nth(1).unwrap().split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect();assert_eq!(row[1],row[3]);
 let(nq,nb,_,regs)=analyze_ops(ops.iter());let(mut r0,mut r1)=(Zero,Zero);let mut sim=super::observed_sim::Simulator::new(nq as usize,nb as usize,&mut r0);let mut reference=quantum_ecc::sim::Simulator::new(nq as usize,nb as usize,&mut r1);
 for lane in 0..64{for k in 0..4{sim.set_register(&regs[k],row[k],lane);reference.set_register(&regs[k],row[k],lane);}}
 let marks=MARKS.lock().unwrap().clone();assert_eq!(marks.len(),10);let mut cursor=0;
 sim.apply_observed(ops.iter(),|at,s,_,cond|{while cursor<marks.len()&&marks[cursor].at==at{let m=&marks[cursor];cursor+=1;let y=value(&m.y,&s.qubits);let x=value(&m.x,&s.qubits);let flags:Vec<_>=m.flags.iter().map(|q|s.qubits[q.0 as usize]&1).collect();eprintln!("PAYLOAD_INTERFACE divide={} label={} op={at} cond={cond:#x} x={x:#x} y={y:#x} flags={flags:?}",m.divide,m.label);}});
 assert_eq!(cursor,marks.len());reference.apply_iter(ops.iter());assert_eq!(sim.qubits,reference.qubits);assert_eq!(sim.bits,reference.bits);assert_eq!(sim.phase,reference.phase);assert_eq!(sim.stats.toffoli_gates,reference.stats.toffoli_gates);
 eprintln!("PAYLOAD_OBSERVATION observer_equal=true fixed_inputs=1 replicated_lanes=64 actual_x={:#x} expected_x={:#x} actual_y={:#x} expected_y={:#x} phase={:#x} score=NONE",sim.get_register(&regs[0],0),row[4],sim.get_register(&regs[1],0),row[5],sim.phase);
}
