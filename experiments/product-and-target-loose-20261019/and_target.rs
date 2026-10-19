//! Exact source-only temporary-AND absorption; no source/input packet tuning.
mod io;
use quantum_ecc::circuit::{Op,OperationType as K,QubitId};
use sha3::{Digest,Sha3_256};
use std::collections::{BTreeSet,HashSet,HashMap};
const NO:u64=u64::MAX;
#[derive(Clone,Debug)]struct Site{start:usize,end:usize,mr:usize,a:u64,b:u64,t:u64,bit:u64,targets:Vec<u64>,queries:Vec<usize>}
fn gate(k:K,a:u64,b:u64,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(a);o.q_target=QubitId(t);if k==K::CCX{o.q_control2=QubitId(b);}o.validate();o}
fn discover(v:&[Op])->Vec<Site>{
 let nq=v.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&x|x!=NO).max().unwrap_or(0)as usize+1;
 let nb=v.iter().flat_map(|o|[o.c_target.0,o.c_condition.0]).filter(|&x|x!=NO).max().unwrap_or(0)as usize+1;
 let pinned:HashSet<_>=v.iter().filter(|o|o.kind==K::AppendToRegister&&o.q_target.0!=NO).map(|o|o.q_target.0).collect();
 let pinned_b:HashSet<_>=v.iter().filter(|o|o.kind==K::AppendToRegister&&o.c_target.0!=NO).map(|o|o.c_target.0).collect();
 let mut depth=0usize;let mut depths=vec![0;v.len()];for(i,o)in v.iter().enumerate(){depths[i]=depth;if o.kind==K::PushCondition{depth+=1;}if o.kind==K::PopCondition{depth=depth.checked_sub(1).unwrap();}}assert_eq!(depth,0);
 let mut safe=vec![true;nb];let mut hmr_safe=HashSet::new();for(i,o)in v.iter().enumerate().rev(){if i>0&&o.kind==K::CZ&&o.c_condition.0!=NO&&v[i-1].kind==K::Hmr&&v[i-1].c_target.0==o.c_condition.0&&safe[o.c_condition.0 as usize]{hmr_safe.insert(i-1);}if o.c_target.0!=NO{safe[o.c_target.0 as usize]=matches!(o.kind,K::Hmr|K::BitStore0|K::BitStore1)&&depths[i]==0&&o.c_condition.0==NO;}if o.c_condition.0!=NO{safe[o.c_condition.0 as usize]=false;}}
 let qubits=|o:&Op|[o.q_control1.0,o.q_control2.0,o.q_target.0];
 let mut touches:Vec<Vec<usize>>=vec![vec![];nq];let mut writes:Vec<Vec<usize>>=vec![vec![];nq];
 for(i,o)in v.iter().enumerate(){for q in qubits(o){if q!=NO{touches[q as usize].push(i);}}if matches!(o.kind,K::X|K::CX|K::CCX|K::R|K::Hmr|K::Swap){writes[o.q_target.0 as usize].push(i);if o.kind==K::Swap{writes[o.q_control1.0 as usize].push(i);}}}
 let mut zero=vec![true;nq];for &q in &pinned{zero[q as usize]=false;}let mut found=vec![];
 for(i,o)in v.iter().enumerate(){
  if o.kind==K::CCX&&depths[i]==0&&o.c_condition.0==NO&&zero[o.q_target.0 as usize]&&!pinned.contains(&o.q_target.0){
   let(a,b,t)=(o.q_control1.0,o.q_control2.0,o.q_target.0);let ts=&touches[t as usize];let lo=ts.partition_point(|&j|j<=i);let mut h=None;let mut targets=BTreeSet::new();let mut queries=vec![];
   for &j in &ts[lo..]{let q=&v[j];if q.kind==K::Hmr{h=Some(j);break;}if q.kind!=K::CX||q.q_control1.0!=t||q.c_condition.0!=NO||depths[j]!=0||[a,b,t].contains(&q.q_target.0){break;}if !targets.remove(&q.q_target.0){targets.insert(q.q_target.0);}queries.push(j);}
   if let Some(end)=h{if !queries.is_empty(){if let Some(z)=v.get(end+1){let hh=&v[end];let bit=hh.c_target.0;
    let stable=[a,b].iter().all(|&q|{let ws=&writes[q as usize];ws.get(ws.partition_point(|&j|j<=i)).map_or(true,|&j|j>=end)});
    let all_targets:BTreeSet<_>=queries.iter().map(|&j|v[j].q_target.0).collect();
    let isolated=all_targets.iter().all(|&q|{let ts=&touches[q as usize];let lo=ts.partition_point(|&j|j<=i);let hi=ts.partition_point(|&j|j<end);ts[lo..hi].iter().all(|j|queries.binary_search(j).is_ok())});
    if stable&&isolated&&depths[end]==0&&hh.q_target.0==t&&hh.c_condition.0==NO&&z.kind==K::CZ&&z.c_condition.0==bit&&((z.q_control1.0==a&&z.q_target.0==b)||(z.q_control1.0==b&&z.q_target.0==a))&&hmr_safe.contains(&end)&&!pinned_b.contains(&bit){found.push(Site{start:i,end:end+2,mr:end,a,b,t,bit,targets:targets.into_iter().collect(),queries});}
   }}}
  }
  if matches!(o.kind,K::X|K::CX|K::CCX|K::R|K::Hmr|K::Swap)&&o.q_target.0!=NO{zero[o.q_target.0 as usize]=matches!(o.kind,K::R|K::Hmr)&&depths[i]==0&&o.c_condition.0==NO;if o.kind==K::Swap{zero[o.q_control1.0 as usize]=false;}}
 }found
}

