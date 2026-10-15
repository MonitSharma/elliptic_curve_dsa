from pathlib import Path
import hashlib,json,datetime
r=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def record(path):
 p=r/path
 return dict(path=path,bytes=p.stat().st_size,sha256=sha(p))
e=r/'evidence'
assert (e/'global-anf-mask-trace.exit').read_text().strip()=='0'
assert (e/'mask-validate-v3.exit').read_text().strip()=='0'
for stem in ['global-anf-mask-trace','mask-validate-v3']:
 assert (e/(stem+'-before.sha256')).read_bytes()==(e/(stem+'-after.sha256')).read_bytes()
program=record('evidence/mr-mask-tip-v3.bin')
assert program['sha256']=='560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d'
meta=json.loads((e/'mr-mask-tip-v3.json').read_text());assert meta['compiled_nodes']==7914981
reports={name:json.loads((e/('mask-validate-v3-'+name+'.json')).read_text()) for name in ['audit','all-failing-tip','sensitivity-structured','sensitivity-arbitrary']}
assert all(x['protected_known_bit_containment_passed'] and x['independent_physical_mr_streams']==8 for x in reports.values())
assert sum(x['shots'] for x in reports.values())==2214
assert reports['audit']['certified_wrong_value_shots']==24
assert reports['all-failing-tip']['certified_wrong_value_shots']==421
sources=['input_anf_dag_trace.rs','mask_program_trace.rs','bin/global_rng_anf_mask_trace.rs','global_rng_anf_mask_trace_body.rs','global_rng_anf_retained_masks.rs','shadow_value_contract_bound.rs','shadow_value_contract_zeros.rs','shadow_apply_region_bound.rs','reset_projection.rs','reset_projection_symbols.rs','bin/mask_validate.rs','mask_validate_body.rs']
report=dict(status='FROZEN_SOURCE_BOUND_INPUT_CONDITIONED_MR_CERTIFICATE',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_commit=meta['source_commit'],stream_sha256=meta['original_stream_sha256'],program=program,artifact_metadata=record('evidence/mr-mask-tip-v3.json'),abi=record('MR-MASK-ABI.txt'),audit_vectors=[record('evidence/mr-mask-tip-v3.audit-input-u64le.bin'),record('evidence/mr-mask-tip-v3.audit-known-u64le.bin')],schema=dict(magic='MRMASK01',header_bytes=32,node_bytes=16,inputs=1024,outputs=512,meaning='known = NOT dependency-root'),theorem='A zero dependence upper bound guarantees that scored output bit independent of every physical MR and conservative cap symbol for this input. A wrong zeroMR coordinate on a certified-known scored bit proves failure for every physicalMR.',caps='FreshMR and opaque unknowns remain outer ANF variables; pure-input caps retain immutable exact definitions. Undeclared exported terminals abort. No opaque becomes a known input.',all_global_bits_rng_independent=False,auxiliary_initialization='All undeclared q/b zero; declared1024 inputs arbitrary',local_contracts='Exact operation digest bound; proved-zero prefix preconditions checked at application',exporter_native_tests=33,exporter_protected_full_state_seeds=4,validation_inputs=2214,physical_mr_streams=8,protected_stream_input_comparisons=17712,saved_census_value_failures=431,saved_census_certified_value_failures=421,reports=reports,independent_python=json.loads((e/'mask-reference-v3-audit.json').read_text()),source_files=[record('tool/src/'+s) for s in sources],proof_receipts=[record('evidence/'+s) for s in ['global-anf-mask-trace-tip32.json','global-anf-mask-trace.tests.log','global-anf-mask-trace-before.sha256','global-anf-mask-trace-after.sha256','mask-validate-v3-before.sha256','mask-validate-v3-after.sha256']],not_claimed=['all512bits globallyMRindependent','phaseorGarbagecorrectness','structuredfixturecounts asofficialfailurecensus','arbitrarycoordinatescorrectness','transfer to any changed stream without universal equivalence','live search or submission by this agent'],coordinator_integration_gate='requires independent runtime validator and exact source binding/transfer before live use')
(e/'mask-freeze-v3.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(receipt='evidence/mask-freeze-v3.json',sha256=sha(e/'mask-freeze-v3.json'),source_files=len(sources),program=program)))
