from pathlib import Path
r=Path(__file__).resolve().parent;e=r.parent
s=(e/'product-guard-schedule-20261019/guard_schedule.rs').read_text()
old='if a.mr{if let Some(p)=mr{deps.push(p);}mr=Some(i);}'
assert s.count(old)==1
s=s.replace(old,'')
old='if a.mr{if mr.is_some_and(|x|x>=j){return false;}mr=Some(j);}'
assert s.count(old)==1
s=s.replace(old,'')
# Remove now-unused independent MR-chain variables; real c-target writes remain.
s=s.replace('let mut mr=None;','')
s=s.replace('let(mut low,mut mr)=(0,None);','let mut low=0;')
s=s.replace('mr=None;continue;','continue;')
needle='let raw:Vec<_>=p.iter().flat_map(|&i|(i as u64).to_le_bytes()).collect();'
assert s.count(needle)==1
s=s.replace(needle,'''let mut ordinal=vec![u32::MAX;v.len()];let mut event_count=0u32;for(i,o)in v.iter().enumerate(){if matches!(o.kind,K::R|K::Hmr){ordinal[i]=event_count;event_count+=1;}}
 let event_map:Vec<_>=p.iter().filter_map(|&i|match nodes[i].item{Item::Gate(o)if matches!(o.kind,K::R|K::Hmr)=>Some(ordinal[nodes[i].origin]),_=>None}).collect();assert_eq!(event_map.len(),event_count as usize);let mut seen=vec![false;event_count as usize];for &x in &event_map{assert!(!seen[x as usize]);seen[x as usize]=true;}assert!(seen.iter().all(|x|*x));let mut map_raw=b"RNGPERM1".to_vec();map_raw.extend((event_count as u64).to_le_bytes());map_raw.extend(full_hash.as_bytes());for &x in &event_map{map_raw.extend(x.to_le_bytes());}std::fs::write(format!("{}.rng-map.bin",a[2]),&map_raw).unwrap();
 '''+needle)
s=s.replace('"all_original_R_and_Hmr_order_preserved":true','"all_original_R_and_Hmr_order_preserved":false,"rng_events":event_count,"changed_event_positions":event_map.iter().enumerate().filter(|(i,x)|*i!=**x as usize).count(),"rng_map_sha3_256":format!("{:x}",Sha3_256::digest(&map_raw))')
s=s.replace('MATERIALIZED_GUARD_AND_NODE_COMMUTATION_AUDIT_PASS_NOT_A_SCORE','MATERIALIZED_GUARD_MRFREE_NODE_AND_EVENT_BIJECTION_AUDIT_PASS_NOT_A_SCORE')
s=s.replace('fn all_measurements_and_resets_share_one_order_chain()','fn independent_measurements_and_resets_may_exchange_with_an_outcome_map()')
s=s.replace('assert!(!verify(&[a,b],&[1,0],2,1));','assert!(verify(&[a,b],&[1,0],2,1));')
s=s.replace('assert_eq!(old,run(&ordered,qi,ci,seed));','let _=&ordered; /* Full reordered comparison uses the certified event map. */')
(r/'guard_mrfree.rs').write_text(s,encoding='utf-8',newline='\n')

g=(e/'product-support-tight-20261019/tight_color.rs').read_text()
g=g.replace('fn color(v:&[Op])->(Vec<Op>,serde_json::Value){','fn color(v:&[Op])->(Vec<Op>,serde_json::Value,Vec<(u64,u64)>){')
g=g.replace('let mut examples=vec![];','let mut examples=vec![];let mut clean_events=vec![];')
g=g.replace('zero_releases+=1;','zero_releases+=1;clean_events.push((i as u64,role));')
assert g.count('(out,result)\n}')==1
g=g.replace('(out,result)\n}','(out,result,clean_events)\n}')
needle='let(out,mut result)=color(&v);'
assert g.count(needle)==1
g=g.replace(needle,'let(out,mut result,events)=color(&v);let mut raw=b"GRCLEAN1".to_vec();raw.extend((v.len()as u64).to_le_bytes());raw.extend(hash(&v).as_bytes());raw.extend((events.len()as u64).to_le_bytes());for(i,q)in events{raw.extend(i.to_le_bytes());raw.extend(q.to_le_bytes());}std::fs::write(format!("{}.clean-events.bin",a[2]),&raw).unwrap();result["clean_event_file_sha3_256"]=serde_json::json!(format!("{:x}",Sha3_256::digest(&raw)));')
g=g.replace('let(w,r)=color(','let(w,r,_)=color(').replace('let(_,r)=color(','let(_,r,_)=color(').replace('let(w,_)=color(','let(w,_,_)=color(')
(r/'tight_annotated.rs').write_text(g,encoding='utf-8',newline='\n')

