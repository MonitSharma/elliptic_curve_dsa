#![allow(dead_code,unused_imports)]
include!("../prefix.rs");
include!("../fast_sim_wide.rs");
use std::{fs,path::Path,io::BufWriter};
const DEFAULT_ZSTD_LEVEL:i32=3;
unsafe extern "C" {fn zero8_run(ops:*const CompactOp,n:usize,q:*mut u64,b:*mut u64,stack:*mut u64,cap:usize)->i32;}
struct ZeroReader;
impl XofReader for ZeroReader {fn read(&mut self,out:&mut[u8]){out.fill(0);}}
fn run(p:&Compact,q:&mut[u64],b:&mut[u64]){let mut stack=vec![0;4096*8];assert_eq!(unsafe{zero8_run(p.ops.as_ptr(),p.ops.len(),q.as_mut_ptr(),b.as_mut_ptr(),stack.as_mut_ptr(),4096)},0);}
fn load_ir(path:&str,nq:usize,nb:usize)->Compact{
 let d=fs::read(path).unwrap();assert_eq!(d.len()%16,0);let mut ops=Vec::new();
 for x in d.chunks_exact(16){let u16at=|i|u16::from_le_bytes(x[i..i+2].try_into().unwrap());let u32at=|i|u32::from_le_bytes(x[i..i+4].try_into().unwrap());let o=CompactOp{a:u16at(0),b:u16at(2),t:u16at(4),k:x[6],pad:x[7],c:u32at(8),bt:u32at(12)};
  assert_eq!(o.pad,0);assert!([o.a,o.b,o.t].iter().all(|x|*x==u16::MAX||(*x as usize)<nq));assert!(o.c==u32::MAX||(o.c as usize)<nb);assert!(o.bt==u32::MAX||(o.bt as usize)<nb);
  assert!([0,3,4,5,6,7,8,9,10,11,12,13,14,15,16,35,36,37,38,40,42,43,44,45].contains(&o.k));let k=if o.k>=32{o.k-32}else{o.k};
  if [6,7,8,9,10,11,12,13,14].contains(&k){assert!((o.t as usize)<nq);}if[8,9,10,13,14].contains(&k){assert!((o.a as usize)<nq);}if[13,14].contains(&k){assert!((o.b as usize)<nq);}if[3,4,5,12].contains(&k){assert!((o.bt as usize)<nb);}if k==15{assert!((o.c as usize)<nb);}ops.push(o);
 }Compact{ops,rng_count:0}
}
fn verify(label:&str,initialq:&[u64],initialb:&[u64],full:&Compact,ir:&Compact,ops:&[Op],regs:&[Vec<QubitOrBit>],nq:usize,nb:usize){
 let(mut fq,mut fb)=(initialq.to_vec(),initialb.to_vec());run(full,&mut fq,&mut fb);
 let(mut sq,mut sb)=(initialq.to_vec(),initialb.to_vec());run(ir,&mut sq,&mut sb);
 for j in 0..8 {let mut reader=ZeroReader;let mut sim=Simulator::new(nq,nb,&mut reader);
  for i in 0..nq{sim.qubits[i]=initialq[i*8+j];}for i in 0..nb{sim.bits[i]=initialb[i*8+j];}sim.apply_iter(ops.iter());
  for i in 0..nq{assert_eq!(fq[i*8+j],sim.qubits[i],"full native q{i} lane-group{j} {label}");}
  for i in 0..nb{assert_eq!(fb[i*8+j],sim.bits[i],"full native bit{i} lane-group{j} {label}");}
  for r in &regs[..2]{for w in r{match w{QubitOrBit::Qubit(id)=>assert_eq!(sq[id.0 as usize*8+j],sim.qubits[id.0 as usize],"IR output {label}"),QubitOrBit::Bit(id)=>assert_eq!(sb[id.0 as usize*8+j],sim.bits[id.0 as usize],"IR output {label}")}}}
 }println!("FRESH_ALL70_ZERO_IR_CONTROL_PASS label={label} packed_slots=512 full_all_q_b=true scored_bits=512 phase_not_queried=true");
}
fn put(rows:&[[U256;4]],regs:&[Vec<QubitOrBit>],nq:usize,nb:usize)->(Vec<u64>,Vec<u64>){
 assert!(rows.len()<=512);let(mut q,mut b)=(vec![0;nq*8],vec![0;nb*8]);
 for(index,row)in rows.iter().enumerate(){let(j,lane)=(index/64,index%64);for(reg,val)in regs[..4].iter().zip(row){for(i,w)in reg.iter().enumerate(){let v=(val.bit(i)as u64)<<lane;match w{QubitOrBit::Qubit(id)=>q[id.0 as usize*8+j]|=v,QubitOrBit::Bit(id)=>b[id.0 as usize*8+j]|=v}}}}
 (q,b)
}
fn negatives(){
 let no=u32::MAX;let make=|k,c|CompactOp{a:0,b:0,t:0,k,pad:0,c,bt:0};
 for(k,c,cap,expected)in[(255,no,1,4),(16,no,1,3),(15,0,0,2),(15,0,1,5)]{
  let mut q=[0u64;8];let mut b=[u64::MAX;8];let mut stack=[0u64;8];let o=make(k,c);
  assert_eq!(unsafe{zero8_run(&o,1,q.as_mut_ptr(),b.as_mut_ptr(),stack.as_mut_ptr(),cap)},expected);
 }println!("FRESH_ALL70_ZERO_IR_NEGATIVES_PASS opcode_underflow_overflow_unbalanced=4");
}
fn main(){
 let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),5);let ops=load_ops(&a[1]).unwrap();assert_eq!(ops.len(),11630716);assert_eq!(ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count(),906156);
 let(nq,nb,_,regs)=analyze_ops(ops.iter());assert_eq!((nq,nb),(1234,45701));assert_eq!(regs.len(),4);assert!(regs.iter().all(|r|r.len()==256));
 let(nq,nb)=(nq as usize,nb as usize);let full=Compact::compile(&ops);let ir=load_ir(&a[2],nq,nb);negatives();
 for case in 0..4 {let(mut q,mut b)=(vec![0;nq*8],vec![0;nb*8]);let mut h=Shake256::default();h.update(b"all70-zero-mr-declared-ABI-fixed-controls-20261016");let mut random=h.finalize_xof();
  for(port,w)in regs.iter().flatten().enumerate(){for j in 0..8{let v=match case{0=>0,1=>u64::MAX,2=>if(port+j)%2==0{0xaaaaaaaaaaaaaaaa}else{0x5555555555555555},_=>{let mut d=[0;8];XofReader::read(&mut random,&mut d);u64::from_le_bytes(d)}};match w{QubitOrBit::Qubit(id)=>q[id.0 as usize*8+j]=v,QubitOrBit::Bit(id)=>b[id.0 as usize*8+j]=v}}}
  verify(&format!("declared-ABI-state-{case}"),&q,&b,&full,&ir,&ops,&regs,nq,nb);
 }
 let audit=fs::read_to_string(&a[3]).unwrap().lines().filter(|l|!l.is_empty()).map(|l|{let f:Vec<_>=l.split_whitespace().skip(1).map(|x|U256::from_str_radix(x.trim_start_matches("0x"),16).unwrap()).collect();assert_eq!(f.len(),6);[f[0],f[1],f[2],f[3]]}).collect::<Vec<_>>();assert_eq!(audit.len(),32);
 let(q,b)=put(&audit,&regs,nq,nb);verify("existing-audit32",&q,&b,&full,&ir,&ops,&regs,nq,nb);
 let corpus=fs::read_to_string(&a[4]).unwrap().lines().skip(1).take(512).map(|l|{let f:Vec<_>=l.split('\t').collect();std::array::from_fn(|j|U256::from_str_radix(f[4+j],16).unwrap())}).collect::<Vec<[U256;4]>>();assert_eq!(corpus.len(),512);
 for count in [0,1,7,11,31,32,63,64,65,511,512]{let(q,b)=put(&corpus[..count],&regs,nq,nb);verify(&format!("existing-partial-{count}"),&q,&b,&full,&ir,&ops,&regs,nq,nb);}
 println!("FRESH_ALL70_ZERO_IR_ALL_CONTROLS_PASS source_ops=11630716 Q1234 B45701 scored_bits=512 native_states=4 audit=32 partial_cases=11 phase_pass_authority=false");
}
