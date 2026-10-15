// Benchmarks only. No universal RNG-independence certificate has been accepted.
// Every provisional witness is explicitly unauthoritative; no nonce is selected.
const PROOF_ACCEPTED:bool=false;
type ZeroRun=unsafe extern "C" fn(*const CompactOp,usize,*mut u64,*mut u64,*mut u64,usize)->i32;
struct ZeroProgram{p:Compact,run:ZeroRun}
fn sha_check(path:&str,expected:&str){let o=std::process::Command::new("sha256sum").arg(path).output().unwrap();assert!(o.status.success());let s=String::from_utf8(o.stdout).unwrap();assert_eq!(s.split_whitespace().next().unwrap(),expected);}
fn zero_program()->ZeroProgram{
 let root="/home/hclau/ecdsa_research/zero-mr-slice-20261016";
 let path=format!("{root}/tip.compact16.bin");sha_check(&path,"812f706d2edd7e821ff6c5f72db5e7e65b3f9756f562d99c1d0e1fceb007daf0");
 let bytes=std::fs::read(path).unwrap();assert_eq!(bytes.len()%16,0);let mut ops=Vec::new();
 for r in bytes.chunks_exact(16){ops.push(CompactOp{a:u16::from_le_bytes(r[0..2].try_into().unwrap()),b:u16::from_le_bytes(r[2..4].try_into().unwrap()),t:u16::from_le_bytes(r[4..6].try_into().unwrap()),k:r[6],pad:r[7],c:u32::from_le_bytes(r[8..12].try_into().unwrap()),bt:u32::from_le_bytes(r[12..16].try_into().unwrap())});}
 let lib=format!("{root}/libzero8_slice.so");sha_check(&lib,"84b73bcdee01bb537d0320f9985a682758d1076860455ad382a2ae175690ea82");let run=unsafe{let s=CString::new(lib).unwrap();let h=dlopen(s.as_ptr(),2);assert!(!h.is_null());let p=dlsym(h,b"zero8_run\0".as_ptr().cast());assert!(!p.is_null());std::mem::transmute::<*mut c_void,ZeroRun>(p)};
 ZeroProgram{p:Compact{ops,rng_count:0},run}
}
struct CandidatePacket{packet:Packet,nonce:u64,scan_batch:usize,candidates:Vec<(usize,usize)>,cursor:usize,attempts:usize}
impl CandidatePacket{
 fn next_witness(&mut self,curve:&FastCurveC,model:&RailAdvisory)->Option<(usize,usize)>{
  loop{if self.cursor<self.candidates.len(){let r=self.candidates[self.cursor];self.cursor+=1;self.attempts+=1;return Some(r);}
   let batch=self.scan_batch;if !self.packet.ensure(batch,curve){return None;}self.scan_batch+=1;
   self.candidates=rail_flags(model,&self.packet.batches[batch]).iter().enumerate().filter_map(|(i,f)|(*f!=0).then_some((batch,i))).collect();self.cursor=0;
  }
 }
}
fn prepare_packets(base:&Shake8,hash:&Shake256,tail:&[Op],nonces:[u64;8],valid:[bool;8])->Vec<CandidatePacket>{
 let mut encoded=Vec::with_capacity(TAIL*49*8);for nonce in nonces{for op in nonce_tail(tail,nonce){encoded.extend_from_slice(&record49(&op));}}
 let mut ctx=base.copy();ctx.different(&encoded,TAIL*49);ctx.finalize();let keys=ctx.squeeze(NUM_TESTS*64);
 for j in 0..8{let mut h=hash.clone();h.update(&encoded[j*TAIL*49..(j+1)*TAIL*49]);let mut check=[0u8;64];XofReader::read(&mut h.finalize_xof(),&mut check);assert_eq!(&check,&keys[j*NUM_TESTS*64..j*NUM_TESTS*64+64]);}
 (0..8).filter(|j|valid[*j]).map(|j|CandidatePacket{packet:Packet{keys:keys[j*NUM_TESTS*64..(j+1)*NUM_TESTS*64].to_vec(),next:0,batches:Vec::new()},nonce:nonces[j],scan_batch:0,candidates:Vec::new(),cursor:0,attempts:0}).collect()
}
struct ZeroReader;impl XofReader for ZeroReader{fn read(&mut self,out:&mut[u8]){out.fill(0);}}
fn packed_values(program:&ZeroProgram,points:&[PointTriple],regs:&[Vec<QubitOrBit>],nq:usize,nb:usize,shadow:Option<&[Op]>)->Vec<bool>{
 assert!(points.len()<=512);let mut q=vec![0u64;nq*8];let mut b=vec![0u64;nb*8];let mut stack=vec![0u64;4096*8];
 for(index,(t,o,_))in points.iter().enumerate(){let(j,lane)=(index/64,index%64);for(reg,value)in regs[..4].iter().zip([t.0,t.1,o.0,o.1]){for(i,wire)in reg.iter().enumerate(){let v=(value.bit(i)as u64)<<lane;match wire{QubitOrBit::Qubit(id)=>q[id.0 as usize*8+j]|=v,QubitOrBit::Bit(id)=>b[id.0 as usize*8+j]|=v}}}}
 let initial=shadow.map(|_|(q.clone(),b.clone()));assert_eq!(unsafe{(program.run)(program.p.ops.as_ptr(),program.p.ops.len(),q.as_mut_ptr(),b.as_mut_ptr(),stack.as_mut_ptr(),4096)},0);
 if let Some(ops)=shadow{let(iq,ib)=initial.unwrap();for j in 0..8{let mut zero=ZeroReader;let mut sim=Simulator::new(nq,nb,&mut zero);for i in 0..nq{sim.qubits[i]=iq[i*8+j];}for i in 0..nb{sim.bits[i]=ib[i*8+j];}sim.apply_iter(ops.iter());for reg in &regs[..2]{for w in reg{let(a,z)=match w{QubitOrBit::Qubit(id)=>(sim.qubits[id.0 as usize],q[id.0 as usize*8+j]),QubitOrBit::Bit(id)=>(sim.bits[id.0 as usize],b[id.0 as usize*8+j])};assert_eq!(a,z,"packed sliced output differs from protected fixed-zero simulation");}}}}
 points.iter().enumerate().map(|(index,(_,_,expected))|{let(j,lane)=(index/64,index%64);let mut wrong=false;for(reg,value)in regs[..2].iter().zip([expected.0,expected.1]){for(i,wire)in reg.iter().enumerate(){let raw=match wire{QubitOrBit::Qubit(id)=>q[id.0 as usize*8+j],QubitOrBit::Bit(id)=>b[id.0 as usize*8+j]};wrong|=((raw>>lane)&1)!=(value.bit(i)as u64);}}wrong}).collect()
}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),8,"ORIGINAL_OPS FIRST COUNT THREADS OUT MODEL_SOURCE LOOKAHEAD");assert!(!PROOF_ACCEPTED,"benchmark gate must remain disabled until separately reviewed certificate");
 sha_check(&a[1],"2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e");let ops=load_ops(&a[1]).unwrap();let n=ops.len();let tail=&ops[n-TAIL..];for pair in tail.chunks_exact(2){assert_eq!(pair[0],pair[1]);assert_eq!(pair[0].kind,OperationType::X);}
 let(nq,nb,_,regs)=analyze_ops(ops.iter());let(nq,nb)=(nq as usize,nb as usize);let first=a[2].parse::<u64>().unwrap();let count=a[3].parse::<usize>().unwrap();let threads=a[4].parse::<usize>().unwrap();let lookahead=a[7].parse::<usize>().unwrap();assert!(count<=4096&&threads>0&&threads<=16&&lookahead>0&&lookahead<=4096);
 let mut base=Shake8::new();let mut hash=Shake256::default();for bytes in [b"quantum_ecc-fiat-shamir-v2".as_slice(),&(n as u64).to_le_bytes()]{base.same(bytes);hash.update(bytes);}let mut encoded=Vec::new();for op in &ops[..n-TAIL]{encoded.extend_from_slice(&record49(op));if encoded.len()>=49*32768{base.same(&encoded);hash.update(&encoded);encoded.clear();}}if !encoded.is_empty(){base.same(&encoded);hash.update(&encoded);}
 let curve=FastCurveC::new(20);let model=RailAdvisory::new(&a[6]);let program=zero_program();let shadow=std::env::var_os("PACKED_ZERO_SHADOW").is_some();let out=Mutex::new(File::create(&a[5]).unwrap());let start=std::time::Instant::now();let mut prepare_secs=0.0;let mut value_secs=0.0;let mut fallback_secs=0.0;let mut total_witnesses=0;
 for window in (0..count).step_by(lookahead){let stop=(window+lookahead).min(count);let next=AtomicUsize::new(window);let pending=Mutex::new(Vec::new());let t=std::time::Instant::now();std::thread::scope(|scope|{for _ in 0..threads{scope.spawn(||loop{let ix=next.fetch_add(8,Ordering::SeqCst);if ix>=stop{break;}let nonces=std::array::from_fn(|j|first+(ix+j).min(stop-1)as u64);let valid=std::array::from_fn(|j|ix+j<stop);for mut packet in prepare_packets(&base,&hash,tail,nonces,valid){let witness=packet.next_witness(&curve,&model);pending.lock().unwrap().push((packet,witness));}});}});prepare_secs+=t.elapsed().as_secs_f64();let mut pending=pending.into_inner().unwrap();
  while !pending.is_empty(){let mut points=Vec::new();let mut owners=Vec::new();let mut done=Vec::new();for(index,(packet,witness))in pending.iter().enumerate(){if let Some((batch,shot))=*witness{points.push(packet.packet.batches[batch][shot]);owners.push(index);}else{done.push(index);}}
   let t=std::time::Instant::now();let mut wrong=vec![false;points.len()];for(chunk,outchunk)in points.chunks(512).zip(wrong.chunks_mut(512)){let result=packed_values(&program,chunk,&regs,nq,nb,shadow.then_some(ops.as_slice()));outchunk.copy_from_slice(&result);}value_secs+=t.elapsed().as_secs_f64();total_witnesses+=points.len();let mut remove=vec![false;pending.len()];
   for(index,bad)in owners.into_iter().zip(wrong){if bad{let(packet,witness)=&pending[index];let(batch,shot)=witness.unwrap();writeln!(out.lock().unwrap(),"{}",serde_json::json!({"nonce":packet.nonce,"provisional_wrong_value":true,"authoritative_rejection":false,"proof_accepted":false,"witness_batch":batch,"witness_shot":shot,"witnesses_tried":packet.attempts})).unwrap();remove[index]=true;}}
   for index in done{let t=std::time::Instant::now();let packet=&pending[index].0;let mut actual=ops[..n-TAIL].to_vec();actual.extend(nonce_tail(tail,packet.nonce));let result=run_tests(&actual,&regs,nq as u64,nb as u64,fiat_shamir_seed(&actual),NUM_TESTS);fallback_secs+=t.elapsed().as_secs_f64();writeln!(out.lock().unwrap(),"{}",serde_json::json!({"nonce":packet.nonce,"provisional_wrong_value":false,"original_full_fallback_pass":result.ok,"authoritative_rejection":false,"proof_accepted":false,"witnesses_tried":packet.attempts,"protected_shots":result.n_shots})).unwrap();remove[index]=true;}
   let queue=Mutex::new(pending.into_iter().zip(remove).filter_map(|(v,r)|(!r).then_some(v)).collect::<std::collections::VecDeque<_>>());let updated=Mutex::new(Vec::new());let t=std::time::Instant::now();std::thread::scope(|scope|{for _ in 0..threads{scope.spawn(||loop{let item=queue.lock().unwrap().pop_front();let Some((mut packet,_))=item else{break};let witness=packet.next_witness(&curve,&model);updated.lock().unwrap().push((packet,witness));});}});prepare_secs+=t.elapsed().as_secs_f64();pending=updated.into_inner().unwrap();
  }
 }
 println!("PACKED_WITNESS_BENCH first={first} count={count} threads={threads} lookahead={lookahead} wall_seconds={:.6} preparation_seconds={prepare_secs:.6} value_seconds={value_secs:.6} fallback_seconds={fallback_secs:.6} witnesses={total_witnesses} PROOF_ACCEPTED=false AUTHORITATIVE_REJECTIONS=0 NONCE_SELECTED=false",start.elapsed().as_secs_f64());
}
