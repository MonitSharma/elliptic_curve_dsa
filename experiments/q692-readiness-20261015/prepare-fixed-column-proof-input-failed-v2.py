"""Exact failed-input column/payload regressions with independent phase audit."""
from pathlib import Path
import hashlib,json,sys
source,lib,dest,kernel=map(Path,sys.argv[1:5]);(dest/'src').mkdir(parents=True,exist_ok=False)
program=r'''
use quantum_ecc::{circuit,sim,weierstrass_elliptic_curve};
use circuit::QubitId;
#[allow(dead_code)]#[path="SOURCE/src/point_add/mod.rs"]mod point_add;
#[path="KERNEL"]mod phase_kernel;
use point_add::frogdrop_sched::{N,Kind};
fn zstd_level()->i32{3}
fn rng(s:&mut u64)->u64{*s^=*s<<13;*s^=*s>>7;*s^=*s<<17;*s}
fn put(q:&mut[u64],w:&[QubitId],lane:usize,v:N){for(i,id)in w.iter().enumerate(){q[id.0 as usize]=(q[id.0 as usize]&!(1u64<<lane))|(u64::from(v.bit(i))<<lane);}}
fn main(){let p=point_add::frogdrop_sched::p();let schedule=point_add::frogdrop_sched::from_text(point_add::pointadd_frogdrop::SCHED_FROGDROP);let(cols,_,_)=point_add::pointadd_frogdrop::col_pars(&schedule);let mut total=0;
 for (shot,j,dxtext) in [
  (2726usize,87usize,"23c93f18c98ad481b15836a8c0d65d53c5ddebfe574e35816b88bf68e12e5948"),
  (2726,88,"23c93f18c98ad481b15836a8c0d65d53c5ddebfe574e35816b88bf68e12e5948"),
  (2913,86,"366c371b9cdefffbe6a9e0a4bb16fcf32488a6b91de6ec2420e3cbd1bc03a97a"),
  (3532,52,"509e39f149cd0e616a9a2de93278234b6b540e4a289e08959df935e18e2966cb")]{
  let dx=N::from_str_radix(dxtext,16).unwrap();let(mut r,mut t)=(vec![p,dx],vec![N::ZERO,N::from(1u64)]);
  while !r.last().unwrap().is_zero(){let n=r.len();let q=r[n-2]/r[n-1];r.push(r[n-2]-q*r[n-1]);t.push(t[n-2]+q*t[n-1]);}
  let trace=point_add::frogdrop_sched::shot(dx,128);let mut step=1;let mut found=None;
  for(ci,rec)in trace.recs.iter().enumerate(){if step==j&&matches!(rec.kind,Kind::Hr|Kind::Ht){found=Some((ci,matches!(rec.kind,Kind::Ht)));break;}if matches!(rec.kind,Kind::Hr|Kind::Ht|Kind::Dq){step+=1;}}
  let(ci,ht)=found.expect("failed step is a complete HR/HT column");let cp=&cols[ci];
  let mut b=point_add::builder::B::new();let ring=b.alloc_n(275);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let ph=b.alloc();let pool=b.alloc_n(13);let payload=b.alloc_n(259);assert_eq!(b.width(),692);
  let rev:Vec<_>=ring.iter().rev().copied().collect();let mut fd=point_add::frogdrop_col::Fd{ring:ring.clone(),q:q.clone(),sy:sy.clone(),sx:sx.clone(),ph,cnt:q[121..].to_vec()};let sc=point_add::frogdrop_col::ColScr::carve_col(&pool,&sx,&payload,24,23,40,cp.sz.1>255);let pl=point_add::pointadd_frogdrop::pl_col(&payload,&fd,&pool);
  let record=point_add::frogdrop_col::rec(&mut b,|b|point_add::frogdrop_col::column_pl(b,&mut fd,cp,&sc,Some(&pl)));b.play(&record,false);let forward=std::mem::take(&mut b.ops);b.play(&record,true);let inverse=b.ops;
  println!("FIXED_COLUMN_BEGIN shot={shot} step={j} column={ci} ht={ht} forward_ops={}",forward.len());
  for seed in 0..4{
   let mut input=vec![0u64;692];let mut expected=vec![0u64;692];let mut random=0x692809u64+seed+shot as u64;
   for lane in 0..64 {
    let mut limbs=[0u64;6];for limb in &mut limbs[..4]{*limb=rng(&mut random);}let dy=match lane{0=>N::ZERO,1=>N::from(1u64),2=>p-N::from(1u64),_=>N::from_limbs(limbs)%p};
    let(mut d,mut w)=(dy,N::ZERO);for k in 1..j{let e=d/r[k];d-=e*r[k];let wp=w.wrapping_add(e.wrapping_mul(t[k]));w=(r[k-1]/r[k]).wrapping_mul(t[k]).wrapping_add(!wp);}
    let e=d/r[j];let dn=d-e*r[j];let wp=w.wrapping_add(e.wrapping_mul(t[j]));let wn=(r[j-1]/r[j]).wrapping_mul(t[j]).wrapping_add(!wp);let pre=258-t[j].bit_len();let post=258-t[j+1].bit_len();let br=r[j].bit_len();let off=wn.wrapping_add(N::from(1u64)<<(258-br));
    for l in 0..259{let previous_ht=ci>0 && matches!(trace.recs[ci-1].kind,Kind::Ht);let initial_boundary=if ht&&previous_ht{r[j-1].bit_len()}else{pre};let initial_offset=w.wrapping_add(N::from(1u64)<<(258-r[j-1].bit_len()));let ib=if l<initial_boundary{d.bit(l)}else if ht&&previous_ht{initial_offset.bit(258-l)}else{w.bit(258-l)};let ob=if ht{if l<br{dn.bit(l)}else{off.bit(258-l)}}else{if l<post{dn.bit(l)}else{wn.bit(258-l)}};
     if ib{input[payload[l].0 as usize]|=1u64<<lane;}if ob{expected[payload[l].0 as usize]|=1u64<<lane;}}
    if ht{put(&mut input,&ring,lane,t[j]);put(&mut input,&rev[..r[j-1].bit_len()],lane,r[j-1]);put(&mut input,&q,lane,r[j]);put(&mut input,&sy,lane,N::from(r[j-1].bit_len()as u64));put(&mut expected,&ring,lane,t[j+1]);put(&mut expected,&rev[..r[j+1].bit_len()],lane,r[j+1]);put(&mut expected,&q,lane,r[j]);put(&mut expected,&sx,lane,N::from(r[j+1].bit_len()as u64));input[ph.0 as usize]|=1u64<<lane;expected[ph.0 as usize]|=1u64<<lane;}
    else{put(&mut input,&ring,lane,r[j]);put(&mut input,&rev[..t[j].bit_len()],lane,t[j]);put(&mut input,&q,lane,t[j-1]);put(&mut input,&sy,lane,N::from(t[j].bit_len()as u64));put(&mut expected,&ring,lane,r[j+1]);put(&mut expected,&rev[..t[j+1].bit_len()],lane,t[j+1]);put(&mut expected,&q,lane,t[j]);put(&mut expected,&sx,lane,N::from(t[j+1].bit_len()as u64));}
   }
   let got=phase_kernel::audit(&forward,&input,&[]).expect("fixed-column all-measurement audit");let bad:Vec<_>=got.qubits.iter().zip(&expected).enumerate().filter_map(|(i,(a,b))|if a!=b{Some(i)}else{None}).collect();assert!(bad.is_empty(),"shot={shot} step={j} seed={seed} wrong wires={bad:?}");
   let restored=phase_kernel::audit(&inverse,&got.qubits,&[]).expect("fixed-column inverse all-measurement audit");assert_eq!(restored.qubits,input);total+=64;println!("FIXED_COLUMN_PASS shot={shot} step={j} seed={seed} lanes=64 exact_payload=true all_measurements=true inverse=true");
  }
 }
 println!("FIXED_COLUMN_SUITE_PASS cases={total} columns=4 all_measurements=true exact_euclid_payload_oracle=true");
}
'''.replace('SOURCE',source.as_posix()).replace('KERNEL',kernel.as_posix())
(dest/'src/main.rs').write_text(program,encoding='utf8')
(dest/'Cargo.toml').write_text('[package]\nname="q692_fixed_column_proof"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nquantum_ecc={path='+json.dumps(lib.as_posix())+'}\nalloy-primitives="1.5"\nruint="1.12"\nsha3="0.10"\nzstd="0.13"\n',encoding='utf8')
(dest/'source-binding.json').write_text(json.dumps(dict(scope='exact failed-input component regression only; no score',candidate=str(source),source_sha256={p.relative_to(source).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((source/'src/point_add').rglob('*'))if p.is_file()},kernel_sha256=hashlib.sha256(kernel.read_bytes()).hexdigest(),proof_sha256=hashlib.sha256((dest/'src/main.rs').read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf8')
