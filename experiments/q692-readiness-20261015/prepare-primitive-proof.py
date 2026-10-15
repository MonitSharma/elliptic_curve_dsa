"""Exhaustive small-word controlled-increment verification, outside the candidate."""
from pathlib import Path
import json,shutil,sys
source,library,dest=map(Path,sys.argv[1:4]);tree=dest/'source/point_add';shutil.copytree(source/'src/point_add',tree)
p=tree/'midg.rs';p.write_text(p.read_text(encoding='utf8')+'\npub(crate) fn readiness_inc(b:&mut B,bits:&[QubitId],ctl:&[(QubitId,bool)],dirty:&[QubitId]){inc_with_controls(b,bits,ctl,dirty);}\n',encoding='utf8')
(dest/'src').mkdir(parents=True)
program=r'''
use quantum_ecc::{circuit,sim,weierstrass_elliptic_curve};
use circuit::{Op,OperationType as K};
#[allow(dead_code)]#[path="PRIVATE/mod.rs"]mod point_add;
fn zstd_level()->i32{3}
fn apply(ops:&[Op],q:&mut[u64]){for o in ops {let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let c=o.q_control2.0 as usize;match o.kind{K::X=>q[t]^=!0,K::CX=>q[t]^=q[a],K::CCX=>q[t]^=q[a]&q[c],K::Swap=>q.swap(a,t),_=>panic!("non-unitary/phase operation")}}}
fn rng(s:&mut u64)->u64{*s^=*s<<13;*s^=*s>>7;*s^=*s<<17;*s}
fn main(){let mut seed=0x692cc0deu64;let mut cases=0;
 for n in 1..=8 {for m in 0..=6 {for negative in [0,(1usize<<m)-1,0x2ausize&((1usize<<m)-1)] {
  let mut b=point_add::builder::B::new();let control=b.alloc_n(m);let target=b.alloc_n(n);let dirty=b.alloc_n(32);
  let literals:Vec<_>=control.iter().enumerate().map(|(i,&q)|(q,negative>>i&1!=0)).collect();
  let gate=point_add::frogdrop_col::rec(&mut b,|b|point_add::midg::readiness_inc(b,&target,&literals,&dirty));
  b.play(&gate,false);let forward=std::mem::take(&mut b.ops);b.play(&gate,true);let inverse=b.ops;
  let size=(1usize<<n)*(1usize<<m);
  for pattern in 0..3 {for start in (0..size).step_by(64){let lanes=(size-start).min(64);let mask=if lanes==64{!0}else{(1u64<<lanes)-1};
   let mut input=vec![0u64;m+n+32];
   for &q in &dirty{input[q.0 as usize]=match pattern{0=>0,1=>!0,_=>rng(&mut seed)};}
   let mut expected=input.clone();
   for lane in 0..lanes{let index=start+lane;let x=index&((1usize<<n)-1);let controls=index>>n;
    for i in 0..m{input[i]|=(((controls>>i)&1)as u64)<<lane;expected[i]=input[i];}
    let y=(x+usize::from((controls^negative)==(1usize<<m)-1))&((1usize<<n)-1);
    for i in 0..n{input[m+i]|=(((x>>i)&1)as u64)<<lane;expected[m+i]|=(((y>>i)&1)as u64)<<lane;}
   }
   let mut got=input.clone();apply(&forward,&mut got);for i in 0..got.len(){assert_eq!((got[i]^expected[i])&mask,0,"n={n} m={m} neg={negative} pattern={pattern} wire={i}");}
   apply(&inverse,&mut got);assert_eq!(got,input,"inverse");cases+=lanes;
  }}
 }}}
 println!("PRIMITIVE_PASS cases={cases} n=1..8 controls=0..6 literal_signs=three_patterns dirty=zero_one_arbitrary full_state=true inverse=true phase=unitary_X_CX_CCX_SWAP");
}
'''.replace('PRIVATE',tree.as_posix())
(dest/'src/main.rs').write_text(program,encoding='utf8')
(dest/'Cargo.toml').write_text('[package]\nname="q692_primitive"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nquantum_ecc={path='+json.dumps(library.as_posix())+'}\nalloy-primitives="1.5"\nruint="1.12"\nsha3="0.10"\nzstd="0.13"\n',encoding='utf8')
