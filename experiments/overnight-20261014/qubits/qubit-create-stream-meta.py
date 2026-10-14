"""External bounded-memory stream metadata; never modifies the evaluator."""
from pathlib import Path
import sys
base,dest=map(lambda s:Path(s).resolve(),sys.argv[1:3]);dest.joinpath('src').mkdir(parents=True,exist_ok=True)
dest.joinpath('Cargo.toml').write_text(f'''[package]
name = "qubit_stream_resource_meta"
version = "0.1.0"
edition = "2021"
[dependencies]
quantum_ecc = {{ path = "{base.as_posix()}" }}
zstd = "0.13"
serde_json = "1"
''')
dest.joinpath('src/main.rs').write_text(r'''
use quantum_ecc::circuit::Op;
use std::{fs::File,io::{Read,BufReader},mem::{size_of,align_of}};
fn main(){
 let a:Vec<String>=std::env::args().collect();
 let sample=Vec::<Op>::with_capacity(17);
 if a.len()==1{println!("{}",serde_json::json!({"scope":"metadata only, no score","sizeof_op":size_of::<Op>(),"alignof_op":align_of::<Op>(),"sample_requested_capacity":17,"sample_actual_capacity":sample.capacity()}));return;}
 let mut file=File::open(&a[1]).unwrap();let compressed=file.metadata().unwrap().len();let mut header=[0u8;16];file.read_exact(&mut header).unwrap();assert_eq!(&header[..8],b"QECCOPSZ");let n=u64::from_le_bytes(header[8..].try_into().unwrap());assert!(n<=4_000_000_000);
 let measured_loader_capacity=if a.iter().any(|x|x=="--reserve"){let v=Vec::<Op>::with_capacity(usize::try_from(n).unwrap());let c=v.capacity();drop(v);Some(c)}else{None};
 let mut decoder=zstd::stream::read::Decoder::new(BufReader::new(file)).unwrap();decoder.window_log_max(31).unwrap();
 let mut buffer=vec![0u8;56*65536];let(mut left,mut nq,mut nb,mut nr)=(n,0u64,0u64,0u64);let mut counts=[0u64;18];
 while left>0{let take=left.min(65536)as usize;decoder.read_exact(&mut buffer[..take*56]).unwrap();for rec in buffer[..take*56].chunks_exact(56){let kind=u32::from_le_bytes(rec[..4].try_into().unwrap())as usize;assert!(kind<18);counts[kind]+=1;assert_eq!(&rec[4..8],&[0u8;4]);let field=|o:usize|u64::from_le_bytes(rec[o..o+8].try_into().unwrap());for o in [8,16,24]{let q=field(o);if q!=u64::MAX{nq=nq.max(q.checked_add(1).unwrap());}}for o in [32,40]{let b=field(o);if b!=u64::MAX{nb=nb.max(b.checked_add(1).unwrap());}}let r=field(48);if r!=u64::MAX{nr=nr.max(r.checked_add(1).unwrap());}}left-=take as u64;}
 let mut trailing=[0u8;1];assert_eq!(decoder.read(&mut trailing).unwrap(),0);
 println!("{}",serde_json::json!({"scope":"stream diagnostic metadata, not a score","ops":n,"referenced_qubits":nq,"referenced_bits":nb,"referenced_registers":nr,"sizeof_op":size_of::<Op>(),"alignof_op":align_of::<Op>(),"protected_loader_requested_capacity":n,"measured_loader_vec_capacity":measured_loader_capacity,"op_vec_bytes":n*size_of::<Op>()as u64,"compressed_bytes":compressed,"emitted_counts_by_kind":counts,"peak_method":"same maximum referenced IDs as protected circuit::analyze_ops; no operation vector retained"}));
}
''')
