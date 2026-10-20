"""Paired raw semantic/cost diagnostic; no final statistical gate."""
import hashlib,json,statistics,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;assert(r/'run.exit').read_text().strip()=='0'
f=json.loads((r/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(r/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
binary=r.parent/'simd-census-v2-20261016/bin/simd_census_v2'
reference=json.loads((r.parent/'breakthrough-profile-20261020/REPLAY-VERIFICATION.json').read_text());assert sha(binary)==reference['original_binary_sha256']
label='breakthrough-fold-square-ripple-raw-v1';batches=512;records={}
try:
    for name,cap,expected in[('parent',1234,'13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'),
         ('candidate',1233,'d89649df7d74b8e93b9dbe40172e6f4fcffc84dc4473dfaca49b9101c8780f7c')]:
        ops=r/f'cap{cap}/ops.bin';assert sha(ops)==expected
        with(r/(name+'-replay.out')).open('xb')as out,(r/(name+'-replay.err')).open('xb')as err:
            p=subprocess.Popen([str(binary),str(ops),label,'0',str(batches),'2',str(r/(name+'-census.jsonl')),'8'],stdout=out,stderr=err)
            (r/(name+'-replay.pid')).write_text(str(p.pid)+'\n');assert p.wait()==0
        rows=[json.loads(l)for l in(r/(name+'-census.jsonl')).read_text().splitlines()]
        assert len(rows)==batches and[x['batch']for x in rows]==list(range(batches))
        assert all(x['shots']==64 and x['skipped']==0 for x in rows);records[name]=rows
    summaries={name:{'mean_executed_raw_toffoli':sum(x['toffoli']for x in rows)/(64*batches),
        'value_shots':sum(x['value_shots']for x in rows),'phase_shots':sum(x['phase_shots']for x in rows),
        'dirty_shots':sum(x['dirty_shots']for x in rows),'failed_batches':sum(bool(x['failures'])for x in rows),
        'rows_sha256':sha(r/(name+'-census.jsonl'))}for name,rows in records.items()}
    def values(rows):return{(row['batch'],x['lane']):(x['k1'],x['k2'])for row in rows for x in row['failures']if x['value']}
    same=values(records['parent'])==values(records['candidate'])
    differences=[(a['toffoli']-b['toffoli'])/64 for a,b in zip(records['candidate'],records['parent'])]
    result={'status':'RAW_DIAGNOSTIC_COMPLETE_NO_FINAL_GATE_VERDICT','label':label,'batches':batches,'shots_per_source':64*batches,
        'same_value_failing_shot_identities':same,'summaries':summaries,
        'candidate_minus_parent_mean_raw_toffoli':statistics.mean(differences),'paired_batch_mean_standard_error':statistics.stdev(differences)/batches**0.5,
        'protected_scalar_verified_batches_per_source':8,'replay_binary_sha256':sha(binary),
        'scope':'Raw arithmetic diagnostics including failed inputs; configured1233 still actual1234. No complete optimized score, final gate or nonce search.'}
    (r/'PAIRED-DIAGNOSTIC.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    assert same and summaries['candidate']['dirty_shots']==0
except BaseException:
    (r/'replay.exit').write_text('1\n');raise
else:(r/'replay.exit').write_text('0\n')
