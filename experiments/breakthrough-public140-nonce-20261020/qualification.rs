fn sha_check(path:&str,expected:&str){let o=std::process::Command::new("sha256sum").arg(path).output().unwrap();assert!(o.status.success());assert_eq!(String::from_utf8(o.stdout).unwrap().split_whitespace().next().unwrap(),expected);}
struct Words{v:Vec<u8>,at:usize}
impl XofReader for Words{fn read(&mut self,out:&mut[u8]){out.copy_from_slice(&self.v[self.at..self.at+out.len()]);self.at+=out.len();}}
fn qualify(ops:&[Op],p:&Compact,base:&Shake8,hash:&Shake256,tail:&[Op],curve:&FastCurveC,regs:&[Vec<QubitOrBit>],nq:usize,nb:usize){
 let mut prep=prepare8(base,hash,tail,[1,2,3,4,5,6,7,8],[true;8],curve,&());
 for x in &mut prep{assert!(x.packet.ensure(140,curve));assert_eq!(x.packet.next,NUM_TESTS);let mut full=ops[..ops.len()-TAIL].to_vec();full.extend(nonce_tail(tail,x.nonce));let mut reader=fiat_shamir_seed(&full);let mut keys=vec![0;NUM_TESTS*64];XofReader::read(&mut reader,&mut keys);assert_eq!(keys,x.packet.keys);let mut expected=[0;64];XofReader::read(&mut reader,&mut expected);let actual=x.ctx.copy().squeeze(64);assert_eq!(&expected,&actual[x.lane*64..(x.lane+1)*64]);}
 let packets:Vec<_>=prep.iter().map(|x|Packet{keys:x.packet.keys.clone(),next:x.packet.next,batches:x.packet.batches.clone()}).collect();
 for batch in [0,70,140]{let mut ctx=prep[0].ctx.copy();let rng=ctx.select([batch*p.rng_count;8],p.rng_count);let mut q=vec![0;nq*8];let mut b=vec![0;nb*8];let mut phase=[0;8];let mut stack=vec![0;4096*8];let mut used=0;
  for j in 0..8{for(lane,(t,o,e))in packets[j].batches[batch].iter().enumerate(){let off=(batch*64+lane)*64;let k1=U256::from_le_slice(&packets[j].keys[off..off+32]);let k2=U256::from_le_slice(&packets[j].keys[off+32..off+64]);let c=secp256k1();let tr=c.mul(c.gx,c.gy,k1);let or=c.mul(c.gx,c.gy,k2);assert_eq!(*t,tr);assert_eq!(*o,or);assert_eq!(*e,c.add(tr.0,tr.1,or.0,or.1));for(reg,value)in regs[..4].iter().zip([t.0,t.1,o.0,o.1]){for(i,w)in reg.iter().enumerate(){let v=(value.bit(i)as u64)<<lane;match w{QubitOrBit::Qubit(id)=>q[id.0 as usize*8+j]|=v,QubitOrBit::Bit(id)=>b[id.0 as usize*8+j]|=v}}}}}
  let q0=q.clone();let b0=b.clone();assert_eq!(unsafe{(exact_backend().run)(p.ops.as_ptr(),p.ops.len(),q.as_mut_ptr(),b.as_mut_ptr(),phase.as_mut_ptr(),rng.as_ptr(),p.rng_count,stack.as_mut_ptr(),4096,&mut used)},0);assert_eq!(used,p.rng_count);
  for j in 0..8{let mut reader=Words{v:(0..p.rng_count).flat_map(|i|rng[i*8+j].to_le_bytes()).collect(),at:0};let mut sim=Simulator::new(nq,nb,&mut reader);for i in 0..nq{sim.qubits[i]=q0[i*8+j];}for i in 0..nb{sim.bits[i]=b0[i*8+j];}let mut full=ops[..ops.len()-TAIL].to_vec();full.extend(nonce_tail(tail,j as u64+1));sim.apply_iter(full.iter());assert_eq!(sim.phase,phase[j]);for i in 0..nq{assert_eq!(sim.qubits[i],q[i*8+j]);}for i in 0..nb{assert_eq!(sim.bits[i],b[i*8+j]);}assert_eq!(reader.at,p.rng_count*8);}
  println!("QUALIFIED_FULL_STATE batch={batch} nonces=1..8 scalar_curve=true all_qubits_bits_phase_rng=true");
 }
 for n in [1,2,17,63]{let mask=(1u64<<n)-1;assert_eq!((1u64<<n)&mask,0);assert_ne!((1u64<<(n-1))&mask,0);}
 println!("QUALIFICATION_PASS unique_nonce_controls=8 scalar_full_state_batches=24 partial_masks=1,2,17,63 production_screens=0");
}
