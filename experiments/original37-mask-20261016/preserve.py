"""Preserve one completed private proof trial, including its small binary mask."""
from pathlib import Path
import hashlib,json,tarfile
root=Path(__file__).resolve().parent
assert (root/'run.exit').read_text().strip()=='0'
assert (root/'input-before.sha256').read_bytes()==(root/'input-after.sha256').read_bytes()
assert (root/'input-before.sha256').read_text().startswith('2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e ')
report=json.loads((root/'global.json').read_text())
assert report['protected_full_state_containment_seeds']==4 and report['rng_draws']==906156
family=json.loads((root/'a29-fold-family-v1/hints.json').read_text())['hints']
six=json.loads((root/'a29-edited-folds-v1/original-candidates.json').read_text())
wanted={(r['old_start'],r['old_end_exclusive']) for r in family}
wanted.update(map(tuple,six['candidate_shadow_regions']));assert len(wanted)==37
accepted={(r['start'],r['end_exclusive']) for r in report['applied_shadow_contracts']}
tests=(root/'tests.log').read_text();assert '33 passed; 0 failed' in tests
old=root.parent/'prefilter-20261015/tool/src'
critical=['input_anf_dag_trace.rs','global_rng_anf_retained_masks.rs','reset_projection.rs','reset_projection_symbols.rs','shadow_value_contract_bound.rs','shadow_apply_region_bound.rs','mask_program_trace.rs']
kernel_hashes={}
for name in critical:
    data=(root/'tool/src'/name).read_bytes()
    assert data==(old/name).read_bytes(),name
    kernel_hashes[name]=hashlib.sha256(data).hexdigest()
summary={k:v for k,v in report.items() if not isinstance(v,(dict,list))}
summary.update(status='TERMINAL_PROOF_COVERAGE_NEGATIVE_NO_SCREENING',native_tests=33,
    requested_whole_folds=37,individually_accepted_whole_folds=len(wanted&accepted),
    missing_whole_folds=sorted(wanted-accepted),generic_kernels_identical_to_frozen_original=kernel_hashes,
    production_mask_or_runtime_changed=False,nonce_search=False,resource_record=False)
(root/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n')
allowed={'.py','.rs','.c','.h','.sh','.md','.json','.jsonl','.log','.err','.out','.sha256','.csv','.tsv','.exit','.pid','.txt','.in'}
paths=[]
for p in root.rglob('*'):
    if not p.is_file() or any(s in p.relative_to(root).parts for s in ['target','.git']):continue
    if p.name in ['manifest.json','verified-manifest.json','archive-receipt.json']:continue
    small_binary=p.suffix=='.bin' and p.parent==root/'evidence' and p.stat().st_size<2*1024**2
    if small_binary or p.suffix in allowed or p.name in ['Cargo.toml','Cargo.lock']:paths.append(p)
paths=sorted(set(paths));manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','w:gz') as archive:
    for p in paths+[root/'manifest.json']:archive.add(p,arcname=str(p.relative_to(root)))
receipt={'archive_sha256':hashlib.sha256((root/'evidence.tar.gz').read_bytes()).hexdigest(),'files':len(paths),
    'all_small_binary_masks_and_audit_vectors_preserved':True,'status':summary['status']}
(root/'archive-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'summary':summary,'archive':receipt},indent=2))
