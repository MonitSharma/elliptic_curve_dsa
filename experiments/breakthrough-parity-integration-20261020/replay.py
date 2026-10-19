"""Predeclared512-batch paired raw diagnostic, explicitly not a final gate."""
import hashlib,json,os,statistics,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;label='breakthrough-parity-integration-raw-v1';batches=512
while not(r/'run.exit').exists():time.sleep(15)
assert(r/'run.exit').read_text().strip()=='0'
f=json.loads((r/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(r/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
result=json.loads((r/'GENERATION-RESULT.json').read_text());assert result['uses']>0
binary=r.parent/'simd-census-v2-20261016/bin/simd_census_v2'
reference=json.loads((r.parent/'breakthrough-profile-20261020/REPLAY-VERIFICATION.json').read_text())
assert sha(binary)==reference['original_binary_sha256']
parent=r.parent/'breakthrough-domain-profile-20261020/observer/ops.bin'
assert sha(parent)=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
try:
    records={}
    for name,ops in[('parent',parent),('candidate',r/'observer/ops.bin')]:
        with(r/(name+'-replay.out')).open('xb')as out,(r/(name+'-replay.err')).open('xb')as err:
            child=subprocess.Popen([str(binary),str(ops),label,'0',str(batches),'2',str(r/(name+'-census.jsonl')),'8'],stdout=out,stderr=err)
            (r/(name+'-replay.pid')).write_text(str(child.pid)+'\n');rc=child.wait();assert rc==0,(name,rc)
        rows=[json.loads(l)for l in(r/(name+'-census.jsonl')).read_text().splitlines()]
        assert len(rows)==batches and[x['batch']for x in rows]==list(range(batches))
        assert all(x['shots']==64 and x['skipped']==0 for x in rows)
        records[name]=rows
    summaries={name:{'mean_executed_toffoli':sum(x['toffoli']for x in rows)/(64*batches),
        'value_failing_shots':sum(x['value_shots']for x in rows),'phase_failing_shots':sum(x['phase_shots']for x in rows),
        'dirty_shots':sum(x['dirty_shots']for x in rows),'failed_batches':sum(bool(x['failures'])for x in rows),
        'rows_sha256':sha(r/(name+'-census.jsonl'))}for name,rows in records.items()}
    changes=[(a['toffoli']-b['toffoli'])/64 for a,b in zip(records['candidate'],records['parent'])]
    summaries['comparison']={'candidate_minus_parent_mean_toffoli':statistics.mean(changes),
        'paired_batch_mean_standard_error':statistics.stdev(changes)/batches**0.5}
    assert all(sha(r/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
    report={'status':'PAIRED_RAW_DIAGNOSTIC_COMPLETE_NO_FINAL_GATE_VERDICT','label':label,'batches':batches,'shots_per_source':64*batches,
        'summaries':summaries,'parent_stream_sha256':sha(parent),'candidate_stream_sha256':sha(r/'observer/ops.bin'),
        'replay_binary_sha256':sha(binary),'protected_scalar_verified_batches_per_source':8,
        'scope':'Raw arithmetic only. These are diagnostic counts including failed inputs; no complete optimized QxT record or final statistical gate/nonce search.'}
    (r/'PAIRED-DIAGNOSTIC.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
except BaseException:
    (r/'replay.exit').write_text('1\n');raise
else:(r/'replay.exit').write_text('0\n')
