"""Profile the actual frozen/rewritten bank-partition routine, outside submissions."""
from pathlib import Path
import hashlib,json,subprocess,sys
source,library,dest=map(Path,sys.argv[1:4])
(dest/'src').mkdir(parents=True,exist_ok=False)
binding=dict(scope='component emission counts only; not executed Toffolis or a benchmark',source=str(source),revision=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip(),source_sha256={p.relative_to(source).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((source/'src/point_add').rglob('*')) if p.is_file()})
(dest/'source-binding.json').write_text(json.dumps(binding,indent=2)+'\n',encoding='utf8')
(dest/'Cargo.toml').write_text(f'''[package]
name="q692_profile"
version="0.1.0"
edition="2021"
[dependencies]
quantum_ecc={{path="{library.as_posix()}"}}
alloy-primitives="1.5"
ruint="1.12"
sha3="0.10"
zstd="0.13"
serde_json="1"
''',encoding='utf8')
program=r'''
use quantum_ecc::{circuit,sim,weierstrass_elliptic_curve};
#[allow(dead_code)]
#[path="SOURCE/src/point_add/mod.rs"]mod point_add;
fn zstd_level()->i32{3}
fn main(){
 assert!(std::env::var_os("LOWQ_EXACT_STREAM_PATH").is_none());
 println!("SOURCE_BINDING {}",include_str!("../source-binding.json"));
 for sz in [(65,256),(101,160),(101,230),(231,256)] {
  for bank in [false,true] {
   let mut b=point_add::builder::B::new();let ring=b.alloc_n(275);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let _ph=b.alloc();let pool=b.alloc_n(13);let dirty=b.alloc_n(259);assert_eq!(b.width(),692);
   let mut r=ring[..18].to_vec();r.extend(&sx[1..6]);r.push(ring[274]);if bank{r.extend(&q[120..128]);}
   let k=r.len();let s=point_add::midg::S1{r,f:sx[0],zero:ring[17],sgn:sx[0],gt:vec![sx[0]],anc:vec![],andc:vec![],chain:vec![],dirty};
   let rec=point_add::midg::stage1_v_compact_bank_partition(&mut b,&ring[275-k..275],&ring[17..18+point_add::midg::TC],&pool[..8],sz,&s,pool[12],true,&sy,bank,bank);
   b.play(&rec,false);let forward=std::mem::take(&mut b.ops);b.play(&rec,true);let inverse=std::mem::take(&mut b.ops);
   let ccx=|ops:&[circuit::Op]|ops.iter().filter(|o|o.kind==circuit::OperationType::CCX).count();
   println!("PROFILE {}",serde_json::json!({"source":"SOURCE","sz":sz,"bank":bank,"head":k,"qubits":b.width(),"forward_ops":forward.len(),"forward_ccx":ccx(&forward),"inverse_ops":inverse.len(),"inverse_ccx":ccx(&inverse)}));
  }
 }
}
'''.replace('SOURCE',source.as_posix())
(dest/'src/main.rs').write_text(program,encoding='utf8')
