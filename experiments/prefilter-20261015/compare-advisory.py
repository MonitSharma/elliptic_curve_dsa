import json
from pathlib import Path
r=Path(__file__).parent/'evidence'
def read(name):return {int(x['nonce']):x for x in map(json.loads,(r/name).read_text().splitlines())}
a=read('advisory-128.jsonl');b=read('simd-ascending-128.jsonl');c=read('fast-screen-c-1-128.jsonl');old=read('reference-screen-1-128.jsonl')
assert set(a)==set(b)==set(c)==set(old)==set(range(1,129))
assert all(a[k]['pass']==b[k]['pass']==c[k]['pass']==old[k]['pass'] for k in a)
assert all(x['rejection_policy']=='exact_full_state_only' and x['exact_witness_batch'] is not None for x in a.values())
def total(v):return sum(v[k]['group_secs'] for k in sorted(v) if (k-1)%8==0)
rpt=dict(source='4b2ec52f',stream_sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e',nonces=128,truth_equal=True,all_rejected=True,workers=2,advisory_exact_batches=sum(x['batches_run'] for x in a.values()),ascending_exact_batches=sum(x['batches_run'] for x in b.values()),advisory_mean_chosen_batch=sum(x['advisory_batch'] for x in a.values())/128,advisory_group_worker_seconds=total(a),ascending_group_worker_seconds=total(b),compact_c_worker_seconds=sum(x['secs'] for x in c.values()),original_protected_worker_seconds=sum(x['secs'] for x in old.values()),status='DIFFERENTIAL_VALIDATION_ONLY_NO_SEARCH_NO_RECORD')
(r/'advisory-differential.json').write_text(json.dumps(rpt,indent=2)+'\n');print(json.dumps(rpt,indent=2))
