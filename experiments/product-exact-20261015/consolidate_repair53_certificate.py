"""Freeze the complete A29-relative universal cache theorem and separate mask premise."""
import hashlib,json,re
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'repair53-universal-20261016';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();target=d/'CACHE_EQUIVALENCE_CERTIFICATE.json';assert not target.exists()
assert (d/'launcher.exit').read_text().strip()=='0';receipt=json.loads((d/'RECEIPT.json').read_text());assert receipt['status']=='UNIVERSAL_REPAIRED53_CHAIN_PASS' and len(receipt['stages'])==53
assert sha(r/'REPAIR53_FREEZE.json')==receipt['source_freeze_sha256'] and sha(r/'repair53-native-20261016/NATIVE_RECEIPT.json')==receipt['native_receipt_sha256']
assert sha(r/'target-cache-certificate-v2/release/product_paired_diagnostic')==receipt['verifier_executable_sha256']
source=r/'cache-certificate-v2-tool';assert {str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file() and 'target' not in p.relative_to(source).parts}==receipt['source_files_sha256']
last=receipt['baseline_stream_sha256'];leases=uses=0
for number,row in enumerate(receipt['stages'],1):
    assert row['stage']==number and row['status']=='PASS' and row['returncode']==0 and row['input_sha256']==last
    for path,h in [('input_stream','input_sha256'),('output_stream','output_sha256'),('audit_log','audit_log_sha256')]:assert sha(r/row[path])==row[h]
    log=(r/row['audit_log']).read_text()
    if row['lease_log']=='=':assert 'UNIVERSAL_BYTE_IDENTITY_PASS' in log and row['input_sha256']==row['output_sha256']
    else:
        assert sha(r/row['lease_log'])==row['lease_log_sha256'] and 'UNIVERSAL_CACHE_CERTIFICATE_PASS' in log and 'independent_zero_and_product_passes=true' in log
        leases+=int(re.search(r'leases=(\d+)',log).group(1));uses+=int(re.search(r'uses=(\d+)',log).group(1))
    last=row['output_sha256']
assert last==receipt['candidate_stream_sha256'];freeze=json.loads((r/'REPAIR53_FREEZE.json').read_text())
certificate={k:receipt[k] for k in ['baseline_stream_sha256','candidate_stream_sha256','source_freeze_sha256','native_receipt_sha256','source_files_sha256','verifier_executable_sha256','trusted_base','protected_dependency_revision','protected_dependency_files_sha256']}
certificate.update(status='UNIVERSAL_A29_RELATIVE_CACHE_EQUIVALENCE_PASS',stage_count=53,leases_verified=leases,replaced_uses_verified=uses,no_sampled_inputs=True,receipt_sha256=sha(d/'RECEIPT.json'),conclusion='For every original corrected-A29 ABI input and original A29 MR assignment, candidate coordinates, original classical outputs and phase equal corrected A29 under the preserved original-MR projection, independently of every added private cache MR assignment; private flags and donor scratch are cleaned.',original4b_coordinate_function_transfer=False,global_A29_MR_independence_proved=False,native_source_binding='Separate normal native generation and source/protected receipt bind this candidate hash. A changed nonce additionally requires the exact audited pre-tail bytes and48 adjacent XX identity pairs, and its own final-source Fiat inputs.',score=None,nonce_search_performed=False)
target.write_text(json.dumps(certificate,indent=2)+'\n')
companion={'status':'CONDITIONAL_PER_INPUT_MASK_TRANSFER_THEOREM_NOT_A_MASK_PROOF','certificate_sha256':sha(target),'baseline_A29_stream_sha256':receipt['baseline_stream_sha256'],'candidate_stream_sha256':last,'candidate_prefix':freeze['prefix_manifest'],'theorem':'For fixed ABI input x and scored output bit b, if a separate sound A29-source-bound mask proves F_A29,b(x,r) constant for every original A29 MR assignment r, the cache candidate bit equals F_A29,b(x,0) for every candidate MR assignment under the audited projection. No global MR-independence theorem is needed.','separate_premises':['A29 model/mask bound to baseline stream1cd3457b, its exact prefix, ABI and output bit ordering. Original4b masks are not valid across this arithmetic change.','Evaluate the sound A29 zero-MR value function on the candidate final-source Fiat inputs.','Final nonce source retains the exact audited prefix and48 adjacent XX identity pairs.','Any survivor still needs exact full phase/dirty checks and the unchanged official benchmark.'],'score':None}
(d/'PER_INPUT_MASK_TRANSFER.json').write_text(json.dumps(companion,indent=2)+'\n')
(d/'PER_INPUT_MASK_TRANSFER.md').write_text('# Corrected A29 per-input mask transfer\n\nThe separately hashed universal cache certificate compares A29 source1cd3457b with this corrected53 cache candidate. For each fixed input and scored bit, a separately sound A29-source-bound MR-independence mask lets the A29 zero-MR value evaluator provide that bit for every candidate MR under the audited projection. This does not reuse the original4b mask, prove global A29 MR independence, or replace final phase/dirty/official checks. A new nonce requires identical audited pre-tail bytes,48 adjacent XX identity pairs and its own Fiat inputs.\n')
print(json.dumps({'certificate_sha256':sha(target),'mask_companion_sha256':sha(d/'PER_INPUT_MASK_TRANSFER.json'),'leases':leases,'uses':uses}),flush=True)
