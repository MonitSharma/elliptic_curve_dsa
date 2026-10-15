"""Measure additional existing exact public passes on the frozen wide stream."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent
dest=root/'extra-tool'
(dest/'src').mkdir(parents=True,exist_ok=True)
old=root.parent/'cache-retention-20261015/analyzer'
s=(old/'src/main.rs').read_text().split('use quantum_ecc::{circuit,sim};')[0]
s+='''
use quantum_ecc::{circuit,sim};
use std::{path::Path,io::BufWriter,fs};
const DEFAULT_ZSTD_LEVEL:i32=3;
mod cond_pass;
mod pscan;
mod zero_force;
fn main(){
 let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),4);
 let ops=load_ops(&a[1]).unwrap();
 let ops=if a[2]=="zero" {zero_force::run(ops)}else{
  std::env::set_var("SL_COND",if a[2]=="combo"{"mufsr"}else{&a[2]});
  let ops=cond_pass::run(ops);
  if a[2]=="combo"{zero_force::run(ops)}else{ops}
 };
 write_ops(&ops,Path::new(&a[3])).unwrap();
}
'''
(dest/'src/main.rs').write_text(s)
base=root/'candidate/src/point_add'
(dest/'src/cond_pass.rs').write_bytes((base/'cond_pass.rs').read_bytes())
for name in ['pscan.rs','zero_force.rs']:
 data=subprocess.check_output(['git','-C',str(root.parent/'toffoli'),'show',f'4b2ec52f:src/point_add/{name}'])
 (dest/'src'/name).write_bytes(data)
for name in ['Cargo.toml','Cargo.lock']:
 (dest/name).write_bytes((old/name).read_bytes())
