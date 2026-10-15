from pathlib import Path
root=Path(__file__).resolve().parent
dest=root/'single-tool'
(dest/'src').mkdir(parents=True,exist_ok=True)
old=root/'extra-tool'
prefix=(old/'src/main.rs').read_text().split('use quantum_ecc::{circuit,sim};')[0]
(dest/'src/main.rs').write_text(prefix+'''
use quantum_ecc::{circuit,sim};
use std::{path::Path,io::BufWriter,fs};
const DEFAULT_ZSTD_LEVEL:i32=3;
mod cond_pass;
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),4);let mut ops=load_ops(&a[1]).unwrap();for _ in 0..a[2].parse::<usize>().unwrap(){ops=cond_pass::lazy_single(ops);}write_ops(&ops,Path::new(&a[3])).unwrap();}
''')
(dest/'src/cond_pass.rs').write_text((old/'src/cond_pass.rs').read_text()+'\n'+(root/'lazy_single.rs').read_text()+'\n'+(root/'lazy_single_tests.rs').read_text())
for name in ['Cargo.toml','Cargo.lock']:(dest/name).write_bytes((old/name).read_bytes())
