// Exact backwards value cone. Reject compile if measurement randomness reaches
// an output bit: such a stream requires exact RNG replay and is unsupported.
use quantum_ecc::circuit::NO_BIT;
struct ValueCone { ops: Vec<Op>, nq: usize, nb: usize, random_dependencies: usize, rng_indices:Vec<usize>, rng_count:usize }
impl ValueCone {
 fn compile(ops:&[Op], regs:&[Vec<QubitOrBit>], nq:usize, nb:usize)->Self {
  let mut q=vec![false;nq]; let mut b=vec![false;nb];
  for reg in &regs[..2] { for x in reg { match x { QubitOrBit::Qubit(x)=>q[x.0 as usize]=true, QubitOrBit::Bit(x)=>b[x.0 as usize]=true } } }
  let mut conds=Vec::<Vec<BitId>>::with_capacity(ops.len()); let mut stack=Vec::new();
  for o in ops { if o.kind==OperationType::PopCondition {stack.pop();} conds.push(stack.clone()); if o.kind==OperationType::PushCondition {stack.push(o.c_condition);} }
  let mut kept=Vec::new(); let mut rnd=0; let mut rng_indices=Vec::new(); let mut rng_count=0; let all_rng:Vec<usize>=ops.iter().map(|o|{let i=rng_count;if matches!(o.kind,OperationType::R|OperationType::Hmr){rng_count+=1;}i}).collect();
  for ((o, cs),ri) in ops.iter().zip(conds.iter()).zip(all_rng.iter()).rev() {
   use OperationType::*;
   let tq=o.q_target.0 as usize; let tb=o.c_target.0 as usize;
   let conditional=o.c_condition!=NO_BIT || !cs.is_empty();
   let take=match o.kind {
    PushCondition|PopCondition=>{kept.push(*o);rng_indices.push(*ri);continue;},
    CCX|CX|X=>q[tq], Swap=>q[tq]||q[o.q_control1.0 as usize],
    R=>q[tq], Hmr=>{if b[tb] {rnd+=1;} q[tq]||b[tb]},
    BitInvert|BitStore0|BitStore1=>b[tb], _=>false
   };
   if !take {continue;}
   for x in cs {b[x.0 as usize]=true;}
   match o.kind {
    CCX=>{q[o.q_control1.0 as usize]=true;q[o.q_control2.0 as usize]=true;},
    CX=>{q[o.q_control1.0 as usize]=true;},
    Swap=>{q[tq]=true;q[o.q_control1.0 as usize]=true;},
    R|Hmr=>{if !conditional {q[tq]=false;} if o.kind==Hmr&&!conditional {b[tb]=false;}},
    BitStore0|BitStore1=>{if !conditional {b[tb]=false;}}, _=>{}
   }
   if o.c_condition!=NO_BIT {b[o.c_condition.0 as usize]=true;}
   kept.push(*o);rng_indices.push(*ri);
  }
  kept.reverse();rng_indices.reverse();
  eprintln!("VALUE_CONE input_ops={} kept={} random_dependencies={} nq={nq} nb={nb}", ops.len(),kept.len(),rnd);
  Self {ops:kept,nq,nb,random_dependencies:rnd,rng_indices,rng_count}
 }
 fn apply(&self, q:&mut [u64], b:&mut [u64], words:&[u64]) {
  assert_eq!(words.len(),self.rng_count);
  let mut stack=Vec::new();let mut base=u64::MAX;
  for (o,ri) in self.ops.iter().zip(&self.rng_indices) {
   let c=base & if o.c_condition==NO_BIT {u64::MAX} else {b[o.c_condition.0 as usize]};
   let t=o.q_target.0 as usize;
   use OperationType::*;
   match o.kind {
    PushCondition=>{stack.push(base);base &= b[o.c_condition.0 as usize];},
    PopCondition=>{base=stack.pop().unwrap();},
    CCX=>q[t]^=c&q[o.q_control1.0 as usize]&q[o.q_control2.0 as usize],
    CX=>q[t]^=c&q[o.q_control1.0 as usize], X=>q[t]^=c,
    Swap=>{let a=o.q_control1.0 as usize;let d=c&(q[t]^q[a]);q[t]^=d;q[a]^=d;},
    R=>q[t]&=!c,
    Hmr=>{q[t]&=!c;let bt=o.c_target.0 as usize;b[bt]=(b[bt]&!c)^(words[*ri]&c);},
    BitInvert=>b[o.c_target.0 as usize]^=c,
    BitStore0=>b[o.c_target.0 as usize]&=!c,
    BitStore1=>b[o.c_target.0 as usize]|=c,
    _=>unreachable!()
   }
  }
 }
}

