from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parent;old=root.parent/'prefilter-20261015'
assert not (root/'tool').exists(),'never overwrite a prior trial'
shutil.copytree(old/'tool/src',root/'tool/src')
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/name,root/'tool'/name)
e=root/'evidence';e.mkdir()
inputs=['evidence/global-anf-shadow-bound-tip32.json','a29-fold-family-v1/hints.json','a29-edited-folds-v1/original-candidates.json','packets/audit.tsv','opaque-tail-certified-v1-proof-spans.tsv']
summaries=[f'evidence/reset-projection-{s}.summary.json' for s in ['tip','symbols-tip','comparators','top1-complete','all-scopes-tip','carry']]
record={}
for relative in inputs+summaries:
    p=old/relative;data=p.read_bytes();out=root/relative;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
    record[relative]={'source_sha256':hashlib.sha256(data).hexdigest(),'source_copy_unchanged':data==p.read_bytes()}
    assert record[relative]['source_copy_unchanged']
prior=json.loads((root/inputs[0]).read_text())
hints={(r['start'],r['end_exclusive']) for r in prior['applied_shadow_contracts']}
family=json.loads((root/inputs[1]).read_text())['hints'];assert len(family)==31
added={(r['old_start'],r['old_end_exclusive']) for r in family}
six=json.loads((root/inputs[2]).read_text());assert six['full_operation_count']==11630716 and six['unmapped']==0
assert len(six['candidate_shadow_regions'])==6
added.update(map(tuple,six['candidate_shadow_regions']));assert len(added)==37
assert all(0<=a<b<=11630716 for a,b in added)
hints.update(added)
private={'status':'BOUNDARIES_ONLY_NO_ACCEPTANCE_OR_MASK_ROOTS_TRANSFERRED','rng_draws':906156,'applied_shadow_contracts':[{'start':a,'end_exclusive':b} for a,b in sorted(hints,key=lambda p:(p[0],-p[1]))]}
(e/'original37-prior.json').write_text(json.dumps(private,indent=2)+'\n')
wrapper=(old/'tool/src/bin/global_rng_anf_mask_trace.rs').read_text()
for before,after in [('../global_rng_anf_mask_trace_body.rs','../original37_mask_body.rs'),('../mask_program_trace.rs','../original37_mask_program.rs')]:
    assert wrapper.count(before)==1
    wrapper=wrapper.replace(before,after)
wrapper='#![recursion_limit="256"]\n'+wrapper
(root/'tool/src/bin/original37_mask.rs').write_text(wrapper)
body=(old/'tool/src/global_rng_anf_mask_trace_body.rs').read_text()
assert body.count('evidence/global-anf-shadow-bound-tip32.json')==1
body=body.replace('evidence/global-anf-shadow-bound-tip32.json','evidence/original37-prior.json')
assert body.count('evidence/mr-mask-tip-v3')>=4
body=body.replace('evidence/mr-mask-tip-v3','evidence/mr-mask-original37')
(root/'tool/src/original37_mask_body.rs').write_text(body)
shutil.copyfile(old/'tool/src/mask_program_trace.rs',root/'tool/src/original37_mask_program.rs')
(root/'INPUT-RECEIPT.json').write_text(json.dumps({'inputs':record,'additional_whole_fold_hints':37,'total_distinct_hints':len(hints),'old_mask_loaded':False,'generic_proof_engine_changed':False},indent=2)+'\n')
print('Prepared private original37 proof with',len(hints),'candidate intervals; all acceptance remains fresh')
