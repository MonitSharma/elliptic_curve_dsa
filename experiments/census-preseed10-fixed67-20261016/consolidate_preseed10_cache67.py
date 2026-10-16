"""Freeze only fresh PRESEED10-relative proofs; copy kernel provenance, never old equivalence."""
from pathlib import Path
import hashlib,json,re
r=Path(__file__).resolve().parent;d=r/'preseed10-cache67-20261016';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();target=d/'CACHE_EQUIVALENCE_CERTIFICATE.json';assert not target.exists()
freeze=json.loads((r/'PRESEED10_FIXED67_FREEZE.json').read_text());bindings=json.loads((d/'CACHE_BINDINGS.json').read_text());rows=json.loads((d/'CACHE_STAGE_RECEIPTS.json').read_text());assert len(rows)==67
trusted=r/'cache-certificate-v2-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json';assert sha(trusted)==bindings['trusted_kernel_provenance_certificate_sha256'];kernel=json.loads(trusted.read_text())
assert sha(r/'target-cache-certificate-v2/release/product_paired_diagnostic')==bindings['verifier_sha256'];source=r/'cache-certificate-v2-tool';assert {p.relative_to(source).as_posix():sha(p)for p in source.rglob('*')if p.is_file()and 'target'not in p.relative_to(source).parts}==bindings['verifier_source_files_sha256']
last=freeze['preseed10_parent_sha256'];leases=uses=0
for number,row in enumerate(rows,1):
 assert row['stage']==number and row['status']=='UNIVERSAL_PASS'and row['input_sha256']==last
 for path,digest in [('input_stream','input_sha256'),('output_stream','output_sha256'),('audit_log','audit_log_sha256')]:assert sha(r/row[path])==row[digest]
 log=(r/row['audit_log']).read_text()
 if row['lease_log']=='=':assert 'UNIVERSAL_BYTE_IDENTITY_PASS'in log and row['input_sha256']==row['output_sha256']
 else:
  assert sha(r/row['lease_log'])==row['lease_log_sha256'] and 'UNIVERSAL_CACHE_CERTIFICATE_PASS'in log and 'independent_zero_and_product_passes=true'in log and 'no_simulated_inputs=true'in log
  leases+=int(re.search(r'leases=(\d+)',log).group(1));uses+=int(re.search(r'uses=(\d+)',log).group(1))
 last=row['output_sha256']
assert last==freeze['external_stream_sha256']
certificate={k:kernel[k]for k in ['trusted_base','protected_dependency_revision','protected_dependency_files_sha256']}
certificate.update(status='UNIVERSAL_PRESEED10_RELATIVE_CACHE_EQUIVALENCE_PASS',stage_count=67,leases_verified=leases,replaced_uses_verified=uses,no_sampled_inputs=True,baseline_stream_sha256=freeze['preseed10_parent_sha256'],candidate_stream_sha256=last,source_files_sha256=bindings['verifier_source_files_sha256'],verifier_executable_sha256=bindings['verifier_sha256'],source_freeze_sha256=sha(r/'PRESEED10_FIXED67_FREEZE.json'),stage_receipts_sha256=sha(d/'CACHE_STAGE_RECEIPTS.json'),preseed10_native_parent_receipt_sha256=sha(d/'BASE_NATIVE_RECEIPT.json'),conclusion='For every PRESEED10 baseline ABI input and original MR assignment, final cache coordinates, original classical outputs and phase equal PRESEED10 under the preserved original-MR projection, independently of every added private cache MR assignment; private flags and donor scratch are cleaned.',original4b_coordinate_function_transfer=False,global_PRESEED10_MR_independence_proved=False,native_final_source_binding='Separate normal native byte receipt must bind this final hash. A new nonce requires the exact audited pre-tail bytes,48 adjacent XX identity pairs and its own final-source Fiat inputs.',score=None,nonce_search_performed=False)
target.write_text(json.dumps(certificate,indent=2)+'\n')
companion={'status':'CONDITIONAL_PER_INPUT_MASK_TRANSFER_NOT_A_BASE_MASK_PROOF','certificate_sha256':sha(target),'baseline_PRESEED10_stream_sha256':freeze['preseed10_parent_sha256'],'candidate_stream_sha256':last,'theorem':'For fixed ABI input x and scored bit b, if a separate sound PRESEED10-source-bound mask proves F_PRESEED10,b(x,r) constant for every original PRESEED10 MR assignment r, the cache candidate bit equals F_PRESEED10,b(x,0) for every candidate MR assignment under the audited projection.','separate_premises':['Fresh PRESEED10 value model/mask bound to the new PRESEED10 base source/prefix, ABI and output ordering. No original4b or A29 mask reuse.','Evaluate the sound PRESEED10 zero-MR value function on candidate final-source Fiat inputs.','Final source retains exact audited pre-tail and48 adjacent XX identity pairs.','Exact full phase/dirty checks and unchanged official benchmark remain required.'],'runtime_or_search_authority':False,'score':None}
(d/'PER_INPUT_MASK_TRANSFER.json').write_text(json.dumps(companion,indent=2)+'\n');print(json.dumps({'certificate_sha256':sha(target),'mask_companion_sha256':sha(d/'PER_INPUT_MASK_TRANSFER.json'),'leases':leases,'uses':uses}),flush=True)
