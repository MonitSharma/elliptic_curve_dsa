import hashlib,json,shutil,sys
from pathlib import Path
R=Path(__file__).resolve().parent;P=R.parent/'prefilter-20261015'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
binding=json.loads((R/'BASE-BINDING.json').read_text());base=Path(binding['stream_path'])
assert sha(base)==binding['stream_sha256'] and binding['operation_count']==11630716
plan=json.loads((R/'SOURCE-PLAN.json').read_text())
T=R/'tool';assert not T.exists();(T/'src/bin').mkdir(parents=True)
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(P/'tool'/name,T/name)
for name,h in plan['kernel_source_pins_local'].items():
 src=P/'tool/src'/name;assert sha(src)==h,(name,sha(src));shutil.copyfile(src,T/'src'/name)
driver=P/'tool/src/a29_rng_mask_v2_body.rs';assert sha(driver)==plan['precursor_driver']['sha256']
text=driver.read_text()
for old,new in [('11636536','11630716'),('a29-mask-v2/candidates-v3.json','candidates.json'),('a29-mask-v2/mr-mask-a29','mr-mask-all70'),('1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522',binding['stream_sha256'])]:
 assert old in text; text=text.replace(old,new)
marker='let(nq,nb,_,regs)=analyze_ops(ops.iter());'
assert text.count(marker)==1
text=text.replace(marker,marker+'assert_eq!((nq,nb),(1234,45701));assert_eq!(regs.len(),4);assert!(regs.iter().all(|r|r.len()==256));')
marker='assert!(stack.is_empty());let seconds='
assert text.count(marker)==1
text=text.replace(marker,'assert_eq!(mr,906156);assert!(stack.is_empty());let seconds=')
(T/'src/all70_body.rs').write_text(text)
wrapper=(P/'tool/src/bin/a29_rng_mask_v2.rs').read_text()
assert wrapper.count('include!("../input_anf_dag_trace.rs");')==1
prefix=wrapper.split('include!("../input_anf_dag_trace.rs");')[0]
tail='''include!("../input_anf_dag_trace.rs");
include!("../global_rng_anf_retained_masks.rs");
mod coeff_projection{use super::*;include!("../reset_projection.rs");pub(super)fn prove(ops:&[Op])->bool{reset_projection_certificate(ops,200000,1000).proved}}
mod symbol_projection{use super::*;include!("../reset_projection_symbols.rs");pub(super)fn prove(ops:&[Op])->bool{reset_projection_certificate(ops,200000,1000).proved}}
include!("../shadow_value_contract_bound.rs");
include!("../shadow_apply_region_bound.rs");
include!("../mask_program_trace.rs");
include!("../all70_body.rs");
'''
(T/'src/bin/all70_rng_mask.rs').write_text(prefix+tail)
resetpaths=['reset-projection-tip.summary.json','reset-projection-symbols-tip.summary.json','reset-projection-comparators.summary.json','reset-projection-top1-complete.summary.json','reset-projection-all-scopes-tip.summary.json','reset-projection-carry.summary.json']
resets=[];hints={}
for name in resetpaths:
 p=P/'evidence'/name;s=json.loads(p.read_text());assert s['full_operation_count']==11630716
 resets.extend(s['selected_disjoint_certified_regions']);hints[str(p)]=sha(p)
prior=P/'evidence/global-anf-shadow-bound-tip32.json';s=json.loads(prior.read_text());assert s['rng_draws']==906156
shadow=[[r['start'],r['end_exclusive']]for r in s['applied_shadow_contracts']];hints[str(prior)]=sha(prior)
tailpath=P/'opaque-tail-certified-v1-proof-spans.tsv'
shadow.extend([list(map(int,line.split()[:2]))for line in tailpath.read_text().splitlines()if line.strip()]);hints[str(tailpath)]=sha(tailpath)
(R/'reset-hints.json').write_text(json.dumps({'full_operation_count':11630716,'selected_disjoint_certified_regions':sorted({tuple(x)for x in resets}),'status':'ENDPOINT_HINTS_ONLY_REQUIRE_FRESH_PROOF'})+'\n')
(R/'candidates.json').write_text(json.dumps({'full_operation_count':11630716,'candidate_reset_regions':[],'candidate_shadow_regions':sorted({tuple(x)for x in shadow}),'status':'ENDPOINT_HINTS_ONLY_REQUIRE_FRESH_PROOF'})+'\n')
manifest={'source_hash':binding['stream_sha256'],'hint_provenance':hints,'fresh_reset_hint_count':len({tuple(x)for x in resets}),'fresh_shadow_hint_count':len({tuple(x)for x in shadow}),
 'trusted_kernels_unchanged':True,'files':{str(p.relative_to(R)):sha(p)for p in T.rglob('*')if p.is_file()},'authority':False}
(R/'PREPARED-SOURCE.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest),flush=True)
