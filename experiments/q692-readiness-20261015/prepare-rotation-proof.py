"""Compare original and factored virtual size rotations on the entire state."""
from pathlib import Path
import hashlib,json,sys
source,lib,dest=map(Path,sys.argv[1:4]);(dest/'src').mkdir(parents=True,exist_ok=False)
program=r'''
use quantum_ecc::{circuit,sim,weierstrass_elliptic_curve};
use circuit::{Op,OperationType as K};
#[allow(dead_code)]#[path="SOURCE/src/point_add/mod.rs"]mod point_add;
fn zstd_level()->i32{3}
fn rng(s:&mut u64)->u64{*s^=*s<<13;*s^=*s>>7;*s^=*s<<17;*s}
fn apply(ops:&[Op],q:&mut[u64]){for o in ops{let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let c=o.q_control2.0 as usize;match o.kind{K::X=>q[t]^=!0,K::CX=>q[t]^=q[a],K::CCX=>q[t]^=q[a]&q[c],K::Swap=>q.swap(a,t),_=>panic!("unexpected non-unitary/phase operation")}}}
fn main(){let mut cases=0usize;let mut seed=0x692607a710u64;
 for protected in [false,true]{
  let mut b=point_add::builder::B::new();let ring=b.alloc_n(275);let sz=b.alloc_n(9);let sy=b.alloc_n(8);let flag=b.alloc();let dirty=b.alloc_n(259);let _spectators=b.alloc_n(140);assert_eq!(b.width(),692);
  let support=if protected{(0..44).chain(243..275).collect()}else{(0..25).collect()};
  let old=point_add::midg::care_borrowed_sz(&mut b,&ring,&sz,&sy,&support,false,&dirty);
  let new=point_add::midg::care_borrowed_sz_flag(&mut b,&ring,&sz,&sy,&support,false,&dirty,flag);
  b.play(&old,false);let oldf=std::mem::take(&mut b.ops);b.play(&new,false);let newf=std::mem::take(&mut b.ops);b.play(&old,true);let oldi=std::mem::take(&mut b.ops);b.play(&new,true);let newi=std::mem::take(&mut b.ops);
  let tof=|v:&[Op]|v.iter().filter(|o|o.kind==K::CCX).count();
  println!("ROTATION_PROFILE protected={protected} old_ops={} new_ops={} old_ccx={} new_ccx={} width=692",oldf.len(),newf.len(),tof(&oldf),tof(&newf));
  for selector in 0..256usize{for group in 0..8usize{
   let mut input:Vec<u64>=(0..692).map(|_|rng(&mut seed)).collect();input[flag.0 as usize]=0;
   for (i,q) in sy.iter().enumerate(){input[q.0 as usize]=if selector>>i&1!=0{!0}else{0};}
   for q in &sz{input[q.0 as usize]=0;}
   for lane in 0..64{let size=group*64+lane;for (i,q) in sz.iter().enumerate(){input[q.0 as usize]|=(((size>>i)&1)as u64)<<lane;}}
   for (of,nf,oi,ni) in [(&oldf,&newf,&oldi,&newi),(&oldi,&newi,&oldf,&newf)]{
    let mut a=input.clone();let mut c=input.clone();apply(of,&mut a);apply(nf,&mut c);assert_eq!(a,c,"forward/inverse entire state sy={selector} group={group} protected={protected}");assert_eq!(c[flag.0 as usize],0);
    apply(oi,&mut a);apply(ni,&mut c);assert_eq!(a,input);assert_eq!(c,input);cases+=64;
   }
  }}
 }
 println!("ROTATION_PASS cases={cases} all_sy_256=true all_sz_512=true both_supports=true direct_forward_inverse=true dirty_arbitrary=true entire_state=true flag_restored=true phase=unitary_X_CX_CCX_SWAP");
}
'''.replace('SOURCE',source.as_posix())
(dest/'src/main.rs').write_text(program,encoding='utf8')
(dest/'Cargo.toml').write_text('[package]\nname="q692_rotation"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nquantum_ecc={path='+json.dumps(lib.as_posix())+'}\nalloy-primitives="1.5"\nruint="1.12"\nsha3="0.10"\nzstd="0.13"\n',encoding='utf8')
(dest/'source-binding.json').write_text(json.dumps(dict(source=str(source),source_sha256={p.relative_to(source).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((source/'src/point_add').rglob('*'))if p.is_file()}),indent=2)+'\n',encoding='utf8')
