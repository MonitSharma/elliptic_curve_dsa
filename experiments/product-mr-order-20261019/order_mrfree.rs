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
 // The protected simulator draws once for every R and Hmr, even when the
 // effective guard is false. Preserve this entire physical event sequence.
 Access{read,write,qs,mr:matches!(o.kind,K::R|K::Hmr)}
}
fn size(v:&[Op])->(usize,usize){let nq=v.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;let nb=v.iter().flat_map(|o|[o.c_condition.0,o.c_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;(nq,nq+nb)}
fn priority(o:&Op,a:&Access,live:&[bool],root:bool,closed:Option<&[usize]>)->i32{let added=a.qs.iter().filter(|&&q|!live[q]).count()as i32;if let Some(c)=closed{return added-c.len()as i32;}let release=matches!(o.kind,K::R|K::Hmr)&&root&&o.c_condition.0==NO&&live[o.q_target.0 as usize];added-if release{1}else{0}}
fn segment(v:&[Op],offset:usize,nq:usize,_slots:usize,live:&mut[bool],root:bool,closes:Option<&Clean>)->Vec<usize>{
 let n=v.len();if n==0{return vec![];}let mut aa:Vec<_>=v.iter().map(|o|access(o,nq)).collect();
 let mut active_slots:Vec<_>=aa.iter().flat_map(|a|a.read.iter().chain(a.write.iter()).copied()).collect();active_slots.sort_unstable();active_slots.dedup();let slots=active_slots.len();
 let mut active_q:Vec<_>=aa.iter().flat_map(|a|a.qs.iter().copied()).collect();active_q.sort_unstable();active_q.dedup();
 for a in &mut aa{for q in a.read.iter_mut().chain(a.write.iter_mut()){*q=active_slots.binary_search(q).unwrap();}}
 let mut last=vec![None;slots];let mut readers:Vec<Vec<usize>>=vec![vec![];slots];let mut edges:Vec<Vec<usize>>=vec![vec![];n];let mut deg=vec![0;n];
 for(i,a)in aa.iter().enumerate(){let mut deps=vec![];
  for &q in &a.read{if let Some(p)=last[q]{deps.push(p);}readers[q].push(i);}
  for &q in &a.write{if let Some(p)=last[q]{deps.push(p);}deps.append(&mut readers[q]);last[q]=Some(i);}
  
  deps.sort_unstable();deps.dedup();deps.retain(|&j|j!=i);deg[i]=deps.len();for p in deps{edges[p].push(i);}
 }
 let mut heap=BinaryHeap::new();let mut ready=vec![false;n];let mut versions=vec![0usize;n];let mut wire_ready:Vec<BTreeSet<usize>>=vec![BTreeSet::new();active_q.len()];
 let enqueue=|i:usize,heap:&mut BinaryHeap<Reverse<(i32,usize,usize)>>,ready:&mut Vec<bool>,wire_ready:&mut Vec<BTreeSet<usize>>,versions:&Vec<usize>,live:&[bool]|{ready[i]=true;for &q in &aa[i].qs{wire_ready[active_q.binary_search(&q).unwrap()].insert(i);}heap.push(Reverse((priority(&v[i],&aa[i],live,root,closes.map(|c|c.get(offset+i))),i,versions[i])));};
 for i in 0..n{if deg[i]==0{enqueue(i,&mut heap,&mut ready,&mut wire_ready,&versions,live);}}
 let mut out=Vec::with_capacity(n);
 while let Some(Reverse((_,i,version)))=heap.pop(){if !ready[i]||version!=versions[i]{continue;}ready[i]=false;for &q in &aa[i].qs{assert!(wire_ready[active_q.binary_search(&q).unwrap()].remove(&i));}
  out.push(offset+i);let mut changes=vec![];for &q in &aa[i].qs{if !live[q]{live[q]=true;changes.push(q);}}
  if let Some(c)=closes{for &q in c.get(offset+i){assert!(aa[i].qs.contains(&q));if live[q]{live[q]=false;changes.push(q);}}}
  else if matches!(v[i].kind,K::R|K::Hmr)&&root&&v[i].c_condition.0==NO{let q=v[i].q_target.0 as usize;if live[q]{live[q]=false;changes.push(q);}}
  changes.sort_unstable();changes.dedup();let mut affected=BTreeSet::new();for q in changes{affected.extend(wire_ready[active_q.binary_search(&q).unwrap()].iter().copied());}
  for j in affected{versions[j]+=1;heap.push(Reverse((priority(&v[j],&aa[j],live,root,closes.map(|c|c.get(offset+j))),j,versions[j])));}
  for &j in &edges[i]{deg[j]-=1;if deg[j]==0{enqueue(j,&mut heap,&mut ready,&mut wire_ready,&versions,live);}}
 }assert_eq!(out.len(),n,"dependency cycle");out
}
fn schedule(v:&[Op],closes:Option<&Clean>)->Vec<usize>{let(nq,slots)=size(v);let mut live=vec![false;nq];for o in v{if o.kind==K::AppendToRegister&&o.q_target.0!=NO{live[o.q_target.0 as usize]=true;}}
 let mut out=vec![];let(mut start,mut depth)=(0,0usize);
 for(i,o)in v.iter().enumerate(){if barrier(o){out.extend(segment(&v[start..i],start,nq,slots,&mut live,depth==0,closes));out.push(i);start=i+1;match o.kind{K::PushCondition=>depth+=1,K::PopCondition=>depth-=1,_=>{}}}}
 out.extend(segment(&v[start..],start,nq,slots,&mut live,depth==0,closes));assert_eq!(depth,0);out
}
fn verify(v:&[Op],permutation:&[usize])->bool{
 if permutation.len()!=v.len(){return false;}let mut position=vec![usize::MAX;v.len()];for(new,&old)in permutation.iter().enumerate(){if old>=v.len()||position[old]!=usize::MAX{return false;}position[old]=new;}
 let(nq,slots)=size(v);let mut lower=0;let mut last_write=vec![None;slots];let mut max_read=vec![None;slots];let mut touched=vec![];
 for(i,o)in v.iter().enumerate(){let p=position[i];if barrier(o){if p!=i{return false;}for j in lower..i{if position[j]<lower||position[j]>=i{return false;}}lower=i+1;for q in touched.drain(..){last_write[q]=None;max_read[q]=None;}continue;}
  let a=access(o,nq);for q in a.read{touched.push(q);if last_write[q].is_some_and(|w|w>=p){return false;}max_read[q]=Some(max_read[q].map_or(p,|x:usize|x.max(p)));}
  for q in a.write{touched.push(q);if last_write[q].is_some_and(|w|w>=p)||max_read[q].is_some_and(|r|r>=p){return false;}last_write[q]=Some(p);max_read[q]=None;}
  
 }for &p in &position[lower..]{if p<lower{return false;}}true
}
fn hash(v:&[Op])->String{let mut h=Sha3_256::new();for o in v{for x in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(x.to_le_bytes());}}format!("{:x}",h.finalize())}
struct Clean{starts:Vec<u32>,roles:Vec<usize>}
impl Clean{fn get(&self,i:usize)->&[usize]{&self.roles[self.starts[i]as usize..self.starts[i+1]as usize]}
 fn load(path:&str,v:&[Op])->Self{let raw=std::fs::read(path).unwrap();assert_eq!(&raw[..8],b"GRCLEAN1");let word=|i:usize|u64::from_le_bytes(raw[i..i+8].try_into().unwrap());assert_eq!(word(8)as usize,v.len());assert_eq!(&raw[16..80],hash(v).as_bytes());let n=word(80)as usize;assert_eq!(raw.len(),88+n*16);let mut starts=vec![0u32;v.len()+1];let mut roles=vec![];let mut cursor=0;let mut prior=None;
  for k in 0..n{let i=word(88+k*16)as usize;let q=word(96+k*16)as usize;assert!(i<v.len());assert!(prior.is_none_or(|p|p<(i,q)));prior=Some((i,q));assert!([v[i].q_control1.0,v[i].q_control2.0,v[i].q_target.0].contains(&(q as u64)));while cursor<=i{starts[cursor]=roles.len().try_into().unwrap();cursor+=1;}roles.push(q);}
  while cursor<=v.len(){starts[cursor]=roles.len().try_into().unwrap();cursor+=1;}Self{starts,roles}
 }}
fn main(){let a:Vec<_>=std::env::args().collect();assert!(a.len()==4||a.len()==5);let mode=&a[3];assert!(["full","core","clean"].contains(&mode.as_str()));let mut v=io::load_ops(&a[1]);let full_hash=hash(&v);let full_count=v.len();let tail=if mode=="full"{vec![]}else{let t=v.split_off(v.len()-96);for x in t.chunks_exact(2){assert_eq!(x[0],x[1]);assert_eq!(x[0].kind,K::X);assert!(x[0].q_target.0<=1);assert_eq!(x[0].c_condition.0,NO);}t};let core_hash=hash(&v);let clean=if mode=="clean"{assert_eq!(a.len(),5);Some(Clean::load(&a[4],&v))}else{None};let mut p=schedule(&v,clean.as_ref());assert!(verify(&v,&p));let core_len=v.len();p.extend(core_len..full_count);v.extend(tail);assert!(verify(&v,&p));let map=event_map(&v,&p);let mut event_bytes=b"RNGPERM1".to_vec();event_bytes.extend((map.len()as u64).to_le_bytes());event_bytes.extend(full_hash.as_bytes());for &i in &map{event_bytes.extend(i.to_le_bytes());}std::fs::write(format!("{}.rng-map.bin",a[2]),&event_bytes).unwrap();let out:Vec<_>=p.iter().map(|&i|v[i]).collect();io::save_ops(&format!("{}.ops.bin",a[2]),&out);let moved=p.iter().enumerate().filter(|(a,b)|*a!=**b).count();let raw:Vec<_>=p.iter().flat_map(|&i|(i as u64).to_le_bytes()).collect();std::fs::write(format!("{}.permutation.bin",a[2]),&raw).unwrap();let d=serde_json::json!({"status":"EXACT_COMMUTING_CHANNEL_WITH_RNG_BIJECTION_AUDIT_PASS","mode":mode,"ops":v.len(),"input_full_sha3_256":full_hash,"core_sha3_256":core_hash,"output_full_sha3_256":hash(&out),"permutation_sha3_256":format!("{:x}",Sha3_256::digest(&raw)),"moved_operations":moved,"identity_tail_pinned":mode!="full","all_quantum_classical_conflict_orders_preserved":true,"outcomes_match_under_exported_event_bijection":true,"physical_rng_order_may_change":true,"clean_annotations_affect_only_heuristic":mode=="clean","rng_events":map.len(),"rng_map_sha3_256":format!("{:x}",Sha3_256::digest(&event_bytes))});std::fs::write(format!("{}.json",a[2]),serde_json::to_string_pretty(&d).unwrap()).unwrap();println!("mode={mode} moved={moved}");}

#[cfg(test)]mod tests{
 use super::*;use quantum_ecc::circuit::{QubitId,BitId};
 fn op(k:K,a:u64,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(a);o.q_target=QubitId(t);o}
 fn sim(v:&[Op],mut x:u64)->(u64,bool){let mut p=false;for o in v{let b=|q:u64|x>>q&1!=0;match o.kind{K::X=>x^=1<<o.q_target.0,K::CX=>if b(o.q_control1.0){x^=1<<o.q_target.0},K::CCX=>if b(o.q_control1.0)&&b(o.q_control2.0){x^=1<<o.q_target.0},K::Swap=>if b(o.q_control1.0)!=b(o.q_target.0){x^=(1<<o.q_control1.0)|(1<<o.q_target.0)},K::Z=>p^=b(o.q_target.0),K::CZ=>p^=b(o.q_control1.0)&&b(o.q_target.0),K::CCZ=>p^=b(o.q_control1.0)&&b(o.q_control2.0)&&b(o.q_target.0),K::R=>{assert!(!b(o.q_target.0));},_=>panic!("unsupported")}}(x,p)}
 #[test]fn advances_cleanup_over_independent_allocation(){let v=vec![op(K::X,NO,0),op(K::X,NO,1),op(K::X,NO,0),op(K::R,NO,0),op(K::X,NO,1),op(K::R,NO,1)];let p=schedule(&v,None);assert!(verify(&v,&p));assert_eq!(p,vec![0,2,3,1,4,5]);let w:Vec<_>=p.iter().map(|&i|v[i]).collect();assert_eq!(sim(&v,0),sim(&w,0));}
 #[test]fn target_phase_cannot_cross_toggle(){let v=vec![op(K::X,NO,0),op(K::Z,NO,0)];assert!(!verify(&v,&[1,0]));}
 #[test]fn same_control_reads_can_commute(){let v=vec![op(K::CX,0,1),op(K::CX,0,2)];assert!(verify(&v,&[1,0]));for x in 0..8{assert_eq!(sim(&v,x),sim(&[v[1],v[0]],x));}}
 #[test]fn write_after_multiple_readers_waits_for_both(){let v=vec![op(K::CX,0,1),op(K::CX,0,2),op(K::X,NO,0)];assert!(!verify(&v,&[0,2,1]));assert!(!verify(&v,&[2,0,1]));}
 #[test]fn independent_measurement_labels_can_reorder(){let mut a=op(K::Hmr,NO,0);a.c_target=BitId(0);let mut b=op(K::Hmr,NO,1);b.c_target=BitId(1);assert!(verify(&[a,b],&[1,0]));}
 #[test]fn independent_resets_can_reorder_with_an_event_bijection(){let a=op(K::R,NO,0);let mut b=op(K::Hmr,NO,1);b.c_target=BitId(0);assert!(verify(&[a,b],&[1,0]));let mut c=op(K::R,NO,2);c.c_condition=BitId(1);assert!(verify(&[a,c],&[1,0]));}
 #[test]fn classical_write_cannot_cross_condition_read(){let mut x=op(K::X,NO,0);x.c_condition=BitId(0);let mut b=Op::empty();b.kind=K::BitInvert;b.c_target=BitId(0);assert!(!verify(&[x,b],&[1,0]));}
 #[test]fn captured_guard_boundaries_are_fences(){let mut push=Op::empty();push.kind=K::PushCondition;push.c_condition=BitId(0);let v=vec![op(K::X,NO,0),push,op(K::X,NO,1)];assert!(!verify(&v,&[2,1,0]));}
 #[test]fn duplicate_missing_and_out_of_range_rejected(){let v=vec![op(K::X,NO,0),op(K::X,NO,1)];for p in [vec![0,0],vec![0],vec![0,2]]{assert!(!verify(&v,&p));}}
 #[test]fn random_unitary_networks_preserve_all_basis_values_and_phases(){let mut rng=17u64;for _ in 0..100{let mut v=vec![];for _ in 0..64{rng=rng.wrapping_mul(6364136223846793005).wrapping_add(1);let t=rng%4;let a=(t+1+(rng>>8)%3)%4;let b=(0..4).find(|&q|q!=t&&q!=a).unwrap();let k=[K::X,K::CX,K::CCX,K::Z,K::CZ,K::CCZ,K::Swap][((rng>>16)%7)as usize];let mut o=op(k,if matches!(k,K::X|K::Z){NO}else{a},t);if matches!(k,K::CCX|K::CCZ){o.q_control2=QubitId(b);}v.push(o);}let p=schedule(&v,None);assert!(verify(&v,&p));let w:Vec<_>=p.iter().map(|&i|v[i]).collect();for x in 0..16{assert_eq!(sim(&v,x),sim(&w,x));}}}
}

