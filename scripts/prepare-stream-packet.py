"""Export one fixed official packet without allocating a complete operation vector."""
import argparse
import hashlib
import json
from pathlib import Path

SCAN=r'''
fn streamed_seed(path:&str)->(sha3::Shake256Reader,u64,u64){
 let mut file=File::open(path).unwrap();let mut header=[0u8;16];file.read_exact(&mut header).unwrap();
 assert_eq!(&header[..8],b"QECCOPSZ");let n=u64::from_le_bytes(header[8..].try_into().unwrap());assert!(n<=4_000_000_000);
 let mut dec=zstd::stream::read::Decoder::new(BufReader::new(file)).unwrap();dec.window_log_max(27).unwrap();
 let mut h=Shake256::default();h.update(b"quantum_ecc-fiat-shamir-v2");h.update(&n.to_le_bytes());
 let mut raw=vec![0u8;56*65536];let mut canonical=Vec::with_capacity(49*65536);let mut left=n;let mut mr=0u64;
 while left>0{let count=left.min(65536)as usize;dec.read_exact(&mut raw[..count*56]).unwrap();canonical.clear();
  for rec in raw[..count*56].chunks_exact(56){let kind=u64::from_le_bytes(rec[..8].try_into().unwrap());assert!(kind<=17);if kind==11||kind==12{mr+=1;}canonical.push(kind as u8);canonical.extend_from_slice(&rec[8..]);}
  h.update(&canonical);left-=count as u64;
 }
 let mut tail=[0u8;1];assert_eq!(dec.read(&mut tail).unwrap(),0);
 eprintln!("STREAMED_SEED ops={n} reset_measurement_ops={mr} operation_vector_allocated=false");
 (h.finalize_xof(),n,mr)
}

fn main(){
 let a:Vec<String>=std::env::args().collect();assert_eq!(a.len(),4,"mode stream packet-output");
 let(mut seed,n,mr)=streamed_seed(&a[2]);
 if a[1]=="check-small"{assert!(n<20_000_000);let ops=load_ops(&a[2]).unwrap();let mut reference=fiat_shamir_seed(&ops);let mut x=[0u8;1024];let mut y=x;XofReader::read(&mut seed,&mut x);XofReader::read(&mut reference,&mut y);assert_eq!(x,y);println!("STREAMED_SEED_SMALL_VECTOR_REFERENCE_PASS ops={n} bytes=1024");return;}
 assert_eq!(a[1],"export");let curve=secp256k1();let mut out=File::create(&a[3]).unwrap();
 writeln!(out,"# index target_x target_y offset_x offset_y expected_x expected_y scalar1 scalar2").unwrap();let mut index=0usize;
 for _ in 0..NUM_TESTS{let mut rb=[[0u8;32];2];XofReader::read(&mut seed,&mut rb[0]);XofReader::read(&mut seed,&mut rb[1]);let k1=U256::from_le_bytes(rb[0]);let k2=U256::from_le_bytes(rb[1]);
  let t=curve.mul(curve.gx,curve.gy,k1);let o=curve.mul(curve.gx,curve.gy,k2);
  if t.0==o.0||(t.0.is_zero()&&t.1.is_zero())||(o.0.is_zero()&&o.1.is_zero()){continue;}
  let e=curve.add(t.0,t.1,o.0,o.1);writeln!(out,"{index}\t{:#x}\t{:#x}\t{:#x}\t{:#x}\t{:#x}\t{:#x}\t{:#x}\t{:#x}",t.0,t.1,o.0,o.1,e.0,e.1,k1,k2).unwrap();index+=1;
 }
 // Store only the exact selected batch's simulator transcript start, retaining
 // the unchanged official draw/skip rules and MR consumption on skipped gates.
 assert_eq!(index,9024);let batch=37u64;let mut left=batch*mr*8;let mut buffer=vec![0u8;1<<20];
 while left>0{let count=left.min(buffer.len()as u64)as usize;XofReader::read(&mut seed,&mut buffer[..count]);left-=count as u64;}
 let mut probe=[0u8;64];XofReader::read(&mut seed,&mut probe);std::fs::write(format!("{}.batch37-rng-prefix.bin",a[3]),probe).unwrap();
 println!("OFFICIAL_FIXED_PACKET_EXPORTED shots={index} ops={n} measurements_per_batch={mr} selected_batch=37 selected_shot=2379 score=NONE");
}
'''

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('protected',type=Path);a.add_argument('destination',type=Path)
    args=a.parse_args();base=args.protected.resolve();dest=args.destination.resolve()
    source=(base/'src/bin/eval_circuit.rs').read_text()
    prefix=source[source.index('use alloy_primitives'):source.index('const OPS_PATH')]
    prefix=prefix.replace('use std::fs::{File, OpenOptions};','use std::fs::File;').replace('use std::process::Command;','').replace('use std::time::{SystemTime, UNIX_EPOCH};','')
    constants=source[source.index('const MAGIC:'):source.index('// ─── Bounded ops.bin loader')]
    helpers=source[source.index('fn op_kind_from_u32'):source.index('// ─── Test runner')]
    (dest/'src').mkdir(parents=True,exist_ok=False)
    (dest/'src/main.rs').write_text(prefix+constants+helpers+SCAN,encoding='utf8')
    (dest/'Cargo.toml').write_text('[package]\nname="fixed_stream_packet"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nquantum_ecc={path='+json.dumps(base.as_posix())+'}\nalloy-primitives="1.5"\nsha3="0.10"\nzstd="0.13"\n[profile.release]\nopt-level=3\nlto="thin"\ncodegen-units=1\n',encoding='utf8')
    (dest/'rust-toolchain').write_bytes((base/'rust-toolchain').read_bytes())
    d={'protected_evaluator_sha256':hashlib.sha256((base/'src/bin/eval_circuit.rs').read_bytes()).hexdigest(),'external_main_sha256':hashlib.sha256((dest/'src/main.rs').read_bytes()).hexdigest(),'scope':'Exact fixed official packet from streamedcanonicalSHAKE256seed. Protected curve/draw/skip rules copied unchanged; small-vector seed reference mandatory. No nonce/packet search or score.'}
    (dest/'source-binding.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
    print(json.dumps(d))

if __name__=='__main__':main()