t=(e/'product-guard-schedule-20261019/guard_trace.rs').read_text()
t=t.replace('phase:u64)->(Vec<u64>','phase:u64,map:Option<&[u32]>)->(Vec<u64>')
needle='let mut r=rng("guard-schedule-control-physical-RNG-20261019",batch);'
assert t.count(needle)==1
t=t.replace(needle,'''let count=v.iter().filter(|o|matches!(o.kind,K::R|K::Hmr)).count();let mut physical=rng("guard-schedule-control-physical-RNG-20261019",batch);let mut data=vec![0;count*8+64];physical.read(&mut data);let data=if let Some(map)=map{permute(&data,map)}else{data};let mut r=Bytes{data,at:0};''')
t=t.replace('(state.0,state.1,state.2,state.3,tail)','assert_eq!(r.at,r.data.len());(state.0,state.1,state.2,state.3,tail)')
t=t.replace('assert_eq!(a.len(),6);','assert_eq!(a.len(),7);')
needle='let old_nb=dims(&original).1;'
assert t.count(needle)==1
t=t.replace(needle,needle+'''let raw=std::fs::read(&a[5]).unwrap();assert_eq!(&raw[..8],b"RNGPERM1");let count=u64::from_le_bytes(raw[8..16].try_into().unwrap())as usize;assert_eq!(&raw[16..80],hash(&original).as_bytes());assert_eq!(raw.len(),80+4*count);let map:Vec<_>=raw[80..].chunks_exact(4).map(|x|u32::from_le_bytes(x.try_into().unwrap())).collect();validate(&map);let old_events:Vec<_>=original.iter().filter(|o|matches!(o.kind,K::R|K::Hmr)).collect();let new_events:Vec<_>=ordered.iter().filter(|o|matches!(o.kind,K::R|K::Hmr)).collect();assert_eq!(old_events.len(),count);assert_eq!(new_events.len(),count);for(j,&i)in map.iter().enumerate(){let x=old_events[i as usize];let y=new_events[j];assert_eq!((x.kind,x.q_target,x.c_target),(y.kind,y.q_target,y.c_target));}''')
t=t.replace('run(&original,batch,&input,phase)','run(&original,batch,&input,phase,None)').replace('run(&converted,batch,&input,phase)','run(&converted,batch,&input,phase,None)').replace('run(&ordered,batch,&input,phase)','run(&ordered,batch,&input,phase,Some(&map))').replace('run(&colored,batch,&input,phase)','run(&colored,batch,&input,phase,Some(&map))')
t=t.replace('"PROTECTED_SIMULATOR_MATERIALIZED_GUARD_PHYSICAL_TRANSCRIPT_CONTROL_PASS"','"PROTECTED_SIMULATOR_MATERIALIZED_GUARD_MAPPED_EVENT_TRANSCRIPT_CONTROL_PASS"')
t=t.replace('"scope":"512 uniformly sampled raw assignments and arbitrary initial phase; tool integration, not a curve failure-rate gate or score"','"scope":"512 raw assignments; converted circuit uses ordinary RNG, reordered circuit uses event bijection. Not an ordinary physical-RNG gate or resource score","rng_map_sha3_256":format!("{:x}",Sha3_256::digest(&raw))')
t=t.replace('std::fs::write(&a[5]','std::fs::write(&a[6]')
t=t.replace('all quantum/classical (including fresh bits), phase, cost and physical RNG after scheduling','all quantum/classical (including fresh bits), phase, cost and mapped-event continuation after scheduling')
t=t.replace('"all_values_including_fresh_classical_bits_equal_after_reordering":true','"all_values_including_fresh_classical_bits_equal_under_event_bijection":true')
t=t.replace('all eight full materialized-guard physical-RNG transcript controls pass','all eight full materialized-guard mapped-event transcript controls pass')
prefix=s[s.index('fn hash('):s.index('\nfn metadata(')]
t=t.replace('use sha3::{Shake256,','use sha3::{Sha3_256,Digest,Shake256,')
# Digest::update and XOF Update would otherwise conflict in the hash helper.
prefix=prefix.replace('h.update(x.to_le_bytes())','Digest::update(&mut h,x.to_le_bytes())')
t+='''\nstruct Bytes{data:Vec<u8>,at:usize}impl XofReader for Bytes{fn read(&mut self,out:&mut[u8]){let end=self.at.checked_add(out.len()).unwrap();assert!(end<=self.data.len());out.copy_from_slice(&self.data[self.at..end]);self.at=end;}}
fn validate(map:&[u32]){let mut seen=vec![false;map.len()];for &x in map{assert!((x as usize)<map.len());assert!(!seen[x as usize]);seen[x as usize]=true;}assert!(seen.iter().all(|x|*x));}
fn permute(data:&[u8],map:&[u32])->Vec<u8>{validate(map);assert_eq!(data.len(),8*map.len()+64);let mut out=vec![];for &i in map{out.extend_from_slice(&data[8*i as usize..8*i as usize+8]);}out.extend_from_slice(&data[8*map.len()..]);out}
#[cfg(test)]mod tests{use super::*;
 #[test]fn event_words_and_final_continuation_are_preserved(){let data:Vec<_>=(0..80).collect();let x=permute(&data,&[1,0]);assert_eq!(&x[..8],&data[8..16]);assert_eq!(&x[8..16],&data[..8]);assert_eq!(&x[16..],&data[16..]);}
 #[test]#[should_panic]fn duplicate_event_is_rejected(){validate(&[0,0]);}
 #[test]#[should_panic]fn out_of_range_event_is_rejected(){validate(&[0,2]);}
 #[test]fn empty_map_retains_continuation(){assert_eq!(permute(&[1;64],&[]),vec![1;64]);}
}\n'''+prefix
(r/'guard_mapped_trace.rs').write_text(t,encoding='utf-8',newline='\n')
