"""Compose universal95 with the independently verified appended84 stages (96..179)."""
import hashlib,json,re
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'cache-certificate179-20261017';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
target=d/'CACHE_EQUIVALENCE_CERTIFICATE.json';assert not target.exists()
assert (d/'launcher.exit').read_text().strip()=='0'
old=r/'cache-certificate95-20261017/CACHE_EQUIVALENCE_CERTIFICATE.json';assert sha(old)=='f3af2e4d3275f9b39fa34ad61d8a000f166935eb4f7236ac28a5cd2032dc27ad';prior=json.loads(old.read_text())
receipt=json.loads((d/'RECEIPT.json').read_text());assert receipt['status']=='UNIVERSAL179_CHAIN_PASS' and len(receipt['stages'])==84
assert receipt['prior_certificate_sha256']==sha(old)
assert sha(r/'cache-certificate95-20261017/RECEIPT.json')==receipt['prior_receipt_sha256']
assert sha(r/'PRODUCT179_FREEZE.json')==receipt['source_freeze_sha256']
last=prior['candidate_stream_sha256'];leases=prior['leases_verified'];uses=prior['replaced_uses_verified']
for number,row in enumerate(sorted(receipt['stages'],key=lambda x:x['stage']),96):
    assert row['stage']==number and row['status']=='PASS' and row['returncode']==0 and row['input_sha256']==last
    for key,h in [('input_stream','input_sha256'),('output_stream','output_sha256'),('audit_log','audit_log_sha256')]:assert sha(r/row[key])==row[h]
    log=(r/row['audit_log']).read_text()
    if row['lease_log']=='=':assert 'UNIVERSAL_BYTE_IDENTITY_PASS' in log and row['input_sha256']==row['output_sha256']
    else:
        assert sha(r/row['lease_log'])==row['lease_log_sha256'];assert 'UNIVERSAL_CACHE_CERTIFICATE_PASS' in log and 'independent_zero_and_product_passes=true' in log
        leases+=int(re.search(r'leases=(\d+)',log).group(1));uses+=int(re.search(r'uses=(\d+)',log).group(1))
    last=row['output_sha256']
assert last==receipt['candidate_stream_sha256']==json.loads((r/'PRODUCT179_FREEZE.json').read_text())['external_stream_sha256']
assert sha(r/'target-cache-certificate-v2/release/product_paired_diagnostic')==receipt['verifier_executable_sha256']
tool=r/'cache-certificate-v2-tool'
sources={str(p.relative_to(tool)):sha(p) for p in tool.rglob('*') if p.is_file() and 'target' not in p.relative_to(tool).parts}
assert sources==prior['source_files_sha256']
answer={'status':'UNIVERSAL_CACHE_EQUIVALENCE_AUDIT_PASS','stage_count':179,'leases_verified':leases,'replaced_uses_verified':uses,'no_sampled_inputs':True,'prior_certificate_sha256':sha(old),'appended_receipt_sha256':sha(d/'RECEIPT.json'),'baseline_stream_sha256':prior['baseline_stream_sha256'],'candidate_stream_sha256':last,'verifier_executable_sha256':receipt['verifier_executable_sha256'],'source_files_sha256':sources,'protected_dependency_revision':prior['protected_dependency_revision'],'protected_dependency_files_sha256':prior['protected_dependency_files_sha256'],'trusted_base':prior['trusted_base'],'conclusion':prior['conclusion'],'original_coordinate_measurement_independence_proved_by_this_audit':False,'conditional_transfer':prior['conditional_transfer'],'per_input_transfer':'For fixed ABI input x and original scored output bit b, if a separate sound source-bound mask proves F_b(x,MR) constant over every original MR, then this candidate bit equals F_b(x,0) for every candidate MR under the audited original-MR projection. No global MR-independence theorem required. Mask soundness is a separate premise.','native_source_binding':'This certificate binds the frozen external267 stream hash. The coordinator separately checks normal native generation byte identity, point_add-only source scope and its protected harness. Every final nonce source must retain the audited exact pre-tail bytes and48 adjacent XX identity pairs and use its own Fiat inputs.','nonce_scope':prior['nonce_scope'],'phase_screening':prior['phase_screening'],'score':None,'nonce_search_performed_by_this_experiment':False}
answer['native_source_binding']=prior['native_source_binding'].replace('external95','external179')
target.write_text(json.dumps(answer,indent=2)+'\n');print(json.dumps({k:answer[k] for k in ['status','stage_count','leases_verified','replaced_uses_verified','baseline_stream_sha256','candidate_stream_sha256']}),flush=True)
