"""Build a separate full-state paired/structured diagnostic; protected files unchanged."""
from pathlib import Path
import hashlib,sys
base=Path(sys.argv[1]).resolve();dest=Path(sys.argv[2]).resolve()
source=(base/'src/bin/eval_circuit.rs').read_text()
dest.joinpath('src').mkdir(parents=True,exist_ok=True)
prefix=source[source.index('use alloy_primitives'):source.index('const OPS_PATH')]
prefix=prefix.replace('use std::fs::{File, OpenOptions};','use std::fs::File;')
prefix=prefix.replace('use std::process::Command;','').replace('use std::time::{SystemTime, UNIX_EPOCH};','')
constants=source[source.index('const MAGIC:'):source.index('// ─── Bounded ops.bin loader')]
helpers=source[source.index('fn op_kind_from_u32'):source.index('// ─── Test runner')]
main=r'''
fn main() {
 let a:Vec<String>=std::env::args().collect();assert!(a.len()==5,"baseline stream, candidate stream, packet mode, out.tsv");
 let left=load_ops(&a[1]).unwrap();let right=load_ops(&a[2]).unwrap();
 let (nq,nb,_,regs)=analyze_ops(left.iter());let (rq,rb,_,rregs)=analyze_ops(right.iter());
 assert_eq!((nq,nb),(rq,rb));assert_eq!(regs,rregs);
 let curve=secp256k1();let mut packets=Vec::new();
 let mut xof=if a[3]=="baseline"{fiat_shamir_seed(&left)}else{let mut h=Shake256::default();h.update(b"product-independent-structured-v1");h.finalize_xof()};
 let size=if a[3]=="baseline"{NUM_TESTS}else{256};
 let beta=U256::from(2).pow_mod((curve.modulus-U256::from(1))/U256::from(3),curve.modulus);
 assert!(beta!=U256::from(1));assert_eq!(beta.pow_mod(U256::from(3),curve.modulus),U256::from(1));
 let mut out=File::create(&a[4]).unwrap();writeln!(out,"# index target_x target_y offset_x offset_y expected_x expected_y family").unwrap();
 for i in 0..size {
  let mut b1=[0u8;32];let mut b2=[0u8;32];XofReader::read(&mut xof,&mut b1);XofReader::read(&mut xof,&mut b2);
  let mut t=curve.mul(curve.gx,curve.gy,U256::from_le_bytes(b1));let o=curve.mul(curve.gx,curve.gy,U256::from_le_bytes(b2));
  let family=if a[3]=="structured"&&i%2==0{let d=curve.add(o.0,o.1,o.0,o.1);t=(d.0,curve.modulus-d.1);"minus2A"}
    else if a[3]=="structured"{t=(o.0.mul_mod(beta,curve.modulus),o.1);"zero_slope"}else{"independent"};
  if t.0==o.0||(t.0.is_zero()&&t.1.is_zero())||(o.0.is_zero()&&o.1.is_zero()){continue;}
  assert!(curve.is_on_curve(t.0,t.1));assert!(curve.is_on_curve(o.0,o.1));
  let e=curve.add(t.0,t.1,o.0,o.1);
  writeln!(out,"{}\t{:#x}\t{:#x}\t{:#x}\t{:#x}\t{:#x}\t{:#x}\t{family}",packets.len(),t.0,t.1,o.0,o.1,e.0,e.1).unwrap();
  packets.push([t.0,t.1,o.0,o.1,e.0,e.1]);
 }
 let nr=|ops:&[Op]|ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count();
 assert_eq!(nr(&left),nr(&right),"paired RNG requires unchanged measurement/reset order");
 let (mut mismatches,mut left_bad,mut right_bad,mut left_phase,mut right_phase,mut left_dirty,mut right_dirty)=(0,0,0,0,0,0,0);
 for (batch,points) in packets.chunks(64).enumerate(){
  let mut h=Shake256::default();h.update(b"product-paired-fixed-measurement-v1");h.update(&(batch as u64).to_le_bytes());
  let mut lr=h.clone().finalize_xof();let mut rr=h.finalize_xof();let mut ls=Simulator::new(nq as usize,nb as usize,&mut lr);let mut rs=Simulator::new(rq as usize,rb as usize,&mut rr);
  for (lane,v) in points.iter().enumerate(){for r in 0..4{ls.set_register(&regs[r],v[r],lane);rs.set_register(&regs[r],v[r],lane);}}
  ls.apply_iter(left.iter());rs.apply_iter(right.iter());let live=if points.len()==64{u64::MAX}else{(1u64<<points.len())-1};
  let eq=ls.qubits.iter().zip(&rs.qubits).all(|(l,r)|(l^r)&live==0)&&ls.bits.iter().zip(&rs.bits).all(|(l,r)|(l^r)&live==0)&&(ls.phase^rs.phase)&live==0;
  if !eq{mismatches+=1;eprintln!("PAIRED_STATE_DIFFER batch={batch}");}
  for (lane,v) in points.iter().enumerate(){let good=|s:&Simulator<_>|s.get_register(&regs[0],lane)==v[4]&&s.get_register(&regs[1],lane)==v[5];left_bad+=usize::from(!good(&ls));right_bad+=usize::from(!good(&rs));}
  left_phase+=usize::from(ls.phase&live!=0);right_phase+=usize::from(rs.phase&live!=0);
  for reg in &regs{for q in reg{if let QubitOrBit::Qubit(q)=q{*ls.qubit_mut(*q)=0;*rs.qubit_mut(*q)=0;}}}
  left_dirty+=usize::from(ls.qubits.iter().any(|q|q&live!=0));right_dirty+=usize::from(rs.qubits.iter().any(|q|q&live!=0));
  eprintln!("PAIRED_BATCH {batch} equal={eq} left_phase={:#x} right_phase={:#x}",ls.phase&live,rs.phase&live);
 }
 println!("DIAGNOSTIC_ONLY shots={} unequal_batches={mismatches} left_bad={left_bad} right_bad={right_bad} left_phase_batches={left_phase} right_phase_batches={right_phase} left_dirty_batches={left_dirty} right_dirty_batches={right_dirty} score=NONE",packets.len());
 assert_eq!(mismatches,0,"exact transformation must preserve every final quantum/classical slot and phase");
}
'''
dest.joinpath('src/main.rs').write_text(prefix+constants+helpers+main,newline='\n')
dest.joinpath('Cargo.toml').write_text(f'''[package]
name="product_paired_diagnostic"
version="0.1.0"
edition="2021"
[dependencies]
quantum_ecc={{path="{base.as_posix()}"}}
alloy-primitives="1.5"
sha3="0.10"
zstd="0.13"
[profile.release]
opt-level=3
lto="thin"
codegen-units=1
''',newline='\n')
print('protected_evaluator_sha256='+hashlib.sha256((base/'src/bin/eval_circuit.rs').read_bytes()).hexdigest())
print('diagnostic_sha256='+hashlib.sha256(dest.joinpath('src/main.rs').read_bytes()).hexdigest())
