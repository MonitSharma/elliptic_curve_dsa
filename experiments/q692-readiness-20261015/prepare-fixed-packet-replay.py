"""All 9,024 existing failed-packet inputs, bounded chunks, protected simulator."""
from pathlib import Path
import hashlib,json,subprocess,sys
library,dest=map(Path,sys.argv[1:3]);root=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(root/'prepare-fixed-input-replay.py'),str(library),str(dest)],check=True)
p=dest/'src/main.rs';s=p.read_text(encoding='utf8');start=s.index('fn main(){')
s=s[:start]+r'''
fn main(){
 use circuit::NO_BIT;
 let args:Vec<_>=std::env::args().collect();let packets:serde_json::Value=serde_json::from_slice(&std::fs::read(&args[2]).unwrap()).unwrap();let packet=&packets["packets"];assert_eq!(packet.as_array().unwrap().len(),9024);
 let mut rngs:Vec<_>=(0..141usize).map(|batch|{let mut h=Shake256::default();h.update(b"q692-same-failed-packet-independent-measurements-v1");h.update(&(batch as u64).to_le_bytes());h.finalize_xof()}).collect();
 let mut simulators:Vec<_>=rngs.iter_mut().map(|rng|sim::Simulator::new(692,1,rng)).collect();
 let mut regs:Vec<Vec<QubitOrBit>>=vec![vec![];4];let mut initialized=false;let mut depth=0usize;let mut max_depth=0usize;let mut chunks=0usize;let mut max_chunk=0usize;let mut classical_bits=1usize;
 let mut file=BufReader::new(std::fs::File::open(&args[1]).unwrap());let mut header=[0u8;16];file.read_exact(&mut header).unwrap();assert_eq!(&header[..8],b"QECCOPSZ");let n=u64::from_le_bytes(header[8..].try_into().unwrap());let mut reader=zstd::stream::read::Decoder::new(file).unwrap();let mut raw=[0u8;56];let mut chunk=Vec::with_capacity(1<<20);
 for index in 0..n{
  reader.read_exact(&mut raw).unwrap();let op=decode(&raw);
  for bit in [op.c_target,op.c_condition]{if bit!=NO_BIT{classical_bits=classical_bits.max(bit.0 as usize+1);assert!(classical_bits<=8_388_608,"refuse excessive aggregate classical storage");}}
  if op.kind==K::AppendToRegister{assert!(!initialized);let value=if op.q_target!=NO_QUBIT{QubitOrBit::Qubit(op.q_target)}else{QubitOrBit::Bit(op.c_target)};regs[op.r_target.0 as usize].push(value);}
  if op.kind==K::PushCondition{depth+=1;max_depth=max_depth.max(depth);}else if op.kind==K::PopCondition{assert!(depth>0);depth-=1;}
  chunk.push(op);assert!(chunk.len()<=16_777_216,"refuse unbounded conditional block");
  if depth==0&&(chunk.len()>=1<<20||index+1==n){
   assert!(regs.iter().all(|r|r.len()==256));
   for(batch,simulator)in simulators.iter_mut().enumerate(){
    if classical_bits>simulator.bits.len(){simulator.bits.resize(classical_bits,0);simulator.num_bits=classical_bits;}
    if !initialized{for lane in 0..64{let case=&packet[batch*64+lane];let read=|group:&str,coord:usize|U256::from_str_radix(case[group][coord].as_str().unwrap(),16).unwrap();simulator.set_register(&regs[0],read("target",0),lane);simulator.set_register(&regs[1],read("target",1),lane);simulator.set_register(&regs[2],read("offset",0),lane);simulator.set_register(&regs[3],read("offset",1),lane);}}
    simulator.apply_iter(chunk.iter());
   }
   initialized=true;max_chunk=max_chunk.max(chunk.len());chunk.clear();chunks+=1;
   if chunks%16==0{println!("FIXED_PACKET_PROGRESS operations={}/{n} batches=141 classical_bits={classical_bits}",index+1);}
  }
 }
 assert_eq!(depth,0);assert!(chunk.is_empty());let mut extra=[0];assert_eq!(reader.read(&mut extra).unwrap(),0);
 let output_ids:std::collections::HashSet<_>=regs[..2].iter().flatten().filter_map(|v|if let QubitOrBit::Qubit(q)=v{Some(q.0 as usize)}else{None}).collect();let mut failed=vec![];let mut phases=vec![];let mut garbage=vec![];
 for(batch,simulator)in simulators.iter().enumerate(){
  if simulator.phase!=0{phases.push(serde_json::json!({"batch":batch,"word":format!("{:016x}",simulator.phase)}));}
  let anc:Vec<_>=simulator.qubits.iter().enumerate().filter(|(i,v)|!output_ids.contains(i)&&**v!=0).map(|(i,v)|serde_json::json!({"qubit":i,"word":format!("{:016x}",v)})).collect();if !anc.is_empty(){garbage.push(serde_json::json!({"batch":batch,"garbage":anc}));}
  for lane in 0..64{let shot=batch*64+lane;let x=simulator.get_register(&regs[0],lane);let y=simulator.get_register(&regs[1],lane);let expected=&packet[shot]["expected"];let wx=U256::from_str_radix(expected[0].as_str().unwrap(),16).unwrap();let wy=U256::from_str_radix(expected[1].as_str().unwrap(),16).unwrap();if x!=wx||y!=wy{failed.push(serde_json::json!({"fixed_shot":shot,"actual":[format!("{:064x}",x),format!("{:064x}",y)],"expected":expected}));}}
 }
 let pass=failed.is_empty()&&phases.is_empty()&&garbage.is_empty();let report=serde_json::json!({"scope":"all SAME 9024 v6 failed-packet inputs; unchanged protected simulator; independent fixed measurements; diagnostic only, not an official score","ops_path":args[1],"packet_path":args[2],"width":692,"physical_ops":n,"shots":9024,"value_failures":failed,"phase_failure_batches":phases,"ancilla_failure_batches":garbage,"classical_bits":classical_bits,"chunks":chunks,"maximum_chunk_ops":max_chunk,"maximum_condition_depth":max_depth,"passed":pass});
 std::fs::write(&args[3],serde_json::to_vec_pretty(&report).unwrap()).unwrap();println!("FIXED_PACKET_COMPLETE passed={pass} shots=9024 value_failures={} phase_batches={} ancilla_batches={}",failed.len(),phases.len(),garbage.len());if !pass{std::process::exit(1);}
}
'''
p.write_text(s,encoding='utf8');binding=json.loads((dest/'source-binding.json').read_text(encoding='utf8'));binding['program_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();binding['scope']='All 9024 same failed v6 inputs; balanced-stack streaming through 141 protected simulators; aggregate classical storage capped below 9 GiB; not a score.';(dest/'source-binding.json').write_text(json.dumps(binding,indent=2)+'\n',encoding='utf8')
