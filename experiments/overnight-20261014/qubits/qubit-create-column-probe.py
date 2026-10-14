"""Create source-bound one-column diagnostics outside submission checkouts."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

source, library, dest = map(lambda s: Path(s).resolve(), sys.argv[1:4])
attestation = dict(source_variant=source.name,
                  base_revision=subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip(),
                  source_sha256={f:hashlib.sha256(source.joinpath(f).read_bytes()).hexdigest() for f in
                      ["src/point_add/frogdrop.rs", "src/point_add/midg.rs", "src/point_add/tests_midg_k24.rs"]})
dest.joinpath("src").mkdir(parents=True, exist_ok=True)
program = r'''
use quantum_ecc::{circuit,sim,weierstrass_elliptic_curve};
use circuit::{QubitId,Op,analyze_ops};
use sim::Simulator;
use sha3::digest::{Update,ExtendableOutput};
#[allow(dead_code)]
#[path = "SOURCE_PATH/src/point_add/mod.rs"]
mod point_add;
const PROBE_SOURCE: &str = "SOURCE_PATH";
const PROBE_ATTESTATION: &str = r#"ATTESTATION_JSON"#;
use point_add::builder::B;
use point_add::frogdrop_col::{Fd,ColScr};
use point_add::frogdrop_sched::{N,p};
fn zstd_level()->i32 {3}
fn put(q:&mut [u64],reg:&[QubitId],v:N){for(i,qid)in reg.iter().enumerate(){q[qid.0 as usize]=if v.bit(i){u64::MAX}else{0};}}
fn get(q:&[u64],reg:&[QubitId])->N{reg.iter().enumerate().fold(N::ZERO,|v,(i,qid)|v|(N::from(q[qid.0 as usize]&1)<<i))}
fn apply(ops:&[Op],initial:&[u64])->(Vec<u64>,u64){
 let(nq,nb,_,_)=analyze_ops(ops.iter());let mut h=sha3::Shake256::default();h.update(b"qubit-column-source-bound-v1");
 let mut xof=h.finalize_xof();let mut s=Simulator::new((nq as usize).max(initial.len()),nb.max(1)as usize,&mut xof);
 s.qubits=initial.to_vec();s.apply_iter(ops.iter());(s.qubits,s.phase)
}
fn main(){
 println!("PROBE_SOURCE {PROBE_SOURCE}");
 println!("PROBE_ATTESTATION {PROBE_ATTESTATION}");
 let a:Vec<String>=std::env::args().collect();let dx=N::from_str_radix(a[1].trim_start_matches("0x"),16).unwrap();
 let j:usize=a[2].parse().unwrap();let ci:usize=a[3].parse().unwrap();
 let(mut r,mut t)=(vec![p(),dx],vec![N::ZERO,N::from(1u64)]);
 while !r[r.len()-1].is_zero(){let n=r.len();let q=r[n-2]/r[n-1];let rn=r[n-2]-q*r[n-1];let tn=t[n-2]+q*t[n-1];r.push(rn);t.push(tn);}
 assert!(r[j].bit_len()>128,"this probe admits HR columns only");
 let mut b=B::new();let ring=b.alloc_n(276);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let ph=b.alloc();
 let pool=b.alloc_n(13);let dirty=b.alloc_n(259);let cnt=q[121..].to_vec();
 let mut fd=Fd{ring:ring.clone(),q:q.clone(),sy:sy.clone(),sx:sx.clone(),ph,cnt};
 let(cols,_,_)=point_add::pointadd_frogdrop::col_pars(&point_add::frogdrop_sched::from_text(point_add::pointadd_frogdrop::SCHED_FROGDROP));
 let cp=&cols[ci];assert!(cp.hr);assert!(!cp.dn&&!cp.sw&&!cp.ht,"admitted pure HR source envelope");
 assert!(r[j].bit_len()>=cp.sz.0&&r[j].bit_len()<=cp.sz.1);
 assert!(t[j].bit_len()>=cp.sy.0&&t[j].bit_len()<=cp.sy.1);
 let sc=ColScr::carve_col(&pool,&fd.sx,&dirty,24,23,40,cp.sz.1>255);
 let mut initial=vec![0u64;b.width()as usize];
 put(&mut initial,&ring,r[j]);let rev:Vec<_>=ring.iter().rev().copied().collect();put(&mut initial,&rev[..t[j].bit_len()],t[j]);
 put(&mut initial,&q,t[j-1]);put(&mut initial,&sy,N::from(t[j].bit_len()as u64));
 for(i,&qid)in dirty.iter().enumerate(){initial[qid.0 as usize]=(i as u64).wrapping_mul(0x9e3779b97f4a7c15)^0x20261014;}
 println!("ADMITTED_HR column={ci} euclid_step={j} z={:#x} x={:#x} y={:#x} q={} expected_next_t={:#x} expected_next_r={:#x} width={}",r[j],t[j-1],t[j],r[j-1]/r[j],t[j+1],r[j+1],b.width());
 std::env::set_var("FD_MARK","1");point_add::frogdrop_col::MARKS.with(|m|m.borrow_mut().clear());
 point_add::frogdrop_col::column_pl(&mut b,&mut fd,cp,&sc,None);
 let marks=point_add::frogdrop_col::MARKS.with(|m|m.borrow().clone());
 let outdir=std::path::Path::new(&a[4]);std::fs::create_dir_all(outdir).unwrap();
 for(index,stage)in marks{
   if stage>11{continue;}let(words,phase)=apply(&b.ops[..index],&initial);
   let rd=get(&words,&ring);let top=get(&words,&rev);let qq=get(&words,&q);
   println!("STAGE stage={stage} ops={index} ring={rd:#x} top={top:#x} q={qq:#x} sy={} sx={} phase={phase:#x}",get(&words,&sy),get(&words,&sx));
   std::fs::write(outdir.join(format!("stage-{stage}.txt")),words.iter().map(|w|format!("{w:016x}\n")).collect::<String>()).unwrap();
 }
 let(words,phase)=apply(&b.ops,&initial);let expected_bottom=r[j+1];let expected_top=t[j+1];
 let mut expected=initial.clone();for qid in &ring{expected[qid.0 as usize]=0;}
 put(&mut expected,&ring,expected_bottom);put(&mut expected,&rev[..expected_top.bit_len()],expected_top);
 put(&mut expected,&q,t[j]);put(&mut expected,&sy,N::ZERO);put(&mut expected,&sx,N::from(expected_top.bit_len()as u64));
 let mismatch:Vec<_>=words.iter().zip(&expected).enumerate().filter(|(_,(a,z))|a!=z).map(|(i,_)|i).collect();
 println!("COMPONENT_RESULT mismatching_wires={mismatch:?} phase={phase:#x} generated_ops={} score=NONE",b.ops.len());
 let mut ib=B::new();let _ir=ib.alloc_n(276);let _iq=ib.alloc_n(128);let _isy=ib.alloc_n(8);let _isx=ib.alloc_n(8);let _iph=ib.alloc();let _pool=ib.alloc_n(13);let _dirty=ib.alloc_n(259);
 let mut ifd=Fd{ring:ring.clone(),q:q.clone(),sy:sy.clone(),sx:sx.clone(),ph,cnt:q[121..].to_vec()};
 ib.begin();point_add::frogdrop_col::column_pl(&mut ib,&mut ifd,cp,&sc,None);let rec=ib.end();ib.play(&rec,true);
 let(back,iphase)=apply(&ib.ops,&words);println!("INVERSE_RESULT all_wires_restore={} phase={iphase:#x}",back==initial);
}
'''.replace("SOURCE_PATH", source.as_posix()).replace("ATTESTATION_JSON",json.dumps(attestation,separators=(',',':')))
dest.joinpath("src/main.rs").write_text(program)
dest.joinpath("Cargo.toml").write_text(f'''[package]
name="qubit_column_probe_{dest.name.replace('-', '_')}"
version="0.1.0"
edition="2021"
[dependencies]
quantum_ecc={{path="{library.as_posix()}"}}
alloy-primitives="1.5"
ruint="1.12"
sha3="0.10"
zstd="0.13"
[profile.release]
opt-level=3
lto="thin"
codegen-units=1
''')
