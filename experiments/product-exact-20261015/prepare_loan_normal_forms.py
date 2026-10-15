"""Complete-family source-only dirty target queries, one bounded fast engine."""
import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'loan-normal-forms-20261016';tool=r/'loan-normal-forms-tool';other=r.parent/'current-value-attribution-20261016'
assert not d.exists() and not tool.exists();d.mkdir();(tool/'src').mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
family=other/'n2-loan-family.json';v=json.loads(family.read_text());assert v['actual_stream_sha256']=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
for name in ['Cargo.toml','Cargo.lock']:shutil.copy2(other/'tool'/name,tool/name)
support=other/'donor-support-original.rs';(tool/'src/support.rs').write_text(support.read_text()+'\n'+(r/'loan_queries.rs.in').read_text())
loader=(other/'tool/src/bin/affine_loan_donors.rs').read_text().split('fn main(){')[0].replace('#[path="donor_support.rs"]mod support;','mod support;')
loader+='''fn main(){
 let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),3);let ops=load(&args[1]);let family:serde_json::Value=serde_json::from_slice(&std::fs::read(&args[2]).unwrap()).unwrap();let mut queries=std::collections::BTreeMap::new();
 for f in family["families"].as_array().unwrap(){let start=f["out_span"][0].as_u64().unwrap()as usize;let after=f["out_span"][1].as_u64().unwrap()as usize;let end=f["returned_span"][1].as_u64().unwrap()as usize;let mut touched=BTreeSet::new();for o in &ops[start..end]{for q in[o.q_control1,o.q_control2,o.q_target]{if q.0!=u64::MAX{touched.insert(q.0 as usize);}}}let eligible:Vec<_>=(0..1234).filter(|q|!touched.contains(q)).collect();assert_eq!(eligible.len(),650);let targets:Vec<_>=f["source_rails_bit1through5"].as_array().unwrap().iter().flat_map(|rail|rail.as_array().unwrap()[..4].iter().map(|x|x.as_u64().unwrap()as usize)).collect();assert_eq!(targets.len(),8);queries.insert(after,(f["phase"].as_str().unwrap().to_string(),end,eligible,targets));}
 let mut state=support::Support::new(&ops);let started=std::time::Instant::now();for(at,op)in ops.iter().enumerate(){if let Some((phase,end,eligible,targets))=queries.remove(&at){let result=state.dirty_rhs_queries(&eligible,&targets);println!("{}",serde_json::json!({"phase":phase,"at_after_out":at,"full_window_end":end,"seconds":started.elapsed().as_secs_f64(),"result":result,"sampled_inputs":0,"rewrites_applied":false}));if queries.is_empty(){break;}}let _=state.step(op);}assert!(queries.is_empty());
}
'''
(tool/'src/main.rs').write_text(loader);shutil.copy2(family,d/'n2-loan-family.json')
plan=dict(status='PREDECLARED_COMPLETE_FAMILY_SOURCE_ONLY_DIRTY_RHS_QUERY',stream='tip/ops.bin',stream_sha256=v['actual_stream_sha256'],family_sha256=sha(family),source_engine=str(support),source_engine_sha256=sha(support),atom_cap=512,product_cap=200000,calls=2,rails=4,dirty_targets=16,workers=1,address_limit_GiB=24,time_limit_seconds=1800,ordered_queries=['dirty target direct q/complement and indexed XORtwo stable q','Gaussian stable-q-only span then stable-q plus current-classical span','existing inverse product nodes touching target atom IDs, factor forms mapped to stable q, <=4096variants/site, affine plus indexed products'],no_cartesian_product_pair_search=True,sampled_inputs=0,emits_stream=False,full_repair_certificate=False,scope='A found affine/product expression needs independent prefix/function/return-zero/phase and classical-snapshot proof before a repair. A negative only concerns this conservative bounded engine. Complete source family, no14-case-selected target.',source_files_sha256={str(p.relative_to(tool)):sha(p) for p in tool.rglob('*') if p.is_file()})
(d/'DECLARATION.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps(plan))
