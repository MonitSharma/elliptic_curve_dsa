"""Separate native replay of exact depth-zero prefixes; protected files untouched."""
from pathlib import Path
import sys
base=Path(sys.argv[1]).resolve();dest=Path(sys.argv[2]).resolve();s=(base/'src/bin/eval_circuit.rs').read_text()
prefix=s[s.index('use alloy_primitives'):s.index('const OPS_PATH')].replace('use std::fs::{File, OpenOptions};','use std::fs::File;').replace('use std::process::Command;','').replace('use std::time::{SystemTime, UNIX_EPOCH};','')
const=s[s.index('const MAGIC:'):s.index('// ─── Bounded ops.bin loader')];helpers=s[s.index('fn op_kind_from_u32'):s.index('// ─── Test runner')]
main=r'''
fn main(){let a:Vec<_>=std::env::args().collect();let ops=load_ops(&a[1]).unwrap();let(nq,nb,_,regs)=analyze_ops(ops.iter());let curve=secp256k1();
 let text=std::fs::read_to_string(&a[2]).unwrap();let records:Vec<_>=text.lines().filter(|s|!s.starts_with('#')).take(64).collect();
 let vals:Vec<Vec<U256>>=records.iter().map(|s|s.split_whitespace().skip(1).take(6).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect()).collect();
 let families:Vec<_>=records.iter().map(|s|s.split_whitespace().nth(7).unwrap_or("unknown")).collect();
 let mut cuts:Vec<(String,usize)>=a[3].split(',').map(|v|{let(x,y)=v.split_once(':').unwrap();(x.to_string(),y.parse().unwrap())}).collect();cuts.sort_by_key(|c|c.1);
 let mut h=Shake256::default();h.update(b"product-paired-fixed-measurement-v1");h.update(&0u64.to_le_bytes());let mut rng=h.finalize_xof();let mut sim=Simulator::new(nq as usize,nb as usize,&mut rng);
 for(lane,v)in vals.iter().enumerate(){for r in 0..4{sim.set_register(&regs[r],v[r],lane);}}
 let p=curve.modulus;let mut start=0;let mut depth=0;
 for(label,end)in cuts {for op in &ops[start..end]{if op.kind==OperationType::PushCondition{depth+=1;}if op.kind==OperationType::PopCondition{depth-=1;}}assert_eq!(depth,0,"prefix must end outside classical scopes");sim.apply_iter(ops[start..end].iter());start=end;
  println!("PREFIX_STATE phase={label} end={end} phase_mask={:#x}",sim.phase);
  for(lane,v)in vals.iter().enumerate(){let den=quantum_ecc::weierstrass_elliptic_curve::sub_mod(v[0],v[2],p);let num=quantum_ecc::weierstrass_elliptic_curve::sub_mod(v[1],v[3],p);let lambda=num.mul_mod(den.inv_mod(p).unwrap(),p);let x=sim.get_register(&regs[0],lane);let y=sim.get_register(&regs[1],lane);
   println!("PREFIX_SHOT phase={label} index={lane} family={} x={x:#x} y={y:#x} lambda={lambda:#x} lambda_equiv={} expected_final_x={:#x} expected_final_y={:#x}",families[lane],y.reduce_mod(p)==lambda,v[4],v[5]);
  }
 }
 println!("DIAGNOSTIC_ONLY prefix_shots={} score=NONE",vals.len());
}
'''
dest.joinpath('src').mkdir(parents=True,exist_ok=True);dest.joinpath('src/main.rs').write_text(prefix+const+helpers+main,newline='\n')
dest.joinpath('Cargo.toml').write_text(f'''[package]
name="product_prefix_replay"
version="0.1.0"
edition="2021"
[dependencies]
quantum_ecc={{path="{base.as_posix()}"}}
alloy-primitives="1.5"
sha3="0.10"
zstd="0.13"
[profile.release]
opt-level=3
lto="thin"
codegen-units=1
''',newline='\n')
