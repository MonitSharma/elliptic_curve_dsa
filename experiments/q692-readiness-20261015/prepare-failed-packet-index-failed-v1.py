"""Reconstruct the unchanged failed v6 packet; never tune or replace its inputs."""
from pathlib import Path
import hashlib,json,shutil,sys
source,lib,dest=map(Path,sys.argv[1:4]);tree=dest/'source/point_add';shutil.copytree(source/'src/point_add',tree)
p=tree/'frogdrop_sched.rs';s=p.read_text(encoding='utf8')
for name in ['g_hr_ok','g_ht_ok']:assert s.count('fn '+name+'(')==1;s=s.replace('fn '+name+'(','pub(crate) fn '+name+'(')
p.write_text(s,encoding='utf8')
(dest/'src').mkdir(parents=True)
program=r'''
use quantum_ecc::{circuit,sim,weierstrass_elliptic_curve};
use alloy_primitives::U256;
use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
use std::io::{Read,BufReader};
use point_add::frogdrop_sched::{N,Kind};
#[allow(dead_code)]#[path="PRIVATE/mod.rs"]mod point_add;
fn zstd_level()->i32{3}
fn wide(v:U256)->N{let a=v.as_limbs();N::from_limbs([a[0],a[1],a[2],a[3],0,0])}
fn diagnosis(x:N)->serde_json::Value{
 let p=point_add::frogdrop_sched::p();let dx=if x>p/ N::from(2u64){p-x}else{x};
 let schedule=point_add::frogdrop_sched::from_text(point_add::pointadd_frogdrop::SCHED_FROGDROP);
 let shot=point_add::frogdrop_sched::shot(dx,128);let(cols,_,_)=point_add::pointadd_frogdrop::col_pars(&schedule);
 let(mut r,mut t)=(vec![p,dx],vec![N::ZERO,N::from(1u64)]);
 while !r.last().unwrap().is_zero(){let n=r.len();let q=r[n-2]/r[n-1];let rn=r[n-2]-q*r[n-1];let tn=t[n-2]+q*t[n-1];r.push(rn);t.push(tn);}
 let mut j=1usize;let mut issues=vec![];let mut largest=N::ZERO;
 for(c,record)in shot.recs.iter().enumerate(){
  let phase=match record.kind{Kind::Hr|Kind::Dl=>Some(false),Kind::Ht=>Some(true),_=>None};
  if let Some(ht)=phase {
   let q=r[j-1]/r[j];largest=largest.max(q);let cp=&cols[c];
   let pure=cp.n==275&&cp.k==16&&cp.nq==128&&cp.h==18&&cp.sz.0>=101&&cp.hr&&!cp.ht&&!cp.sw&&!cp.dn&&!cp.dl&&!cp.dq&&!cp.psw&&!cp.tt&&cp.sz.1<=255&&cp.sy.1+23<128;
   let ht25=cp.n==275&&cp.k==16&&cp.nq==128&&cp.h==18&&cp.sz.0>=101&&cp.sz.1<=255&&cp.ht;
   let precision=cp.k==16&&cp.n==275&&cp.nq==128&&cp.h==18&&cp.sz.0>=101&&cp.sz.1<=256;
   let y=if ht{r[j]}else{t[j]};let head=if precision{if y.bit_len()<=if ht25{103}else{95}{32}else{24}}else{cp.k};
   let cap=if ht&&ht25{25}else if !ht&&pure{24}else{23};
   let ok=if ht{point_add::frogdrop_sched::g_ht_ok(&t[j],&r[j],&r[j-1],&r[j+1],&q,head,cap)}else{point_add::frogdrop_sched::g_hr_ok(&r[j],&t[j-1],&t[j],&t[j+1],head,cap)};
   if !ok||q.bit_len()>cap{issues.push(serde_json::json!({"column":c,"step":j,"kind":format!("{:?}",record.kind),"quotient":q.to_string(),"quotient_bits":q.bit_len(),"cap":cap,"head":head,"sy":y.bit_len(),"z_bits":if ht{t[j].bit_len()}else{r[j].bit_len()},"gtest_ok":ok,"r_previous":format!("{:x}",r[j-1]),"r_current":format!("{:x}",r[j]),"r_next":format!("{:x}",r[j+1]),"t_previous":format!("{:x}",t[j-1]),"t_current":format!("{:x}",t[j]),"t_next":format!("{:x}",t[j+1])}));}
  }
  match record.kind{Kind::Hr|Kind::Ht|Kind::Dl|Kind::Dq=>j+=1,_=>{}}
 }
 serde_json::json!({"reflected_dx":format!("{:x}",dx),"envelope_check":point_add::frogdrop_sched::check(&shot,&schedule),"largest_quotient":largest.to_string(),"candidate_policy_issues":issues,"public_predictor_k24":point_add::frogdrop_sched::predict_n_geometry(dx,&schedule,24,24,23,83,128,21,276,7,2),"uniform_k32_q25_predictor":point_add::frogdrop_sched::predict_n_geometry(dx,&schedule,32,24,25,83,128,21,275,9,3)})
}
fn main(){
 let a:Vec<_>=std::env::args().collect();let path=&a[1];let output=&a[2];
 let mut file=BufReader::new(std::fs::File::open(path).unwrap());let mut hdr=[0u8;16];file.read_exact(&mut hdr).unwrap();assert_eq!(&hdr[..8],b"QECCOPSZ");let count=u64::from_le_bytes(hdr[8..].try_into().unwrap());assert_eq!(count,1_413_812_844);
 let mut reader=zstd::stream::read::Decoder::new(file).unwrap();let mut hash=Shake256::default();hash.update(b"quantum_ecc-fiat-shamir-v2");hash.update(&count.to_le_bytes());let mut op=[0u8;56];let mut canonical=[0u8;49];
 for _ in 0..count{reader.read_exact(&mut op).unwrap();assert!(u32::from_le_bytes(op[..4].try_into().unwrap())<=17);canonical[0]=op[0];canonical[1..].copy_from_slice(&op[8..]);hash.update(&canonical);}
 let mut extra=[0];assert_eq!(reader.read(&mut extra).unwrap(),0);let mut xof=hash.finalize_xof();
 let curve=weierstrass_elliptic_curve::WeierstrassEllipticCurve{a:U256::ZERO,b:U256::from(7),modulus:U256::from_str_radix("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F",16).unwrap(),gx:U256::from_str_radix("79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798",16).unwrap(),gy:U256::from_str_radix("483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8",16).unwrap(),order:U256::from_str_radix("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141",16).unwrap()};
 let mut packets=vec![];let mut flagged=vec![];
 for draw in 0..9024 {let mut rb=[[0u8;32];2];XofReader::read(&mut xof,&mut rb[0]);XofReader::read(&mut xof,&mut rb[1]);let k1=U256::from_le_bytes(rb[0]);let k2=U256::from_le_bytes(rb[1]);let target=curve.mul(curve.gx,curve.gy,k1);let offset=curve.mul(curve.gx,curve.gy,k2);if target.0==offset.0||(target.0.is_zero()&&target.1.is_zero())||(offset.0.is_zero()&&offset.1.is_zero()){continue;}
  let expected=curve.add(target.0,target.1,offset.0,offset.1);let shot=packets.len();let p=point_add::frogdrop_sched::p();let dx=(wide(target.0)+p-wide(offset.0))%p;let dx2=(wide(expected.0)+p-wide(offset.0))%p;
  let d1=diagnosis(dx);let d2=diagnosis(dx2);
  let packet=serde_json::json!({"shot":shot,"draw":draw,"k1":format!("{:064x}",k1),"k2":format!("{:064x}",k2),"target":[format!("{:064x}",target.0),format!("{:064x}",target.1)],"offset":[format!("{:064x}",offset.0),format!("{:064x}",offset.1)],"expected":[format!("{:064x}",expected.0),format!("{:064x}",expected.1)],"division1":d1,"division2":d2});
  if shot==2726{assert_eq!(format!("{:x}",expected.0),"e87f60efa328b508f346f3caca1e81bf7930083db5504a11440b9b96c5bd8737");assert_eq!(format!("{:x}",expected.1),"3985a15c478dfcc9caf1b9ad55f095320c2f3253a8f5474bea89477792b89cae");println!("FIRST_FAIL_PACKET_RECONSTRUCTION_PASS shot=2726 exact_expected_coordinates=true");}
  if !packet["division1"]["candidate_policy_issues"].as_array().unwrap().is_empty()||!packet["division2"]["candidate_policy_issues"].as_array().unwrap().is_empty()||!packet["division1"]["envelope_check"].is_null()||!packet["division2"]["envelope_check"].is_null(){flagged.push(packet.clone());}
  packets.push(packet);
 }
 std::fs::write(output,serde_json::to_vec_pretty(&serde_json::json!({"scope":"exact unchanged failed v6 packet plus classical source-policy diagnostics; not a new validation packet or score","physical_ops":count,"packets":packets})).unwrap()).unwrap();
 let flagged_path=format!("{output}.flagged.json");std::fs::write(flagged_path,serde_json::to_vec_pretty(&flagged).unwrap()).unwrap();println!("PACKET_RECONSTRUCTION_PASS count={} policy_flagged={}",packets.len(),flagged.len());
 for packet in flagged{println!("POLICY_FLAGGED {}",packet);}
}
'''.replace('PRIVATE',tree.as_posix())
(dest/'src/main.rs').write_text(program,encoding='utf8')
(dest/'Cargo.toml').write_text('[package]\nname="q692_failed_packet"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nquantum_ecc={path='+json.dumps(lib.as_posix())+'}\nalloy-primitives="1.5"\nruint="1.12"\nsha3="0.10"\nzstd="0.13"\nserde_json="1"\n',encoding='utf8')
(dest/'source-binding.json').write_text(json.dumps(dict(scope='exact failed packet reconstruction and classical predictor diagnostics; source unchanged',source=str(source),source_sha256={p.relative_to(source).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((source/'src/point_add').rglob('*'))if p.is_file()}),indent=2)+'\n',encoding='utf8')
