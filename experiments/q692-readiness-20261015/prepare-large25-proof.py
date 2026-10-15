"""Independent arithmetic and all-measurement checks of conditional SZ borrowing."""
from pathlib import Path
import hashlib,json,sys
source,lib,dest,kernel=map(Path,sys.argv[1:5]);(dest/'src').mkdir(parents=True,exist_ok=False)
assert hashlib.sha256(kernel.read_bytes()).hexdigest()=='72ab93a2fa1fd20bb3aad370aca9f6016ea9069013eaaa34d6b02d911d859622'
program=r'''
use quantum_ecc::{circuit,sim,weierstrass_elliptic_curve};
use circuit::{QubitId,Op};
#[allow(dead_code)]#[path="SOURCE/src/point_add/mod.rs"]mod point_add;
#[path="KERNEL"]mod phase_kernel;
fn zstd_level()->i32{3}
fn rng(s:&mut u64)->u64{*s^=*s<<13;*s^=*s>>7;*s^=*s<<17;*s}
fn word(q:&[u64],w:&[QubitId],lane:usize)->u64{w.iter().enumerate().fold(0,|a,(i,v)|a|((q[v.0 as usize]>>lane&1)<<i))}
fn store(q:&mut[u64],w:&[QubitId],lane:usize,value:u64){for(i,v)in w.iter().enumerate(){q[v.0 as usize]=(q[v.0 as usize]&!(1u64<<lane))|((value>>i&1)<<lane);}}
fn main(){let mut seed=0x692825u64;let mut cases=0;let mut audits=0;
 for bank in [false,true]{
  let mut b=point_add::builder::B::new();let ring=b.alloc_n(275);let _q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let _ph=b.alloc();let pool=b.alloc_n(13);let dirty=b.alloc_n(259);assert_eq!(b.width(),692);
  let act=pool[12];let sz=&pool[..8];let zh=&ring[250..275];let win=&ring[17..45];let mut r=ring[..18].to_vec();r.extend(&sx[1..6]);r.push(ring[274]);
  let recording=point_add::midg::stage1_v_compact_large25(&mut b,zh,win,sz,&sy,&r,act,sx[0],&dirty,bank);
  b.play(&recording,false);let forward:Vec<Op>=std::mem::take(&mut b.ops);b.play(&recording,true);let inverse=b.ops;
  for size in 0..256usize {for active in [false,true]{for pattern in 0..2{
   let mut input:Vec<_>=(0..692).map(|_|rng(&mut seed)).collect();input[sx[0].0 as usize]=0;input[act.0 as usize]=if active{!0}else{0};store(&mut input,&sy,0,size as u64);
   let mut expected=input.clone();
   for lane in 0..64{
    store(&mut input,&sy,lane,size as u64);store(&mut expected,&sy,lane,size as u64);
    let sz_value=101+lane%62;store(&mut input,sz,lane,sz_value as u64);store(&mut expected,sz,lane,sz_value as u64);
    let low=size&127;let selected=active&&(low==0||low>=if bank{104}else{96});
    if selected {
     for wire in &r{input[wire.0 as usize]&=!(1<<lane);expected[wire.0 as usize]&=!(1<<lane);}
     let divisor=word(&input,zh,lane)|(1<<24)|1;let mut remainder=(1<<24)-1;let mut add=0;
     for j in 0..27{remainder=2*remainder+1;if remainder>=divisor{remainder-=divisor;}else{add+=1<<(26-j);}}
     let targets:Vec<_>=win[1..].iter().rev().copied().collect();let before=word(&input,&targets,lane);
     store(&mut expected,&targets,lane,(before+add)&((1<<27)-1));
    }
    if pattern==1 {for wire in &dirty{input[wire.0 as usize]&=!(1<<lane);expected[wire.0 as usize]&=!(1<<lane);}}
   }
   let checked=phase_kernel::audit(&forward,&input,&[]).expect("all-measurement forward");assert_eq!(checked.qubits,expected,"bank={bank} sy={size} active={active} pattern={pattern}");
   let restored=phase_kernel::audit(&inverse,&checked.qubits,&[]).expect("all-measurement inverse");assert_eq!(restored.qubits,input);
   cases+=64;audits+=2;
  }}}
  println!("LARGE25_STYLE_PASS bank={bank} physical_ops={} width=692",forward.len());
 }
 println!("LARGE25_PASS cases={cases} all_measurement_audits={audits} independent_integer_reference=true all_sy_256=true both_act=true selected_sz_101_162=true arbitrary_unselected_remainder=true entire_state=true inverse=true");
}
'''.replace('SOURCE',source.as_posix()).replace('KERNEL',kernel.as_posix())
(dest/'src/main.rs').write_text(program,encoding='utf8')
(dest/'Cargo.toml').write_text('[package]\nname="q692_large25_proof"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nquantum_ecc={path='+json.dumps(lib.as_posix())+'}\nalloy-primitives="1.5"\nruint="1.12"\nsha3="0.10"\nzstd="0.13"\n',encoding='utf8')
(dest/'source-binding.json').write_text(json.dumps(dict(scope='component arithmetic proof only; no score',candidate=str(source),midg_sha256=hashlib.sha256((source/'src/point_add/midg.rs').read_bytes()).hexdigest(),proof_sha256=hashlib.sha256((dest/'src/main.rs').read_bytes()).hexdigest(),kernel_sha256=hashlib.sha256(kernel.read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf8')
