#![allow(dead_code,unused_imports)]
include!("prefix.rs");
include!("fast_sim_wide.rs");
include!("fast_curve_c.rs");
const DEFAULT_ZSTD_LEVEL:i32=3;
unsafe extern "C"{fn simd8_run(ops:*const CompactOp,n:usize,q:*mut u64,b:*mut u64,p:*mut u64,rng:*const u64,nr:usize,stack:*mut u64,cap:usize,used:*mut usize,toffoli:*mut u64)->i32;}
type Point=(U256,U256);
struct Batch{index:u64,ks:Vec<(U256,U256)>,points:Vec<(Point,Point,Point)>,skipped:u32,xof:sha3::Shake256Reader}
fn prepare_batch(label:&str,index:u64,curve:&FastCurveC,verify:bool)->Batch{
 let mut h=Shake256::default();h.update(CENSUS_DOMAIN);h.update(&(label.len()as u64).to_le_bytes());h.update(label.as_bytes());h.update(&index.to_le_bytes());let mut xof=h.finalize_xof();
 let(mut ks,mut points,mut skipped)=(Vec::new(),Vec::new(),0);
 while points.len()<64{
  let n=64-points.len();let mut scalars=Vec::with_capacity(n*2);
  for _ in 0..n*2{let mut raw=[0u8;32];XofReader::read(&mut xof,&mut raw);scalars.push(U256::from_le_bytes(raw));}
  for (i,(t,o,e)) in curve.points_with_sums(&scalars).into_iter().enumerate(){
   let pair=(scalars[2*i],scalars[2*i+1]);
   if verify{let c=secp256k1();assert_eq!(t,c.mul(c.gx,c.gy,pair.0));assert_eq!(o,c.mul(c.gx,c.gy,pair.1));assert_eq!(e,c.add(t.0,t.1,o.0,o.1));}
   if t.0==o.0||(t.0.is_zero()&&t.1.is_zero())||(o.0.is_zero()&&o.1.is_zero()){skipped+=1;continue;}
   ks.push(pair);points.push((t,o,e));
  }
 }
 Batch{index,ks,points,skipped,xof}
}
fn set(q:&mut[u64],b:&mut[u64],reg:&[QubitOrBit],value:U256,lane:usize,j:usize){for(i,w)in reg.iter().enumerate(){let word=match w{QubitOrBit::Qubit(id)=>&mut q[id.0 as usize*8+j],QubitOrBit::Bit(id)=>&mut b[id.0 as usize*8+j]};*word|=(value.bit(i)as u64)<<lane;}}
fn get(q:&[u64],b:&[u64],reg:&[QubitOrBit],lane:usize,j:usize)->U256{let mut v=U256::ZERO;for(i,w)in reg.iter().enumerate(){let word=match w{QubitOrBit::Qubit(id)=>q[id.0 as usize*8+j],QubitOrBit::Bit(id)=>b[id.0 as usize*8+j]};if word>>lane&1!=0{v|=U256::from(1)<<i;}}v}
fn main(){
 assert!(std::is_x86_feature_detected!("avx512f"));assert_eq!(std::mem::size_of::<CompactOp>(),16);
 let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),8,"OPS LABEL FIRST COUNT WORKERS OUT VERIFY_FIRST_BATCHES");
 let(first,count,workers,verify_first)=(a[3].parse::<u64>().unwrap(),a[4].parse::<usize>().unwrap(),a[5].parse::<usize>().unwrap(),a[7].parse::<usize>().unwrap());assert!(count>0&&workers>0&&workers<=16);
 let ops=Arc::new(load_ops(&a[1]).unwrap());let(nq,nb,_,regs)=analyze_ops(ops.iter());let p=Arc::new(Compact::compile(&ops));let regs=Arc::new(regs);let label=a[2].clone();FastCurveC::new(20);
 let next=Arc::new(AtomicUsize::new(0));let output=Arc::new(Mutex::new(Vec::<(u64,String)>::new()));let t0=std::time::Instant::now();let mut handles=Vec::new();
 for _ in 0..workers{
  let(ops,p,regs,label,next,output)=(ops.clone(),p.clone(),regs.clone(),label.clone(),next.clone(),output.clone());
  handles.push(std::thread::spawn(move||{
   let curve=FastCurveC::new(20);let mut rng=vec![0u64;p.rng_count*8];let mut stack=vec![0u64;4096*8];let mut q=vec![0;nq as usize*8];let mut b=vec![0;nb as usize*8];
   loop{let start=next.fetch_add(8,Ordering::SeqCst);if start>=count{break;}let n=(count-start).min(8);let mut batches=Vec::new();q.fill(0);b.fill(0);
    for j in 0..8{
     let offset=start+j.min(n-1);let verify=offset<verify_first;let batch=prepare_batch(&label,first+offset as u64,&curve,verify);
     for(lane,(t,o,_))in batch.points.iter().enumerate(){for(reg,v)in regs[..4].iter().zip([t.0,t.1,o.0,o.1]){set(&mut q,&mut b,reg,v,lane,j);}}
     let mut reader=batch.xof.clone();let mut raw=vec![0u8;p.rng_count*8];XofReader::read(&mut reader,&mut raw);for(i,word)in raw.chunks_exact(8).enumerate(){rng[i*8+j]=u64::from_le_bytes(word.try_into().unwrap());}batches.push(batch);
    }
    let(mut phase,mut toffoli,mut used)=([0u64;8],[0u64;8],0usize);assert_eq!(unsafe{simd8_run(p.ops.as_ptr(),p.ops.len(),q.as_mut_ptr(),b.as_mut_ptr(),phase.as_mut_ptr(),rng.as_ptr(),p.rng_count,stack.as_mut_ptr(),4096,&mut used,toffoli.as_mut_ptr())},0);assert_eq!(used,p.rng_count);
    for j in 0..n{let batch=&batches[j];
     if start+j<verify_first{let mut reader=batch.xof.clone();let mut s=Simulator::new(nq as usize,nb as usize,&mut reader);for(lane,(t,o,_))in batch.points.iter().enumerate(){for(reg,v)in regs[..4].iter().zip([t.0,t.1,o.0,o.1]){s.set_register(reg,v,lane);}}s.apply_iter(ops.iter());for i in 0..nq as usize{assert_eq!(q[i*8+j],s.qubits[i],"quantum wire{i} batch{}",batch.index);}for i in 0..nb as usize{assert_eq!(b[i*8+j],s.bits[i],"classical wire{i} batch{}",batch.index);}assert_eq!(phase[j],s.phase);assert_eq!(toffoli[j],s.stats.toffoli_gates);}
     let mut value=0u64;for(lane,(_,_,e))in batch.points.iter().enumerate(){if get(&q,&b,&regs[0],lane,j)!=e.0||get(&q,&b,&regs[1],lane,j)!=e.1{value|=1<<lane;}}
     let mut registered=vec![false;nq as usize];for reg in regs.iter(){for w in reg{if let QubitOrBit::Qubit(id)=w{registered[id.0 as usize]=true;}}}let dirty=(0..nq as usize).filter(|i|!registered[*i]).fold(0u64,|mask,i|mask|q[i*8+j]);let bad=value|phase[j]|dirty;
     let failures=(0..64).filter(|lane|bad>>lane&1!=0).map(|lane|format!("{{\"lane\":{lane},\"value\":{},\"phase\":{},\"dirty\":{},\"k1\":\"{}\",\"k2\":\"{}\"}}",value>>lane&1,phase[j]>>lane&1,dirty>>lane&1,hex(batch.ks[lane].0),hex(batch.ks[lane].1))).collect::<Vec<_>>().join(",");
     let line=format!("{{\"batch\":{},\"shots\":64,\"skipped\":{},\"toffoli\":{},\"value_shots\":{},\"phase_shots\":{},\"dirty_shots\":{},\"failures\":[{failures}]}}",batch.index,batch.skipped,toffoli[j],value.count_ones(),phase[j].count_ones(),dirty.count_ones());output.lock().unwrap().push((batch.index,line));
    }
   }
  }));
 }
 for h in handles{h.join().unwrap();}let mut rows=Arc::try_unwrap(output).unwrap().into_inner().unwrap();rows.sort();assert_eq!(rows.len(),count);let mut f=File::create(&a[6]).unwrap();for(_,line)in rows{writeln!(f,"{line}").unwrap();}
 eprintln!("SIMD_CENSUS_DONE batches={count} shots={} workers={workers} protected_full_state_and_T_verified_batches={} seconds={:.6} score=NONE",count*64,verify_first.min(count),t0.elapsed().as_secs_f64());
}
