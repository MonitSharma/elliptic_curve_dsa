//! A universal commuting permutation; never claims a sampled resource result.
mod io;
use quantum_ecc::circuit::{Op,OperationType as K};
use std::collections::{BTreeSet,BinaryHeap};
use std::cmp::Reverse;
use sha3::{Digest,Sha3_256};
const NO:u64=u64::MAX;
#[derive(Clone)]struct Access{read:Vec<usize>,write:Vec<usize>,qs:Vec<usize>,mr:bool}
fn barrier(o:&Op)->bool{!matches!(o.kind,K::X|K::CX|K::CCX|K::Z|K::CZ|K::CCZ|K::R|K::Hmr|K::Swap|K::BitStore0|K::BitStore1|K::BitInvert)}
fn access(o:&Op,nq:usize)->Access{
 let(mut read,mut write)=(vec![],vec![]);let(t,a,b)=(o.q_target.0 as usize,o.q_control1.0 as usize,o.q_control2.0 as usize);
 match o.kind{
 K::X=>write.push(t),K::CX=>{read.push(a);write.push(t)},K::CCX=>{read.extend([a,b]);write.push(t)},
 K::Z=>read.push(t),K::CZ=>read.extend([a,t]),K::CCZ=>read.extend([a,b,t]),
 K::R|K::Hmr=>write.push(t),K::Swap=>write.extend([a,t]),
 K::BitStore0|K::BitStore1|K::BitInvert=>{},_=>panic!("barrier in access")}
 let mut qs=read.clone();qs.extend(&write);qs.sort_unstable();qs.dedup();
 if o.c_condition.0!=NO{read.push(nq+o.c_condition.0 as usize);}
 if o.c_target.0!=NO{write.push(nq+o.c_target.0 as usize);}
 read.sort_unstable();read.dedup();write.sort_unstable();write.dedup();read.retain(|q|!write.contains(q));
 Access{read,write,qs,mr:o.kind==K::Hmr}
}
fn size(v:&[Op])->(usize,usize){let nq=v.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;let nb=v.iter().flat_map(|o|[o.c_condition.0,o.c_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;(nq,nq+nb)}
fn priority(o:&Op,a:&Access,live:&[bool],root:bool)->i32{let added=a.qs.iter().filter(|&&q|!live[q]).count()as i32;let release=matches!(o.kind,K::R|K::Hmr)&&root&&o.c_condition.0==NO&&live[o.q_target.0 as usize];added-if release{1}else{0}}
fn segment(v:&[Op],offset:usize,nq:usize,slots:usize,live:&mut[bool],root:bool)->Vec<usize>{
 let n=v.len();if n==0{return vec![];}let aa:Vec<_>=v.iter().map(|o|access(o,nq)).collect();
 let mut last=vec![None;slots];let mut readers:Vec<Vec<usize>>=vec![vec![];slots];let mut edges:Vec<Vec<usize>>=vec![vec![];n];let mut deg=vec![0;n];let mut mr=None;
 for(i,a)in aa.iter().enumerate(){let mut deps=vec![];
  for &q in &a.read{if let Some(p)=last[q]{deps.push(p);}readers[q].push(i);}
  for &q in &a.write{if let Some(p)=last[q]{deps.push(p);}deps.append(&mut readers[q]);last[q]=Some(i);}
  if a.mr{if let Some(p)=mr{deps.push(p);}mr=Some(i);}
  deps.sort_unstable();deps.dedup();deps.retain(|&j|j!=i);deg[i]=deps.len();for p in deps{edges[p].push(i);}
 }
 let mut heap=BinaryHeap::new();let mut ready=vec![false;n];let mut versions=vec![0usize;n];let mut wire_ready:Vec<BTreeSet<usize>>=vec![BTreeSet::new();nq];
 let enqueue=|i:usize,heap:&mut BinaryHeap<Reverse<(i32,usize,usize)>>,ready:&mut Vec<bool>,wire_ready:&mut Vec<BTreeSet<usize>>,versions:&Vec<usize>,live:&[bool]|{ready[i]=true;for &q in &aa[i].qs{wire_ready[q].insert(i);}heap.push(Reverse((priority(&v[i],&aa[i],live,root),i,versions[i])));};
 for i in 0..n{if deg[i]==0{enqueue(i,&mut heap,&mut ready,&mut wire_ready,&versions,live);}}
 let mut out=Vec::with_capacity(n);
 while let Some(Reverse((_,i,version)))=heap.pop(){if !ready[i]||version!=versions[i]{continue;}ready[i]=false;for &q in &aa[i].qs{assert!(wire_ready[q].remove(&i));}
  out.push(offset+i);let mut changes=vec![];for &q in &aa[i].qs{if !live[q]{live[q]=true;changes.push(q);}}
  if matches!(v[i].kind,K::R|K::Hmr)&&root&&v[i].c_condition.0==NO{let q=v[i].q_target.0 as usize;if live[q]{live[q]=false;changes.push(q);}}
  changes.sort_unstable();changes.dedup();let mut affected=BTreeSet::new();for q in changes{affected.extend(wire_ready[q].iter().copied());}
  for j in affected{versions[j]+=1;heap.push(Reverse((priority(&v[j],&aa[j],live,root),j,versions[j])));}
  for &j in &edges[i]{deg[j]-=1;if deg[j]==0{enqueue(j,&mut heap,&mut ready,&mut wire_ready,&versions,live);}}
 }assert_eq!(out.len(),n,"dependency cycle");out
}
fn schedule(v:&[Op])->Vec<usize>{let(nq,slots)=size(v);let mut live=vec![false;nq];for o in v{if o.kind==K::AppendToRegister&&o.q_target.0!=NO{live[o.q_target.0 as usize]=true;}}
 let mut out=vec![];let(mut start,mut depth)=(0,0usize);
 for(i,o)in v.iter().enumerate(){if barrier(o){out.extend(segment(&v[start..i],start,nq,slots,&mut live,depth==0));out.push(i);start=i+1;match o.kind{K::PushCondition=>depth+=1,K::PopCondition=>depth-=1,_=>{}}}}
 out.extend(segment(&v[start..],start,nq,slots,&mut live,depth==0));assert_eq!(depth,0);out
}
fn verify(v:&[Op],permutation:&[usize])->bool{
 if permutation.len()!=v.len(){return false;}let mut position=vec![usize::MAX;v.len()];for(new,&old)in permutation.iter().enumerate(){if old>=v.len()||position[old]!=usize::MAX{return false;}position[old]=new;}
 let(nq,slots)=size(v);let mut lower=0;let mut last_write=vec![None;slots];let mut max_read=vec![None;slots];let mut mr=None;
 for(i,o)in v.iter().enumerate(){let p=position[i];if barrier(o){if p!=i{return false;}for j in lower..i{if position[j]<lower||position[j]>=i{return false;}}lower=i+1;last_write.fill(None);max_read.fill(None);mr=None;continue;}
  let a=access(o,nq);for q in a.read{if last_write[q].is_some_and(|w|w>=p){return false;}max_read[q]=Some(max_read[q].map_or(p,|x:usize|x.max(p)));}
  for q in a.write{if last_write[q].is_some_and(|w|w>=p)||max_read[q].is_some_and(|r|r>=p){return false;}last_write[q]=Some(p);max_read[q]=None;}
  if a.mr{if mr.is_some_and(|m|m>=p){return false;}mr=Some(p);}
 }for &p in &position[lower..]{if p<lower{return false;}}true
}
fn hash(v:&[Op])->String{let mut h=Sha3_256::new();for o in v{for x in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(x.to_le_bytes());}}format!("{:x}",h.finalize())}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),3);let v=io::load_ops(&a[1]);let p=schedule(&v);assert!(verify(&v,&p));let out:Vec<_>=p.iter().map(|&i|v[i]).collect();io::save_ops(&format!("{}.ops.bin",a[2]),&out);let moved=p.iter().enumerate().filter(|(a,b)|*a!=**b).count();let raw:Vec<_>=p.iter().flat_map(|&i|(i as u64).to_le_bytes()).collect();std::fs::write(format!("{}.permutation.bin",a[2]),&raw).unwrap();let d=serde_json::json!({"status":"EXACT_COMMUTATION_PERMUTATION_AUDIT_PASS_NOT_A_RESOURCE_SCORE","input":a[1],"ops":v.len(),"input_sha3_256":hash(&v),"output_sha3_256":hash(&out),"permutation_sha256_scope":"SHA3-256 of little-endian u64 source indices","permutation_sha3_256":format!("{:x}",Sha3_256::digest(&raw)),"moved_operations":moved,"all_original_MR_and_conflict_orders_preserved":true});std::fs::write(format!("{}.json",a[2]),serde_json::to_string_pretty(&d).unwrap()).unwrap();println!("moved={moved}");}
#[cfg(test)]mod tests{
 use super::*;use quantum_ecc::circuit::{QubitId,BitId};
 fn op(k:K,a:u64,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(a);o.q_target=QubitId(t);o}
 fn sim(v:&[Op],mut x:u64)->(u64,bool){let mut p=false;for o in v{let b=|q:u64|x>>q&1!=0;match o.kind{K::X=>x^=1<<o.q_target.0,K::CX=>if b(o.q_control1.0){x^=1<<o.q_target.0},K::CCX=>if b(o.q_control1.0)&&b(o.q_control2.0){x^=1<<o.q_target.0},K::Swap=>if b(o.q_control1.0)!=b(o.q_target.0){x^=(1<<o.q_control1.0)|(1<<o.q_target.0)},K::Z=>p^=b(o.q_target.0),K::CZ=>p^=b(o.q_control1.0)&&b(o.q_target.0),K::CCZ=>p^=b(o.q_control1.0)&&b(o.q_control2.0)&&b(o.q_target.0),K::R=>{assert!(!b(o.q_target.0));},_=>panic!("unsupported")}}(x,p)}
 #[test]fn advances_cleanup_over_independent_allocation(){let v=vec![op(K::X,NO,0),op(K::X,NO,1),op(K::X,NO,0),op(K::R,NO,0),op(K::X,NO,1),op(K::R,NO,1)];let p=schedule(&v);assert!(verify(&v,&p));assert_eq!(p,vec![0,2,3,1,4,5]);let w:Vec<_>=p.iter().map(|&i|v[i]).collect();assert_eq!(sim(&v,0),sim(&w,0));}
 #[test]fn target_phase_cannot_cross_toggle(){let v=vec![op(K::X,NO,0),op(K::Z,NO,0)];assert!(!verify(&v,&[1,0]));}
 #[test]fn same_control_reads_can_commute(){let v=vec![op(K::CX,0,1),op(K::CX,0,2)];assert!(verify(&v,&[1,0]));for x in 0..8{assert_eq!(sim(&v,x),sim(&[v[1],v[0]],x));}}
 #[test]fn write_after_multiple_readers_waits_for_both(){let v=vec![op(K::CX,0,1),op(K::CX,0,2),op(K::X,NO,0)];assert!(!verify(&v,&[0,2,1]));assert!(!verify(&v,&[2,0,1]));}
 #[test]fn original_measurement_order_is_global(){let mut a=op(K::Hmr,NO,0);a.c_target=BitId(0);let mut b=op(K::Hmr,NO,1);b.c_target=BitId(1);assert!(!verify(&[a,b],&[1,0]));}
 #[test]fn classical_write_cannot_cross_condition_read(){let mut x=op(K::X,NO,0);x.c_condition=BitId(0);let mut b=Op::empty();b.kind=K::BitInvert;b.c_target=BitId(0);assert!(!verify(&[x,b],&[1,0]));}
 #[test]fn captured_guard_boundaries_are_fences(){let mut push=Op::empty();push.kind=K::PushCondition;push.c_condition=BitId(0);let v=vec![op(K::X,NO,0),push,op(K::X,NO,1)];assert!(!verify(&v,&[2,1,0]));}
 #[test]fn duplicate_missing_and_out_of_range_rejected(){let v=vec![op(K::X,NO,0),op(K::X,NO,1)];for p in [vec![0,0],vec![0],vec![0,2]]{assert!(!verify(&v,&p));}}
 #[test]fn random_unitary_networks_preserve_all_basis_values_and_phases(){let mut rng=17u64;for _ in 0..100{let mut v=vec![];for _ in 0..64{rng=rng.wrapping_mul(6364136223846793005).wrapping_add(1);let t=rng%4;let a=(t+1+(rng>>8)%3)%4;let b=(0..4).find(|&q|q!=t&&q!=a).unwrap();let k=[K::X,K::CX,K::CCX,K::Z,K::CZ,K::CCZ,K::Swap][((rng>>16)%7)as usize];let mut o=op(k,if matches!(k,K::X|K::Z){NO}else{a},t);if matches!(k,K::CCX|K::CCZ){o.q_control2=QubitId(b);}v.push(o);}let p=schedule(&v);assert!(verify(&v,&p));let w:Vec<_>=p.iter().map(|&i|v[i]).collect();for x in 0..16{assert_eq!(sim(&v,x),sim(&w,x));}}}
}
