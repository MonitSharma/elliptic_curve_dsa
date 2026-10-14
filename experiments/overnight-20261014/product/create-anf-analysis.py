"""Generate a lightweight external postpass experiment from protected loader."""
from pathlib import Path
import sys
base=Path(sys.argv[1]).resolve();candidate=Path(sys.argv[2]).resolve();dest=Path(sys.argv[3]).resolve()
source=(base/'src/bin/eval_circuit.rs').read_text();dest.joinpath('src').mkdir(parents=True,exist_ok=True)
prefix=source[source.index('use alloy_primitives'):source.index('const OPS_PATH')]
prefix=prefix.replace('use std::fs::{File, OpenOptions};','use std::fs::File;').replace('use std::process::Command;','').replace('use std::time::{SystemTime, UNIX_EPOCH};','')
const=source[source.index('const MAGIC:'):source.index('// ─── Bounded ops.bin loader')]
helpers=source[source.index('fn op_kind_from_u32'):source.index('// ─── Test runner')]
modules=f'''use quantum_ecc::{{circuit,sim,weierstrass_elliptic_curve}};
#[allow(dead_code)] mod point_add {{
 #[path="{(candidate/'affine_simplify.rs').as_posix()}"] mod affine_simplify;
 #[path="{(candidate/'bounded_anf.rs').as_posix()}"] mod bounded_anf;
 pub fn transform(ops:Vec<crate::circuit::Op>)->Vec<crate::circuit::Op>{{bounded_anf::simplify(ops)}}
}}
'''
main=r'''
fn diag(ops:&[Op])->(usize,usize,f64){let mut depth=0;let mut ccx=0;let mut ccz=0;let mut proxy=0.;for o in ops{match o.kind{OperationType::PushCondition=>depth+=1,OperationType::PopCondition=>depth-=1,OperationType::CCX|OperationType::CCZ=>{if o.kind==OperationType::CCX{ccx+=1}else{ccz+=1};proxy+=2f64.powi(-depth-i32::from(o.c_condition!=circuit::NO_BIT));},_=>{}}} (ccx,ccz,proxy)}
fn main(){let a:Vec<_>=std::env::args().collect();let ops=load_ops(&a[1]).unwrap();let before=diag(&ops);let n=ops.len();let out=point_add::transform(ops);let after=diag(&out);println!("ANF_DIAGNOSTIC before_ops={n} after_ops={} before={before:?} after={after:?} proxy_saving={} score=NONE",out.len(),before.2-after.2);
 if before==after&&n==out.len(){return;}
 let mut file=File::create(&a[2]).unwrap();file.write_all(b"QECCOPSZ").unwrap();file.write_all(&(out.len() as u64).to_le_bytes()).unwrap();let mut enc=zstd::stream::write::Encoder::new(file,3).unwrap();for o in out {enc.write_all(&(o.kind as u32).to_le_bytes()).unwrap();enc.write_all(&0u32.to_le_bytes()).unwrap();for value in [o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{enc.write_all(&value.to_le_bytes()).unwrap();}}enc.finish().unwrap();}
'''
dest.joinpath('src/main.rs').write_text(prefix+const+helpers+modules+main,newline='\n')
dest.joinpath('Cargo.toml').write_text(f'''[package]
name="product_anf_analysis"
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