fn main() {
 let a:Vec<String>=std::env::args().collect(); if a[1]=="@export" {export_census(&a[2],&a[3],a[4].parse().unwrap(),&a[5]);return;} if a[1]=="@curve" {fast_curve_test(a[2].parse().unwrap());return;} let ops=load_ops(&a[1]).unwrap();
 let (nq,nb,_,regs)=analyze_ops(ops.iter()); let cone=ValueCone::compile(&ops,&regs,nq as usize,nb as usize);
 if a.len()==2 {return;}
 
 // Independent fresh-input differential with identical classical inputs, using
 // protected Simulator for the complete stream and its original RNG semantics.
 let batches:usize=a[2].parse().unwrap(); let label=&a[3];
 let curve=secp256k1();let fast=FastCurve::new(10); let mut tcone=std::time::Duration::ZERO;let mut tfull=std::time::Duration::ZERO;
 let mut values=0; let mut rejects=0;
 for batch in 0..batches {
  let mut h=Shake256::default(); h.update(b"ecdsa-research-failure-census-v1");h.update(&(label.len()as u64).to_le_bytes());h.update(label.as_bytes());h.update(&(batch as u64).to_le_bytes());let mut rng=h.finalize_xof();
  let mut sim=Simulator::new(nq as usize,nb as usize,&mut rng);let mut exp=Vec::new();
  for lane in 0..64 {let mut rb=[[0u8;32];2]; XofReader::read(sim.xof,&mut rb[0]);XofReader::read(sim.xof,&mut rb[1]);let t=curve.mul(curve.gx,curve.gy,U256::from_le_bytes(rb[0]));let o=curve.mul(curve.gx,curve.gy,U256::from_le_bytes(rb[1]));assert!(t.0!=o.0);exp.push(curve.add(t.0,t.1,o.0,o.1)); for (r,v)in[t.0,t.1,o.0,o.1].iter().enumerate(){sim.set_register(&regs[r],*v,lane);} }
  let(mut q,mut b)=(sim.qubits.clone(),sim.bits.clone());let tm=std::time::Instant::now();let mut rng_copy=sim.xof.clone();let mut bytes=vec![0u8;cone.rng_count*8];XofReader::read(&mut rng_copy,&mut bytes);let words:Vec<u64>=bytes.chunks_exact(8).map(|x|u64::from_le_bytes(x.try_into().unwrap())).collect();cone.apply(&mut q,&mut b,&words);tcone+=tm.elapsed();let tm=std::time::Instant::now();sim.apply_iter(ops.iter());tfull+=tm.elapsed();
  for r in &regs[..2] {for x in r {match x {QubitOrBit::Qubit(x)=>assert_eq!(q[x.0 as usize],sim.qubit(*x),"value mismatch batch={batch}"),QubitOrBit::Bit(x)=>assert_eq!(b[x.0 as usize],sim.bit(*x))}}}
  let mut bad=0;for(lane,e)in exp.iter().enumerate(){if sim.get_register(&regs[0],lane)!=e.0||sim.get_register(&regs[1],lane)!=e.1 {bad+=1;}}values+=bad;rejects+=usize::from(bad>0);
  if batch%16==0{eprintln!("DIFF_PROGRESS batch={batch} value_failures={values}");}
 }
 println!("{{\"batches\":{batches},\"shots\":{},\"value_failures\":{values},\"rejected_batches\":{rejects},\"cone_us_per_shot\":{:.3},\"full_us_per_shot\":{:.3},\"kept_ops\":{},\"random_dependencies\":{}}}",batches*64,tcone.as_secs_f64()*1e6/(batches*64)as f64,tfull.as_secs_f64()*1e6/(batches*64)as f64,cone.ops.len(),cone.random_dependencies);
}
