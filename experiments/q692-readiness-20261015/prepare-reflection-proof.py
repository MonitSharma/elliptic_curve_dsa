"""All-measurement comparison of original and conditional-clean reflection."""
from pathlib import Path
import hashlib,json,sys
source,lib,dest,kernel=map(Path,sys.argv[1:5]);assert hashlib.sha256(kernel.read_bytes()).hexdigest()=='72ab93a2fa1fd20bb3aad370aca9f6016ea9069013eaaa34d6b02d911d859622'
(dest/'src').mkdir(parents=True,exist_ok=False)
program=r'''
use quantum_ecc::{circuit,sim,weierstrass_elliptic_curve};
use circuit::{Op,OperationType as K};
#[allow(dead_code)]#[path="SOURCE/src/point_add/mod.rs"]mod point_add;
#[path="KERNEL"]mod phase_kernel;
fn zstd_level()->i32{3}
fn rng(s:&mut u64)->u64{*s^=*s<<13;*s^=*s>>7;*s^=*s<<17;*s}
fn apply(ops:&[Op],q:&mut[u64]){for o in ops{let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let c=o.q_control2.0 as usize;match o.kind{K::X=>q[t]^=!0,K::CX=>q[t]^=q[a],K::CCX=>q[t]^=q[a]&q[c],K::Swap=>q.swap(a,t),_=>panic!("old reference unexpectedly has non-unitary/phase operation")}}}
fn main(){let mut cases=0usize;let mut audits=0usize;let mut seed=0x6927ef1ec7u64;
 for style in [0,1]{
  let mut b=point_add::builder::B::new();let _ring=b.alloc_n(275);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let ph=b.alloc();let pool=b.alloc_n(13);let dirty=b.alloc_n(259);assert_eq!(b.width(),692);
  let mut cycle=q.clone();cycle.extend([pool[9],pool[11],pool[10],sx[6],sx[7],pool[6],pool[7],ph]);
  let act;if style==0{cycle.extend([pool[8],sy[7]]);act=pool[12];}else{cycle.extend([pool[12],sx[1]]);act=pool[8];}
  assert_eq!(cycle.len(),138);let selector=if style==0{&sy[..7]}else{&sy[..]};
  let old=point_add::midg::preposition_high_q25(&mut b,&cycle,selector,act,&dirty);
  let new=point_add::midg::preposition_high_q25_flag(&mut b,&cycle,selector,act,&dirty,sx[0]);
  b.play(&old,false);let oldf=std::mem::take(&mut b.ops);b.play(&new,false);let newf=std::mem::take(&mut b.ops);b.play(&old,true);let oldi=std::mem::take(&mut b.ops);b.play(&new,true);let newi=std::mem::take(&mut b.ops);
  let tof=|v:&[Op]|v.iter().filter(|o|o.kind==K::CCX).count();
  println!("REFLECTION_PROFILE style={style} old_ops={} new_ops={} old_ccx={} new_ccx={} width=692",oldf.len(),newf.len(),tof(&oldf),tof(&newf));
  for value in 0..256usize {for active in [false,true]{
   let mut input:Vec<u64>=(0..692).map(|_|rng(&mut seed)).collect();input[sx[0].0 as usize]=0;input[act.0 as usize]=if active{!0}else{0};
   for (i,wire) in sy.iter().enumerate(){input[wire.0 as usize]=if value>>i&1!=0{!0}else{0};}
   for (of,nf,oi,ni) in [(&oldf,&newf,&oldi,&newi),(&oldi,&newi,&oldf,&newf)] {
    let mut expected=input.clone();apply(of,&mut expected);
    let proof=phase_kernel::audit(nf,&input,&[]).expect("all-measurement phase/value audit");assert_eq!(proof.qubits,expected,"style={style} sy={value} act={active}");assert_eq!(proof.qubits[sx[0].0 as usize],0);
    let reverse=phase_kernel::audit(ni,&proof.qubits,&[]).expect("all-measurement inverse audit");assert_eq!(reverse.qubits,input);
    apply(oi,&mut expected);assert_eq!(expected,input);cases+=64;audits+=2;
   }
  }}
 }
 println!("REFLECTION_PASS cases={cases} all_measurement_audits={audits} all_sy_256=true both_act=true both_cycle_styles=true direct_forward_inverse=true dirty_arbitrary=true entire_state=true flag_restored=true");
}
'''.replace('SOURCE',source.as_posix()).replace('KERNEL',kernel.as_posix())
(dest/'src/main.rs').write_text(program,encoding='utf8')
(dest/'Cargo.toml').write_text('[package]\nname="q692_reflection"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nquantum_ecc={path='+json.dumps(lib.as_posix())+'}\nalloy-primitives="1.5"\nruint="1.12"\nsha3="0.10"\nzstd="0.13"\n',encoding='utf8')
(dest/'source-binding.json').write_text(json.dumps(dict(source=str(source),frozen_kernel_sha256=hashlib.sha256(kernel.read_bytes()).hexdigest(),source_sha256={p.relative_to(source).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((source/'src/point_add').rglob('*'))if p.is_file()}),indent=2)+'\n',encoding='utf8')
