"""Accept only a frozen, gate-passing, qualified source and reviewed search port."""
import datetime,hashlib,json,math,statistics
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;proof=ws/'product-parent-sat-20261019';parent=ws/'product-pareto-20261019';qual=proof/'parent4-filter'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
assert not (r/'ACCEPTANCE.json').exists()
assert (r/'build.exit').read_text().strip()=='0'
assert '1 passed; 0 failed' in (r/'order-tests.log').read_text()
assert read(r/'TOOL_DIFF_AUDIT.json')['status']=='ONLY_PARENT4_QUALIFIED_BINDINGS_DIFFER'
assert (qual/'filter.exit').read_text().strip()=='0' and (proof/'extension.exit').read_text().strip()=='0'
q=read(qual/'RESULT.json');assert q['status']=='DISABLED_PARENT4_PIPELINE_QUALIFICATION_PASS' and q['all4096_rows_identical']
assert q['protected_full9024_q_b_phase_physicalMR'] and q['protected_zeroMR_shadow128_and_partial'] and not q['authoritative_rejection']
assert (qual/'binary-before.sha256').read_text()==(qual/'binary-after.sha256').read_text()
assert read(proof/'PUBLIC-PARENT-TRANSFER.json')['status']=='PUBLIC_PARENT_EXTENSION_UNIVERSAL_AUDIT_PASS'
gate=read(parent/'parent4-qualification/RESULT.json');assert gate['status']=='FAILURE_GATE_PASS' and all(gate['rules'].values())
candidate=parent/'candidate-parent4';stream=candidate/'ops.bin';h=sha(stream)
assert h==gate['stream_sha256']['candidate']=='9f50f06098026882a57f5f6c436abaaf68be79be2fc7c6e33b8e884065195a3a'
for name in ('point-add-source.json','protected-files.json'):
    assert all(sha(candidate/p)==digest for p,digest in read(parent/'parent4-qualification'/name).items())
assert read(parent/'NATIVE-PILOT.json')['status']=='NATIVE_PILOT_BYTE_IDENTITY_PASS'
old=read(ws/'plain67-operational-20261016/ACCEPTANCE.json')
required=dict(old['runtime_artifacts'])
for p in [stream,proof/'PUBLIC-PARENT-TRANSFER.json',proof/'VERIFIED-EXTENSION-PROOFS.json',proof/'target/release/verify_extension',
          parent/'parent4-qualification/RESULT.json',parent/'parent4-qualification/point-add-source.json',parent/'parent4-qualification/protected-files.json',
          qual/'RESULT.json',qual/'tool/target/release/value_prefilter',qual/'PREPARATION.json',r/'TOOL_DIFF_AUDIT.json']:
    required[str(p)]=sha(p)
assert all(sha(Path(p))==digest for p,digest in required.items())
lam=gate['failed_batches_per_packet']['candidate'];expected=math.exp(-141*math.log1p(-lam/141))
seconds=statistics.median(q['times_seconds']['threaded']);per_thread=4096/seconds/2
hours=expected/(per_thread*56)/3600
assert hours<=24,'Filter cost exceeds the one-day expected-cost criterion; do not launch this search'
result={'status':'SOURCE_BOUND_MASK_TRANSFER_AND_RUNTIME_ACCEPTED_FOR_ASCENDING_SEARCH',
    'accepted_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate':'Frozen parent4 exact product-retention candidate',
    'candidate_stream_sha256':h,'mask_sha256':'560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d',
    'operational_binary_sha256':sha(r/'tool/target/release/value_prefilter'),'lowest_pass_from':1,'submission_mode':'queue',
    'failure_gate_pass':True,'failure_gate':gate,'cost_gate_pass':True,'expected_nonces':expected,
    'pilot_rate_nonces_per_thread_second':per_thread,'expected_hours_at_56_threads_ideal_linear':hours,'wall_limit_hours':48,
    'cost_estimate_scope':'New-candidate 2-thread median over three 4096-nonce trials; 56-thread linear scaling is an estimate, not a measured production rate.',
    'qualified_prefix_rows_sha256':sha(qual/'baseline-0.jsonl'),'runtime_artifacts':required,
    'derivation':'Reviewed PLAIN67 operational source, changed only in the qualified candidate hash/op count and transfer-artifact bindings; complete source comparison in TOOL_DIFF_AUDIT.json.',
    'remaining_gates':['Operational rows equal qualified prefix 1..4096','Complete audit of every lower nonce before choosing first pass','Native pre-tail identity and unchanged official benchmark','Refresh public record and obey existing submission authorization'],
    'score':None,'existing_submission_authorization':'Parent4 only; GPT-6 Astra attribution; final eligibility remains mandatory'}
(r/'ACCEPTANCE.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'expected_nonces':expected,'estimated_hours_56_threads':hours,'acceptance_sha256':sha(r/'ACCEPTANCE.json')}),flush=True)
