#![allow(dead_code,unused_imports)]
include!("prefix.rs");
include!("fast_sim.rs");
include!("fiat8.rs");
use std::{fs,path::Path,io::BufWriter,time::Instant};
const DEFAULT_ZSTD_LEVEL:i32=3;
#[derive(Clone,Copy,Debug,PartialEq,Eq)] #[repr(C,align(64))]
struct Row([u64;8]);
#[derive(Clone,PartialEq,Eq)] struct State {q:Vec<Row>,b:Vec<Row>,p:Row}
extern "C" {fn simd8_run(ops:*const CompactOp,n:usize,q:*mut u64,b:*mut u64,p:*mut u64,rng:*const u64,nr:usize,stack:*mut u64,cap:usize,used:*mut usize)->i32;}
extern "C" {fn simd8_fast_run(ops:*const CompactOp,n:usize,q:*mut u64,b:*mut u64,p:*mut u64,rng:*const u64,nr:usize,stack:*mut u64,cap:usize,used:*mut usize)->i32;}
fn specialize(p:&Compact)->Compact{let mut ops=p.ops.clone();let mut depth=0;let mut n=0;for o in &mut ops {if o.k==15{depth+=1;}else if o.k==16{depth-=1;}else if depth==0&&o.c==u16::MAX{o.k+=32;n+=1;}}assert_eq!(depth,0);println!("SPECIALIZED unconditional_ops={n} total_ops={}",ops.len());Compact{ops,rng_count:p.rng_count}}
fn run_fast(p:&Compact,s:&mut State,rng:&[Row],stack:&mut[Row])->Result<usize,i32>{let mut used=0;let e=unsafe{simd8_fast_run(p.ops.as_ptr(),p.ops.len(),s.q.as_mut_ptr().cast(),s.b.as_mut_ptr().cast(),s.p.0.as_mut_ptr(),rng.as_ptr().cast(),rng.len(),stack.as_mut_ptr().cast(),stack.len(),&mut used)};if e==0{Ok(used)}else{Err(e)}}
fn workspace(p:&Compact)->Vec<Row>{
 let mut depth=0usize;let mut cap=0;for o in &p.ops {if o.k==15 {depth+=1;cap=cap.max(depth);}else if o.k==16 {depth=depth.checked_sub(1).unwrap();}}
 assert_eq!(depth,0);vec![Row([0;8]);cap]
}
fn run_prepared(p:&Compact,s:&mut State,rng:&[Row],stack:&mut[Row])->Result<usize,i32>{
 let mut used=0;
 let e=unsafe{simd8_run(p.ops.as_ptr(),p.ops.len(),s.q.as_mut_ptr().cast(),s.b.as_mut_ptr().cast(),s.p.0.as_mut_ptr(),rng.as_ptr().cast(),rng.len(),stack.as_mut_ptr().cast(),stack.len(),&mut used)};
 if e==0{Ok(used)}else{Err(e)}
}
fn run(p:&Compact,s:&mut State,rng:&[Row])->Result<usize,i32>{run_prepared(p,s,rng,&mut workspace(p))}
fn reader(seed:usize)->sha3::Shake256Reader{let mut h=Shake256::default();h.update(b"simd8-exact-backend-v1");h.update(&(seed as u64).to_le_bytes());h.finalize_xof()}
struct CountRng {inner:sha3::Shake256Reader,bytes:usize}
impl XofReader for CountRng{fn read(&mut self,out:&mut[u8]){self.bytes+=out.len();XofReader::read(&mut self.inner,out);}}
fn matrix(n:usize,seeds:[usize;8])->(Vec<Row>,f64,f64){
 let t=Instant::now();let mut data=Vec::new();for seed in seeds {let mut v=vec![0u8;n*8];XofReader::read(&mut reader(seed),&mut v);data.push(v);}let fill=t.elapsed().as_secs_f64();
 let t=Instant::now();let mut m=vec![Row([0;8]);n];for j in 0..8 {for i in 0..n {m[i].0[j]=u64::from_le_bytes(data[j][8*i..8*i+8].try_into().unwrap());}}
 (m,fill,t.elapsed().as_secs_f64())
}
fn compare(ops:&[Op],initial:&State,got:&State,seeds:[usize;8],nr:usize,tag:&str)->f64{
 let t=Instant::now();for j in 0..8 {let mut r=CountRng{inner:reader(seeds[j]),bytes:0};let mut s=Simulator::new(initial.q.len(),initial.b.len(),&mut r);
 s.phase=initial.p.0[j];for(i,x)in s.qubits.iter_mut().enumerate(){*x=initial.q[i].0[j];}for(i,x)in s.bits.iter_mut().enumerate(){*x=initial.b[i].0[j];}
 s.apply_iter(ops.iter());for(i,x)in s.qubits.iter().enumerate(){assert_eq!(*x,got.q[i].0[j],"{tag} qubit={i} batch={j}");}for(i,x)in s.bits.iter().enumerate(){assert_eq!(*x,got.b[i].0[j],"{tag} bit={i} batch={j}");}assert_eq!(s.phase,got.p.0[j],"{tag} phase batch={j}");drop(s);assert_eq!(r.bytes,nr*8,"RNG draw count {tag} batch={j}");
 }let dt=t.elapsed().as_secs_f64();println!("PAIRED_FULL tag={tag} batches=8 shots=512 qubits={} bits={} phase=true rng_bytes_per_batch={} protected_seconds={dt:.6}",initial.q.len(),initial.b.len(),nr*8);dt
}
fn rawop(k:OperationType,t:u64,a:u64,b:u64,bt:u64,c:u64)->Op {Op{kind:k,q_target:QubitId(t),q_control1:QubitId(a),q_control2:QubitId(b),c_target:BitId(bt),c_condition:BitId(c),r_target:RegisterId(u64::MAX)}}
fn fixtures(){
 use OperationType::*;let z=u64::MAX;
 let ops=vec![rawop(Neg,z,z,z,z,z),rawop(BitInvert,z,z,z,0,z),rawop(BitStore0,z,z,z,1,0),rawop(BitStore1,z,z,z,2,0),rawop(PushCondition,z,z,z,z,0),rawop(BitInvert,z,z,z,0,z),rawop(PushCondition,z,z,z,z,2),rawop(X,0,z,z,z,1),rawop(Z,1,z,z,z,z),rawop(CX,2,0,z,z,z),rawop(CZ,3,1,z,z,z),rawop(Swap,0,1,z,z,z),rawop(CCX,3,1,2,z,z),rawop(CCZ,3,1,2,z,2),rawop(R,2,z,z,z,1),rawop(Hmr,3,z,z,3,1),rawop(PopCondition,z,z,z,z,z),rawop(PopCondition,z,z,z,z,z),rawop(Hmr,0,z,z,1,z),rawop(R,1,z,z,z,z)];
 for o in &ops{o.validate();}let p=Compact::compile(&ops);let seeds=[1,2,3,4,5,6,7,8];
 let mut init=State{q:vec![Row([0;8]);4],b:vec![Row([0;8]);4],p:Row([0;8])};let(mut m,_,_)=matrix(p.rng_count,seeds);
 for i in 0..4 {for j in 0..8 {init.q[i].0[j]=0x9e3779b97f4a7c15u64.wrapping_mul((1+i*8+j)as u64);init.b[i].0[j]=0x94d049bb133111ebu64.wrapping_mul((3+i*8+j)as u64);}}init.p.0=[0xaaaa5555cccc3333;8];
 let mut got=init.clone();assert_eq!(run(&p,&mut got,&m),Ok(p.rng_count));compare(&ops,&init,&got,seeds,p.rng_count,"fixture-all-opcodes-nested-snapshot");
 // Positive fixture has inactive MR bits followed by active MR, so consuming
 // only active random rows changes subsequent classical outcomes and phase.
 let mut skipped=m.clone();skipped.rotate_left(1);let mut bad=init.clone();run(&p,&mut bad,&skipped).unwrap();assert!(bad!=got,"RNG-position negative fixture failed to detect corruption");
 let mut bad=got.clone();bad.p.0[7]^=1;assert!(bad!=got,"phase negative fixture");
 assert_eq!(run(&p,&mut init.clone(),&m[..m.len()-1]),Err(1));
 let mut badp=Compact{ops:vec![CompactOp{a:0,b:0,t:0,c:0,bt:0,k:16}],rng_count:0};let mut used=0;let e=unsafe{simd8_run(badp.ops.as_ptr(),1,init.q.as_mut_ptr().cast(),init.b.as_mut_ptr().cast(),init.p.0.as_mut_ptr(),m.as_ptr().cast(),0,std::ptr::null_mut(),0,&mut used)};assert_eq!(e,3);
 println!("FIXTURES_PASS opcodes=15 nested_snapshot=true inactive_MR_draws=true arbitrary_dirty_state=true negative_rng=true negative_phase=true short_rng=true stack_underflow=true");
 // Enumerate all 2^(4 quantum + 4 classical + 4 measurement) assignments.
 // Initial phase is arbitrary and is carried through unchanged except XOR.
 struct Fixed{words:Vec<u8>,at:usize}impl XofReader for Fixed{fn read(&mut self,o:&mut[u8]){o.copy_from_slice(&self.words[self.at..self.at+o.len()]);self.at+=o.len();}}
 for group in 0..8{let mut initial=State{q:vec![Row([0;8]);4],b:vec![Row([0;8]);4],p:Row([0;8])};let mut rm=vec![Row([0;8]);4];for j in 0..8{for lane in 0..64{let assignment=group*512+j*64+lane;for k in 0..4{initial.q[k].0[j]|=(((assignment>>k)&1)as u64)<<lane;initial.b[k].0[j]|=(((assignment>>(4+k))&1)as u64)<<lane;rm[k].0[j]|=(((assignment>>(8+k))&1)as u64)<<lane;}initial.p.0[j]|=(((assignment.count_ones()as usize)&1)as u64)<<lane;}}
  let mut actual=initial.clone();run(&p,&mut actual,&rm).unwrap();let mut fast=initial.clone();run_fast(&specialize(&p),&mut fast,&rm,&mut workspace(&p)).unwrap();assert!(fast==actual);for j in 0..8{let mut rr=Fixed{words:rm.iter().flat_map(|r|r.0[j].to_le_bytes()).collect(),at:0};let mut ss=Simulator::new(4,4,&mut rr);ss.phase=initial.p.0[j];for k in 0..4{ss.qubits[k]=initial.q[k].0[j];ss.bits[k]=initial.b[k].0[j];}ss.apply_iter(ops.iter());for k in 0..4{assert_eq!(ss.qubits[k],actual.q[k].0[j]);assert_eq!(ss.bits[k],actual.b[k].0[j]);}assert_eq!(ss.phase,actual.p.0[j]);drop(ss);assert_eq!(rr.at,32);}
 }println!("EXHAUSTIVE_FIXTURE_PASS assignments=4096 quantum_inputs=4 classical_inputs=4 measurement_outcomes=4 all_phase=true");
}
fn full(path:&str,points:&str,reps:usize){
 let ops=load_ops(path).unwrap();let(nq,nb,_,regs)=analyze_ops(ops.iter());let p=Compact::compile(&ops);let seeds=[100,101,102,103,104,105,106,107];
 let rows:Vec<[U256;6]>=fs::read_to_string(points).unwrap().lines().filter(|l|!l.trim().is_empty()).map(|l|l.split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect::<Vec<_>>().try_into().unwrap()).collect();assert!(rows.len()>=256);
 let mut init=State{q:vec![Row([0;8]);nq as usize],b:vec![Row([0;8]);nb as usize],p:Row([0;8])};
 for j in 0..8 {let mut r=reader(0);let mut s=Simulator::new(nq as usize,nb as usize,&mut r);for lane in 0..64{for k in 0..4{s.set_register(&regs[k],rows[(j%4)*64+lane][k],lane);}}for i in 0..nq as usize{init.q[i].0[j]=s.qubits[i];}for i in 0..nb as usize{init.b[i].0[j]=s.bits[i];}}
 let(m,fill,trans)=matrix(p.rng_count,seeds);println!("RNG_TIMING scalar_shake8_seconds={fill:.6} transpose_seconds={trans:.6} matrix_bytes={}",m.len()*64);
 let mut ws=workspace(&p);let mut best=f64::INFINITY;let mut result=init.clone();for rep in 0..reps {let mut s=init.clone();let t=Instant::now();let used=run_prepared(&p,&mut s,&m,&mut ws).unwrap();let dt=t.elapsed().as_secs_f64();assert_eq!(used,p.rng_count);best=best.min(dt);println!("KERNEL_TIMING rep={rep} eight_batch_seconds={dt:.6} ms_per_batch={:.4}",dt*125.0);result=s;}
 let prot=compare(&ops,&init,&result,seeds,p.rng_count,"frozen4b2-full-stream");
 let t=Instant::now();for j in 0..8 {let mut r=reader(seeds[j]);let mut s=FastSimulator::new(nq as usize,nb as usize,&mut r);for i in 0..nq as usize{s.qubits[i]=init.q[i].0[j];}for i in 0..nb as usize{s.bits[i]=init.b[i].0[j];}s.apply(&p);assert_eq!(s.phase,result.p.0[j]);for i in 0..nq as usize{assert_eq!(s.qubits[i],result.q[i].0[j]);}for i in 0..nb as usize{assert_eq!(s.bits[i],result.b[i].0[j]);}}let scalar=t.elapsed().as_secs_f64();
 println!("BENCH compact8_with_rng_seconds={scalar:.6} simd8_kernel_seconds={best:.6} simd8_with_scalar_rng_seconds={:.6} kernel_speedup_vs_compact_with_rng={:.4} end_to_end_speedup={:.4} protected8_seconds={prot:.6} score=NONE nonce_search=false",best+fill+trans,scalar/best,scalar/(best+fill+trans));
}
fn main(){assert!(std::is_x86_feature_detected!("avx512f"));assert!(std::is_x86_feature_detected!("avx512dq"));assert!(std::is_x86_feature_detected!("avx512bw"));assert!(std::is_x86_feature_detected!("avx512vl"));assert_eq!(std::mem::size_of::<CompactOp>(),12);println!("CPU_PREFLIGHT avx512f=true avx512dq=true avx512bw=true avx512vl=true CompactOp_bytes=12 Row_bytes={}",std::mem::size_of::<Row>());fixtures();let a:Vec<String>=std::env::args().collect();if a.len()>1{if a[1]=="@fiat"{fiat8(&a[2]);}else{full(&a[1],&a[2],a.get(3).map(|v|v.parse().unwrap()).unwrap_or(3));}}}
