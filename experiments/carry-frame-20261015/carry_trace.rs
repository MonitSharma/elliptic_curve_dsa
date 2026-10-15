//! Read-only pre/post-fold carry observations on one preserved zero-slope input.
use crate::circuit::{analyze_ops,Op,QubitId};
use alloy_primitives::U256;
use std::sync::Mutex;
use sha3::digest::XofReader;
#[derive(Clone)]
struct Mark {at:usize,label:&'static str,m:QubitId,a:Vec<QubitId>,b:Vec<QubitId>,k:usize,borrow:Option<QubitId>}
static MARKS:Mutex<Vec<Mark>>=Mutex::new(Vec::new());
pub fn mark(at:usize,label:&'static str,m:QubitId,a:&[QubitId],b:&[QubitId],k:usize,borrow:Option<QubitId>){MARKS.lock().unwrap().push(Mark{at,label,m,a:a.to_vec(),b:b.to_vec(),k,borrow});}
struct Zero;
impl XofReader for Zero {fn read(&mut self,b:&mut[u8]){b.fill(0);}}
fn value(q:&[QubitId],words:&[u64])->U256{let mut v=U256::ZERO;for(i,q)in q.iter().enumerate(){if words[q.0 as usize]&1!=0{v|=U256::from(1)<<i;}}v}
pub fn run(ops:&[Op]){
 let text=std::fs::read_to_string("/home/hclau/ecdsa_research/arithmetic-repair-20261015/packets/structured.tsv").unwrap();let row:Vec<U256>=text.lines().nth(1).unwrap().split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect();assert_eq!(row[1],row[3]);
 let(nq,nb,_,regs)=analyze_ops(ops.iter());let(mut r0,mut r1)=(Zero,Zero);let mut s=super::observed_sim::Simulator::new(nq as usize,nb as usize,&mut r0);let mut reference=quantum_ecc::sim::Simulator::new(nq as usize,nb as usize,&mut r1);
 for lane in 0..64{for k in 0..4{s.set_register(&regs[k],row[k],lane);reference.set_register(&regs[k],row[k],lane);}}
 let marks=MARKS.lock().unwrap().clone();assert_eq!(marks.len(),2);let mut cursor=0;let mut before=None;
 s.apply_observed(ops.iter(),|at,s,_,_|{while cursor<marks.len()&&marks[cursor].at==at{let m=&marks[cursor];cursor+=1;let a=value(&m.a,&s.qubits);let b=value(&m.b,&s.qubits);let flag=s.qubits[m.m.0 as usize]&1;let borrow=m.borrow.map_or(0,|q|s.qubits[q.0 as usize]&1);
  eprintln!("CARRY_STATE label={} op={at} width={} target={a:#x} source={b:#x} flag={flag} window={} borrow={borrow} full_compare={}",m.label,m.a.len(),m.k,usize::from(a<b));
  if m.label=="before_fold"{assert_eq!(flag,usize::from(a<b)as u64);before=Some((a,b,flag));}
  else {let(ba,bb,bf)=before.unwrap();assert_eq!(b,bb);assert_eq!(flag,bf);let hi=m.a.len()-m.k;let pred=usize::from((a>>hi)<((b>>hi)+U256::from(borrow)));eprintln!("CARRY_COMPARE pre_target={ba:#x} post_target={a:#x} exact_pre_predicate={bf} full_post_predicate={} window_predicate={pred} upper_preserved={}",usize::from(a<b),ba>>54==a>>54);assert_ne!(pred as u64,flag);}
 }});
 assert_eq!(cursor,marks.len());reference.apply_iter(ops.iter());assert_eq!(s.qubits,reference.qubits);assert_eq!(s.bits,reference.bits);assert_eq!(s.phase,reference.phase);assert_eq!(s.stats.toffoli_gates,reference.stats.toffoli_gates);
 assert_eq!(s.get_register(&regs[0],0),row[4]);assert_eq!(s.get_register(&regs[1],0),row[5]);eprintln!("CARRY_OBSERVATION observer_equal=true correct_values=true fixed_inputs=1 replicated_lanes=64 measurement_outcomes=all_zero score=NONE");
}
