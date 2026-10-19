"""Accept a reviewed port only after final source, runtime and cost gates."""
import datetime,hashlib,json,math,statistics
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;n=ws/'product-classical-nine-20261019';qual=ws/'product-classical-nine-filter-20261019'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
assert not (r/'ACCEPTANCE.json').exists()
assert (r/'build.exit').read_text().strip()=='0' and '1 passed; 0 failed' in (r/'order-tests.log').read_text()
audit=read(r/'TOOL_DIFF_AUDIT.json');assert audit['status']=='ONLY_QUALIFIED_CLASSICAL_NINE_BINDINGS_DIFFER'
assert all(sha(r/'tool'/p)==v['sha256'] for p,v in audit['files'].items())
assert all(sha(Path(p))==h for p,h in audit['additional_runtime_artifacts'].items())
g=read(n/'qualification/RESULT.json');assert g['status']=='FAILURE_GATE_PASS' and all(g['rules'].values())
q=read(qual/'RESULT.json');assert q['status']=='DISABLED_CLASSICAL_NINE_PIPELINE_QUALIFICATION_PASS'
assert q['all4096_rows_identical'] and q['protected_full9024_q_b_phase_physicalMR'] and not q['authoritative_rejection']
assert (qual/'qualification.exit').read_text().strip()=='0'
old=read(ws/'parent4-operational-sat-20261019/ACCEPTANCE.json')
required=dict(old['runtime_artifacts']);required.update(audit['additional_runtime_artifacts'])
required[str(r/'TOOL_DIFF_AUDIT.json')]=sha(r/'TOOL_DIFF_AUDIT.json')
assert all(sha(Path(p))==h for p,h in required.items())
lam=g['failed_batches_per_packet']['candidate'];expected=math.exp(-141*math.log1p(-lam/141))
seconds=statistics.median(q['times_seconds']['threaded']);per_thread=4096/seconds/2
hours=expected/(per_thread*56)/3600
assert hours<=24,'New source fails affordable-search cost gate; do not launch'
result={'status':'SOURCE_BOUND_MASK_TRANSFER_AND_RUNTIME_ACCEPTED_FOR_ASCENDING_SEARCH','accepted_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'candidate':'Frozen parent4 plus nine exact classical-control reductions','candidate_stream_sha256':g['stream_sha256']['candidate'],
 'mask_sha256':old['mask_sha256'],'operational_binary_sha256':sha(r/'tool/target/release/value_prefilter'),'lowest_pass_from':1,'submission_mode':'queue',
 'failure_gate_pass':True,'failure_gate':g,'cost_gate_pass':True,'expected_nonces':expected,'pilot_rate_nonces_per_thread_second':per_thread,
 'expected_hours_at_56_threads_ideal_linear':hours,'wall_limit_hours':48,
 'cost_estimate_scope':'New-source 2-thread median over three4096-row trials. 56-thread linear scaling is an estimate, not a measured production rate.',
 'qualified_prefix_rows_sha256':sha(qual/'baseline-0.jsonl'),'runtime_artifacts':required,
 'derivation':'Reviewed parent4 operational source; only candidate hash/opcount and exact new-source proof/qualification bindings differ.',
 'remaining_gates':['Operational rows equal new qualified prefix1..4096','Current public record and actual CPU/memory/process preflight','Preserve old partial search before replacing it','Complete audit of every lower nonce','Native source/tail reproduction and unchanged benchmark','Queue full evidence; no upload'],
 'score':None,'no_existing_parent4_prefix_rows_reused':True}
(r/'ACCEPTANCE.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','expected_nonces','expected_hours_at_56_threads_ideal_linear']},indent=2))