fn emit(s:&Site)->Vec<Op>{let mut v=vec![];if let Some(&d)=s.targets.first(){for &e in &s.targets[1..]{v.push(gate(K::CX,d,NO,e));}v.push(gate(K::CCX,s.a,s.b,d));for &e in &s.targets[1..]{v.push(gate(K::CX,d,NO,e));}}v}
fn hash(v:&[Op])->String{let mut h=Sha3_256::new();for o in v{for x in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(x.to_le_bytes());}}format!("{:x}",h.finalize())}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),3);let v=io::load_ops(&a[1]);let input_hash=hash(&v);assert_eq!(input_hash,"429af1c31b54064e17e7602be516b519c066c241e218d56f002287ea02b16842");let sites=discover(&v);let mut out=Vec::with_capacity(v.len());let mut removed=HashSet::new();let mut edits=HashMap::new();let mut deleted=HashSet::new();let mut rows=vec![];
 for s in &sites{assert!(edits.insert(s.start,emit(s)).is_none());for j in s.queries.iter().copied().chain([s.mr,s.mr+1]){assert!(deleted.insert(j),"overlapping edited instruction");}removed.insert(s.mr);rows.push(serde_json::json!({"start":s.start,"end_exclusive":s.end,"removed_Hmr":s.mr,"removed_bit":s.bit,"a":s.a,"b":s.b,"temporary":s.t,"targets":s.targets,"query_indices":s.queries}));}
 assert!(edits.keys().all(|i|!deleted.contains(i)));for(i,o)in v.iter().enumerate(){if let Some(w)=edits.get(&i){out.extend_from_slice(w);}else if !deleted.contains(&i){out.push(*o);}}

 let mut event_map=vec![];let mut old_events=0u32;for(i,o)in v.iter().enumerate(){if matches!(o.kind,K::R|K::Hmr){if !removed.contains(&i){event_map.push(old_events);}old_events+=1;}}
 let mut map=b"RNGSUBS1".to_vec();map.extend((old_events as u64).to_le_bytes());map.extend((event_map.len()as u64).to_le_bytes());map.extend(input_hash.as_bytes());for &e in &event_map{map.extend(e.to_le_bytes());}std::fs::write(format!("{}.rng-map.bin",a[2]),map).unwrap();
 let result=serde_json::json!({"status":"EXACT_NONCONTIGUOUS_AND_TARGET_DIAGNOSTIC_NOT_A_SCORE","input_count":v.len(),"output_count":out.len(),"input_full_sha3_256":input_hash,"output_full_sha3_256":hash(&out),"sites":rows,"site_count":sites.len(),"parity_zero_products_removed":sites.iter().filter(|s|s.targets.is_empty()).count(),"original_rng_events":old_events,"remaining_rng_events":event_map.len(),"scope":"No final Q/T score, native reproduction, statistical gate or nonce selection."});io::save_ops(&format!("{}.ops.bin",a[2]),&out);std::fs::write(format!("{}.json",a[2]),serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("sites={} empty={} ops={} -> {}",sites.len(),result["parity_zero_products_removed"],v.len(),out.len());}