#[cfg(test)]#[path="legacy.rs"]mod legacy;
#[cfg(test)]mod compact_controls{use super::*;#[test]fn random_source_permutations_equal_legacy(){use quantum_ecc::circuit::QubitId;let mut seed=43u64;for _ in 0..100{let mut v=vec![];for _ in 0..64{seed=seed.wrapping_mul(6364136223846793005).wrapping_add(1);let t=seed%8;let a=(t+1+(seed>>8)%7)%8;let mut o=Op::empty();o.kind=if seed>>16&1!=0{K::CX}else{K::X};o.q_target=QubitId(t);if o.kind==K::CX{o.q_control1=QubitId(a);}v.push(o);}assert_eq!(schedule(&v,None),legacy::schedule(&v));}}}

fn event_map(v:&[Op],p:&[usize])->Vec<u32>{let mut old=vec![u32::MAX;v.len()];let mut count=0u32;for(i,o)in v.iter().enumerate(){if matches!(o.kind,K::R|K::Hmr){old[i]=count;count=count.checked_add(1).unwrap();}}let mut map=vec![];let mut seen=vec![false;count as usize];for &i in p{let k=old[i];if k!=u32::MAX{assert!(!seen[k as usize]);seen[k as usize]=true;map.push(k);}}assert_eq!(map.len(),count as usize);assert!(seen.iter().all(|x|*x));map}
#[cfg(test)]mod event_controls{use super::*;use quantum_ecc::circuit::{QubitId,BitId};fn fixture()->Vec<Op>{let mut a=Op::empty();a.kind=K::Hmr;a.q_target=QubitId(0);a.c_target=BitId(0);let mut b=a;b.q_target=QubitId(1);b.c_target=BitId(1);vec![a,b]}
#[test]fn event_labels_follow_the_full_permutation(){let v=fixture();assert!(verify(&v,&[1,0]));assert_eq!(event_map(&v,&[1,0]),vec![1,0]);}
#[test]#[should_panic]fn duplicate_event_is_rejected(){event_map(&fixture(),&[0,0]);}
#[test]#[should_panic]fn missing_event_is_rejected(){event_map(&fixture(),&[0]);}
}
