#![allow(dead_code,unused_imports)]
include!("prefix.rs");
include!("fast_sim_wide.rs");
use std::{fs,path::Path,io::BufWriter,time::Instant};
const DEFAULT_ZSTD_LEVEL:i32=3;
unsafe extern "C"{fn zero8_run(ops:*const CompactOp,n:usize,q:*mut u64,b:*mut u64,stack:*mut u64,cap:usize)->i32;}
struct ZeroReader;impl XofReader for ZeroReader{fn read(&mut self,out:&mut[u8]){out.fill(0);}}
fn and(a:u8,b:u8)->u8{if a==0||b==0{0}else if a==1&&b==1{1}else{2}}
fn or(a:u8,b:u8)->u8{if a==1||b==1{1}else if a==0&&b==0{0}else{2}}
fn not(a:u8)->u8{if a==2{2}else{1-a}}
fn xor(a:u8,b:u8)->u8{if a==2||b==2{2}else{a^b}}
fn simplify(p:&Compact,regs:&[Vec<QubitOrBit>],nb:usize)->Compact{
 let mut bits=vec![0u8;nb];for r in regs{for w in r{if let QubitOrBit::Bit(id)=w{bits[id.0 as usize]=2;}}}
 let mut base=1;let mut stack=Vec::new();let mut out=Vec::new();
 for raw in &p.ops{let mut o=*raw;let guard=if o.c==u32::MAX{1}else{bits[o.c as usize]};let c=and(base,guard);match o.k{
  15=>{stack.push(base);base=and(base,bits[o.c as usize]);out.push(o);continue;},16=>{base=stack.pop().unwrap();out.push(o);continue;},
  3=>bits[o.bt as usize]=xor(bits[o.bt as usize],c),4=>bits[o.bt as usize]=and(bits[o.bt as usize],not(c)),5=>bits[o.bt as usize]=or(bits[o.bt as usize],c),12=>bits[o.bt as usize]=and(bits[o.bt as usize],not(c)),_=>{}}
  if c==0||matches!(o.k,0|7|9|14){continue;}if guard==1{o.c=u32::MAX;}out.push(o);
 }assert!(stack.is_empty());println!("STATIC_ZERO original_ops={} value_ops={}",p.ops.len(),out.len());Compact{ops:out,rng_count:0}
}
fn run(p:&Compact,q:&mut[u64],b:&mut[u64],stack:&mut[u64]){assert_eq!(unsafe{zero8_run(p.ops.as_ptr(),p.ops.len(),q.as_mut_ptr(),b.as_mut_ptr(),stack.as_mut_ptr(),stack.len()/8)},0);}
fn main(){assert!(std::is_x86_feature_detected!("avx512f"));let a:Vec<_>=std::env::args().collect();let ops=load_ops(&a[1]).unwrap();let(nq,nb,_,regs)=analyze_ops(ops.iter());let p=Compact::compile(&ops);let simplified=simplify(&p,&regs,nb as usize);
 let rows=fs::read_to_string(&a[2]).unwrap();let mut q=vec![0;nq as usize*8];let mut b=vec![0;nb as usize*8];
 for(index,row)in rows.lines().skip(1).take(512).enumerate(){let(j,lane)=(index/64,index%64);let f:Vec<_>=row.split('\t').collect();for(reg,col)in regs[..4].iter().zip([4,5,6,7]){let v=U256::from_str_radix(f[col],16).unwrap();for(i,w)in reg.iter().enumerate(){let at=match w{QubitOrBit::Qubit(id)=>&mut q[id.0 as usize*8+j],QubitOrBit::Bit(id)=>&mut b[id.0 as usize*8+j]};*at|=(v.bit(i)as u64)<<lane;}}}
 let mut stack=vec![0;4096*8];let(mut fullq,mut fullb)=(q.clone(),b.clone());run(&p,&mut fullq,&mut fullb,&mut stack);let(mut sq,mut sb)=(q.clone(),b.clone());run(&simplified,&mut sq,&mut sb,&mut stack);assert_eq!(fullq,sq);assert_eq!(fullb,sb);
 for j in 0..8{let mut rng=ZeroReader;let mut real=Simulator::new(nq as usize,nb as usize,&mut rng);for i in 0..nq as usize{real.qubits[i]=q[i*8+j];}for i in 0..nb as usize{real.bits[i]=b[i*8+j];}real.apply_iter(ops.iter());for i in 0..nq as usize{assert_eq!(real.qubits[i],sq[i*8+j],"q{i} batch{j}");}for i in 0..nb as usize{assert_eq!(real.bits[i],sb[i*8+j],"bit{i} batch{j}");}}
 println!("ZERO_VALUE_VERIFIED shots=512 qubits={nq} bits={nb} full_and_simplified_all_qubit_classical_words=true phase_not_queried=true rejection_disabled=true");
 for(name,code)in [("full",&p),("static_simplified",&simplified)]{let mut times=Vec::new();for _ in 0..7{let(mut qq,mut bb)=(q.clone(),b.clone());let start=Instant::now();run(code,&mut qq,&mut bb,&mut stack);times.push(start.elapsed().as_secs_f64());assert_eq!(qq,sq);assert_eq!(bb,sb);}println!("ZERO_BENCH mode={name} times={times:?} best_ms_per_batch={:.6}",times.iter().cloned().fold(f64::INFINITY,f64::min)*1000./8.);}
}