#[cfg(test)]mod tests{
 use super::*;use quantum_ecc::{sim::Simulator,circuit::{BitId,RegisterId}};use sha3::digest::XofReader;
 struct Bytes{data:Vec<u8>,at:usize}impl XofReader for Bytes{fn read(&mut self,x:&mut[u8]){x.copy_from_slice(&self.data[self.at..self.at+x.len()]);self.at+=x.len();}}
 fn fixture(targets:&[u64])->Vec<Op>{let mut v=vec![];for q in [0,1,3,4,5]{let mut r=Op::empty();r.kind=K::AppendToRegister;r.q_target=QubitId(q);r.r_target=RegisterId(0);v.push(r);}v.push(gate(K::CCX,0,1,2));for &q in targets{v.push(gate(K::CX,2,NO,q));}let mut h=Op::empty();h.kind=K::Hmr;h.q_target=QubitId(2);h.c_target=BitId(0);v.push(h);let mut z=gate(K::CZ,0,NO,1);z.c_condition=BitId(0);v.push(z);v}
 fn run(v:&[Op],bits:u64,m:u64)->(Vec<u64>,u64,u64,[u8;64]){let mut data=vec![];for _ in v.iter().filter(|o|matches!(o.kind,K::R|K::Hmr)){data.extend(m.to_le_bytes());}data.extend([0x5a;64]);let mut rng=Bytes{data,at:0};let mut s=Simulator::new(6,1,&mut rng);for q in [0,1,3,4,5]{s.qubits[q]=if bits>>q&1!=0{u64::MAX}else{0};}s.phase=0x5555aaaaffff0000;s.apply_iter(v.iter());let state=(s.qubits.clone(),s.phase,s.stats.toffoli_gates);drop(s);let mut tail=[0;64];rng.read(&mut tail);assert_eq!(rng.at,rng.data.len());(state.0,state.1,state.2,tail)}
 #[test]fn arbitrary_dirty_outputs_and_both_outcomes_preserve_values_phase_and_continuation(){for ts in [vec![3],vec![3,4],vec![3,4,5],vec![3,4,3],vec![3,3]]{let v=fixture(&ts);let sites=discover(&v);assert_eq!(sites.len(),1);let s=&sites[0];let mut w=v[..s.start].to_vec();w.extend(emit(s));for bits in 0..64{for m in [0,u64::MAX,0x5555aaaaffff0000]{let x=run(&v,bits,m);let y=run(&w,bits,m);assert_eq!(x.0,y.0);assert_eq!(x.1,y.1);assert_eq!(x.3,y.3);assert_eq!(x.2-y.2,if s.targets.is_empty(){64}else{0});}}}}
 #[test]fn dirty_temporary_is_not_accepted(){let mut v=fixture(&[3]);v.insert(5,gate(K::X,NO,NO,2));assert!(discover(&v).is_empty());}
 #[test]fn registered_cleanup_bit_is_not_accepted(){let mut v=fixture(&[3]);let mut r=Op::empty();r.kind=K::AppendToRegister;r.c_target=BitId(0);r.r_target=RegisterId(1);v.insert(0,r);assert!(discover(&v).is_empty());}
 #[test]fn later_cleanup_bit_reader_is_not_accepted(){let mut v=fixture(&[3]);let mut z=gate(K::Z,NO,NO,5);z.c_condition=BitId(0);v.push(z);assert!(discover(&v).is_empty());}
 #[test]fn fanout_into_control_is_not_accepted(){assert!(discover(&fixture(&[0])).is_empty());}
 #[test]fn guarded_constructor_is_not_accepted(){let mut v=fixture(&[3]);v[5].c_condition=BitId(0);assert!(discover(&v).is_empty());}
 #[test]fn independent_intervening_operations_are_retained(){let mut v=fixture(&[3,4]);v.insert(7,gate(K::X,NO,NO,5));let ss=discover(&v);assert_eq!(ss.len(),1);let s=&ss[0];let mut w=v[..s.start].to_vec();w.extend(emit(s));for(i,o)in v.iter().enumerate().skip(s.start+1){if !s.queries.contains(&i)&&i!=s.mr&&i!=s.mr+1{w.push(*o);}}for bits in 0..64{for m in [0,u64::MAX]{let x=run(&v,bits,m);let y=run(&w,bits,m);assert_eq!(x,y);}}}
 #[test]fn intervening_target_reader_is_rejected(){let mut v=fixture(&[3,4]);v.insert(7,gate(K::CX,3,NO,5));assert!(discover(&v).is_empty());}
 #[test]fn intervening_target_writer_is_rejected(){let mut v=fixture(&[3,4]);v.insert(7,gate(K::X,NO,NO,4));assert!(discover(&v).is_empty());}
 #[test]fn intervening_control_writer_is_rejected(){let mut v=fixture(&[3,4]);v.insert(7,gate(K::X,NO,NO,0));assert!(discover(&v).is_empty());}

}
