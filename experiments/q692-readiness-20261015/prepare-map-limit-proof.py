"""Isolate the even-divisor map on the exact trailing-zero counterexample."""
from pathlib import Path
import hashlib,json,sys
source,lib,dest,kernel=map(Path,sys.argv[1:5]);(dest/'src').mkdir(parents=True,exist_ok=False)
program=r'''
use quantum_ecc::{circuit,sim,weierstrass_elliptic_curve};use circuit::QubitId;
#[allow(dead_code)]#[path="SOURCE/src/point_add/mod.rs"]mod point_add;
#[path="KERNEL"]mod phase_kernel;
use point_add::frogdrop_sched::N;
fn zstd_level()->i32{3}
fn put(q:&mut[u64],w:&[QubitId],v:N){for(i,id)in w.iter().enumerate(){q[id.0 as usize]=if v.bit(i){!0}else{0};}}
fn main(){let p=point_add::frogdrop_sched::p();let dx=N::from_str_radix("23c93f18c98ad481b15836a8c0d65d53c5ddebfe574e35816b88bf68e12e5948",16).unwrap();let(mut r,mut t)=(vec![p,dx],vec![N::ZERO,N::from(1u64)]);while !r.last().unwrap().is_zero(){let n=r.len();let q=r[n-2]/r[n-1];r.push(r[n-2]-q*r[n-1]);t.push(t[n-2]+q*t[n-1]);}
 let(cols,_,_)=point_add::pointadd_frogdrop::col_pars(&point_add::frogdrop_sched::from_text(point_add::pointadd_frogdrop::SCHED_FROGDROP));
 for j in [87usize,88]{let cp=&cols[j];let mut b=point_add::builder::B::new();let ring=b.alloc_n(275);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let ph=b.alloc();let pool=b.alloc_n(13);let dirty=b.alloc_n(259);let fd=point_add::frogdrop_col::Fd{ring:ring.clone(),q:q.clone(),sy:sy.clone(),sx:sx.clone(),ph,cnt:q[121..].to_vec()};let sc=point_add::frogdrop_col::ColScr::carve_col(&pool,&sx,&dirty,24,25,40,cp.sz.1>255);
 let record=point_add::frogdrop_col::map_stage(&mut b,&fd,cp,&sc);b.play(&record,false);let forward=std::mem::take(&mut b.ops);b.play(&record,true);let inverse=b.ops;let rev:Vec<_>=ring.iter().rev().copied().collect();
 let(x,y,z)=(r[j+1],r[j],t[j]);assert_eq!((p-z*x)%y,N::ZERO);let want=(p-z*x)/y;assert_eq!(want,t[j+1]);let mut input=vec![0u64;692];put(&mut input,&ring,z);put(&mut input,&rev[..y.bit_len()],y);put(&mut input,&q,x);put(&mut input,&sy,N::from(y.bit_len()as u64));input[ph.0 as usize]=!0;for id in &dirty{input[id.0 as usize]=0x5a5af0f00ff055aa;}
 let checked=phase_kernel::audit(&forward,&input,&[]).expect("even-divisor map all-measurement phase");let get=|w:&[QubitId]|w.iter().enumerate().fold(N::ZERO,|a,(i,id)|a|((N::from(checked.qubits[id.0 as usize]&1))<<i));let cut=275-x.bit_len();assert_eq!(get(&ring[..cut]),want);assert_eq!(get(&rev[..x.bit_len()]),x);assert_eq!(get(&q),y);let restored=phase_kernel::audit(&inverse,&checked.qubits,&[]).expect("map inverse all-measurement phase");assert_eq!(restored.qubits,input);println!("MAP_LIMIT_PASS step={j} v2_x={} v2_y={} emax={} width=692 all_measurements=true exact_integer_oracle=true",x.trailing_zeros(),y.trailing_zeros(),cp.emax);
 }
}
'''.replace('SOURCE',source.as_posix()).replace('KERNEL',kernel.as_posix())
(dest/'src/main.rs').write_text(program,encoding='utf8')
(dest/'Cargo.toml').write_text('[package]\nname="q692_map_limit_proof"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nquantum_ecc={path='+json.dumps(lib.as_posix())+'}\nalloy-primitives="1.5"\nruint="1.12"\nsha3="0.10"\nzstd="0.13"\n',encoding='utf8')
(dest/'source-binding.json').write_text(json.dumps(dict(scope='exact counterexample map only, not a score',candidate=str(source),map_source_sha256=hashlib.sha256((source/'src/point_add/frogdrop_col.rs').read_bytes()).hexdigest(),proof_sha256=hashlib.sha256((dest/'src/main.rs').read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf8')
