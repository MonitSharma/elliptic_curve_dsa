"""Remove only the global RNG chain; retain all real data dependencies."""
from pathlib import Path
r=Path(__file__).resolve().parent;e=r.parent
s=(e/'product-order-combined-20261019/order_fast.rs').read_text(encoding='utf-8')
build='if a.mr{if let Some(p)=mr{deps.push(p);}mr=Some(i);}'
audit='if a.mr{if mr.is_some_and(|m|m>=p){return false;}mr=Some(p);}'
assert s.count(build)==1 and s.count(audit)==1
s=s.replace(build,'').replace(audit,'').replace('let mut mr=None;','').replace('mr=None;','')
s=s.replace('original_measurement_order_is_global','independent_measurement_labels_can_reorder')
s=s.replace('reset_and_measurement_share_one_rng_chain','independent_resets_can_reorder_with_an_event_bijection')
s=s.replace('assert!(!verify(&[a,b],&[1,0]));','assert!(verify(&[a,b],&[1,0]));')
s=s.replace('assert!(!verify(&[a,c],&[1,0]));','assert!(verify(&[a,c],&[1,0]));')
s=s.replace('"EXACT_COMMUTATION_PERMUTATION_AUDIT_PASS_NOT_A_RESOURCE_SCORE"','"EXACT_COMMUTING_CHANNEL_WITH_RNG_BIJECTION_AUDIT_PASS"')
s=s.replace('"all_original_R_Hmr_and_conflict_orders_preserved":true','"all_quantum_classical_conflict_orders_preserved":true,"outcomes_match_under_exported_event_bijection":true,"physical_rng_order_may_change":true')
s=s.replace('let out:Vec<_>=p.iter().map(|&i|v[i]).collect();','''let map=event_map(&v,&p);let mut event_bytes=b"RNGPERM1".to_vec();event_bytes.extend((map.len()as u64).to_le_bytes());event_bytes.extend(full_hash.as_bytes());for &i in &map{event_bytes.extend(i.to_le_bytes());}std::fs::write(format!("{}.rng-map.bin",a[2]),&event_bytes).unwrap();let out:Vec<_>=p.iter().map(|&i|v[i]).collect();''')
s=s.replace('"clean_annotations_affect_only_heuristic":mode=="clean"','"clean_annotations_affect_only_heuristic":mode=="clean","rng_events":map.len(),"rng_map_sha3_256":format!("{:x}",Sha3_256::digest(&event_bytes))')
s+='''
fn event_map(v:&[Op],p:&[usize])->Vec<u32>{let mut old=vec![u32::MAX;v.len()];let mut count=0u32;for(i,o)in v.iter().enumerate(){if matches!(o.kind,K::R|K::Hmr){old[i]=count;count=count.checked_add(1).unwrap();}}let mut map=vec![];let mut seen=vec![false;count as usize];for &i in p{let k=old[i];if k!=u32::MAX{assert!(!seen[k as usize]);seen[k as usize]=true;map.push(k);}}assert_eq!(map.len(),count as usize);assert!(seen.iter().all(|x|*x));map}
#[cfg(test)]mod event_controls{use super::*;use quantum_ecc::circuit::{QubitId,BitId};fn fixture()->Vec<Op>{let mut a=Op::empty();a.kind=K::Hmr;a.q_target=QubitId(0);a.c_target=BitId(0);let mut b=a;b.q_target=QubitId(1);b.c_target=BitId(1);vec![a,b]}
#[test]fn event_labels_follow_the_full_permutation(){let v=fixture();assert!(verify(&v,&[1,0]));assert_eq!(event_map(&v,&[1,0]),vec![1,0]);}
#[test]#[should_panic]fn duplicate_event_is_rejected(){event_map(&fixture(),&[0,0]);}
#[test]#[should_panic]fn missing_event_is_rejected(){event_map(&fixture(),&[0]);}
}
'''
(r/'order_mrfree.rs').write_text(s,encoding='utf-8',newline='\n')
for src,name in [(e/'product-order-combined-20261019/legacy.rs','legacy.rs'),(e/'product-order-combined-20261019/io.rs','io.rs'),(e/'product-order-combined-20261019/preflight.py','preflight.py')]:
    (r/name).write_bytes(src.read_bytes())
print('Prepared measurement-channel scheduler with explicit event-label map')
