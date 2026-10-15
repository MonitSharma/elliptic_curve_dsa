"""Memory-bounded replay of the SAME failing inputs using the protected simulator.

Chunks end only with an empty condition stack, so apply_iter's local stack
resets do not change semantics. Quantum/classical state, RNG and stats persist.
This is an independent diagnostic with fixed inputs, never a scored benchmark.
"""
from pathlib import Path
import hashlib,json,sys
lib,dest=map(Path,sys.argv[1:3]);(dest/'src').mkdir(parents=True,exist_ok=False)
program=r'''
use quantum_ecc::{circuit,sim};
use circuit::{Op,OperationType as K,QubitId,BitId,RegisterId,QubitOrBit,NO_QUBIT};
use alloy_primitives::U256;
use sha3::{Shake256,digest::{Update,ExtendableOutput}};
use std::io::{Read,BufReader};
fn decode(bytes:&[u8;56])->Op{
 let kinds=[K::Neg,K::Register,K::AppendToRegister,K::BitInvert,K::BitStore0,K::BitStore1,K::X,K::Z,K::CX,K::CZ,K::Swap,K::R,K::Hmr,K::CCX,K::CCZ,K::PushCondition,K::PopCondition,K::DebugPrint];
 let number=u32::from_le_bytes(bytes[..4].try_into().unwrap())as usize;assert!(number<18);
 let word=|i:usize|u64::from_le_bytes(bytes[8+8*i..16+8*i].try_into().unwrap());
 Op{kind:kinds[number],q_control2:QubitId(word(0)),q_control1:QubitId(word(1)),q_target:QubitId(word(2)),c_target:BitId(word(3)),c_condition:BitId(word(4)),r_target:RegisterId(word(5))}
}
fn main(){
 let args:Vec<_>=std::env::args().collect();let packets:serde_json::Value=serde_json::from_slice(&std::fs::read(&args[2]).unwrap()).unwrap();
 let chosen=[2726usize,2913,3532];let mut hash=Shake256::default();hash.update(b"q692-fixed-failed-input-independent-measurements-v1");let mut rng=hash.finalize_xof();let mut simulator=sim::Simulator::new(692,2_353_373,&mut rng);
 let mut regs:Vec<Vec<QubitOrBit>>=vec![vec![];4];let mut initialized=false;let mut depth=0usize;let mut maximum_depth=0usize;let mut chunks=0usize;let mut max_chunk=0usize;
 let mut file=BufReader::new(std::fs::File::open(&args[1]).unwrap());let mut header=[0u8;16];file.read_exact(&mut header).unwrap();assert_eq!(&header[..8],b"QECCOPSZ");let n=u64::from_le_bytes(header[8..].try_into().unwrap());let mut reader=zstd::stream::read::Decoder::new(file).unwrap();let mut raw=[0u8;56];let mut chunk=Vec::with_capacity(1<<20);
 for index in 0..n {
  reader.read_exact(&mut raw).unwrap();let op=decode(&raw);
  if op.kind==K::AppendToRegister{assert!(!initialized);let value=if op.q_target!=NO_QUBIT{QubitOrBit::Qubit(op.q_target)}else{QubitOrBit::Bit(op.c_target)};regs[op.r_target.0 as usize].push(value);}
  if op.kind==K::PushCondition{depth+=1;maximum_depth=maximum_depth.max(depth);}else if op.kind==K::PopCondition{assert!(depth>0);depth-=1;}
  chunk.push(op);assert!(chunk.len()<=16_777_216,"refuse unbounded conditional block");
  if depth==0&&(chunk.len()>=1<<20||index+1==n){
   if !initialized {
    assert!(regs.iter().all(|r|r.len()==256));
    for lane in 0..64{let packet=&packets["packets"][chosen[lane%3]];let read=|group:&str,coord:usize|U256::from_str_radix(packet[group][coord].as_str().unwrap(),16).unwrap();simulator.set_register(&regs[0],read("target",0),lane);simulator.set_register(&regs[1],read("target",1),lane);simulator.set_register(&regs[2],read("offset",0),lane);simulator.set_register(&regs[3],read("offset",1),lane);}
    initialized=true;
   }
   simulator.apply_iter(chunk.iter());max_chunk=max_chunk.max(chunk.len());chunk.clear();chunks+=1;
  }
 }
 assert_eq!(depth,0);assert!(chunk.is_empty());let mut extra=[0];assert_eq!(reader.read(&mut extra).unwrap(),0);
 let mut outputs=vec![];let mut mismatches=0;
 for lane in 0..64{let shot=chosen[lane%3];let packet=&packets["packets"][shot];let x=simulator.get_register(&regs[0],lane);let y=simulator.get_register(&regs[1],lane);let wantx=U256::from_str_radix(packet["expected"][0].as_str().unwrap(),16).unwrap();let wanty=U256::from_str_radix(packet["expected"][1].as_str().unwrap(),16).unwrap();let ok=x==wantx&&y==wanty;if !ok{mismatches+=1;}outputs.push(serde_json::json!({"lane":lane,"fixed_failed_shot":shot,"value_ok":ok,"actual":[format!("{:064x}",x),format!("{:064x}",y)],"phase_bit":simulator.phase>>lane&1}));}
 let output_ids:std::collections::HashSet<_>=regs[..2].iter().flatten().filter_map(|v|if let QubitOrBit::Qubit(q)=v{Some(q.0 as usize)}else{None}).collect();let garbage:Vec<_>=simulator.qubits.iter().enumerate().filter(|(i,v)|!output_ids.contains(i)&&**v!=0).map(|(i,v)|serde_json::json!({"qubit":i,"word":format!("{:016x}",v)})).collect();
 let report=serde_json::json!({"scope":"fixed failing v6 inputs, independent measurement seed, unchanged protected simulator; diagnostic only, not a score","ops_path":args[1],"physical_ops":n,"fixed_failed_shots":chosen,"lanes":64,"value_mismatch_lanes":mismatches,"phase_word":format!("{:016x}",simulator.phase),"ancilla_garbage":garbage,"chunks":chunks,"maximum_condition_depth":maximum_depth,"maximum_chunk_ops":max_chunk,"outputs":outputs});std::fs::write(&args[3],serde_json::to_vec_pretty(&report).unwrap()).unwrap();println!("FIXED_INPUT_REPLAY {}",report);
}
'''
(dest/'src/main.rs').write_text(program,encoding='utf8')
(dest/'Cargo.toml').write_text('[package]\nname="q692_fixed_input_replay"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nquantum_ecc={path='+json.dumps(lib.as_posix())+'}\nalloy-primitives="1.5"\nsha3="0.10"\nzstd="0.13"\nserde_json="1"\n',encoding='utf8')
(dest/'source-binding.json').write_text(json.dumps(dict(scope='unchanged protected simulator with balanced-stack chunk replay, fixed failed inputs only',library=str(lib),protected_simulator_sha256=hashlib.sha256((lib/'src/sim.rs').read_bytes()).hexdigest(),protected_circuit_sha256=hashlib.sha256((lib/'src/circuit.rs').read_bytes()).hexdigest(),program_sha256=hashlib.sha256((dest/'src/main.rs').read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf8')
