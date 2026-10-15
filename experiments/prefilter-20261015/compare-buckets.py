import json,math,re
from pathlib import Path
r=Path(__file__).parent/'evidence'
def load(n):return {x['nonce']:x for x in map(json.loads,(r/(n+'.jsonl')).read_text().splitlines())}
names=['advisory-1024','bucket-1024','bucket-fast-1024'];rows={n:load(n)for n in names};base=rows[names[0]]
assert set(base)==set(range(1,1025))
for name,data in rows.items():
 assert set(data)==set(base)
 assert all(data[k]['pass']==base[k]['pass']for k in base)
 assert all(x['rejection_policy']=='exact_full_state_only' and x['exact_witness_batch'] is not None for x in data.values())
reports={}
for name,data in rows.items():
 text=(r/(name+'.log')).read_text();wall=float(re.search(r'wall_seconds=([0-9.]+)',text)[1]);reports[name]=dict(wall_seconds=wall,workers=2,nominal_worker_seconds=2*wall,exact_batches=sum(x['batches_run']for x in data.values()),nonces_with_fallback=sum(x['batches_run']>1 for x in data.values()),no_advisory_hit=sum(not x.get('advisory_hit',True)for x in data.values()),mean_selected_batch=sum(x['advisory_batch']for x in data.values())/1024)
positive={}
for name in ['advisory-positive','advisory-no-hit-positive','advisory-lowest-positive','bucket-positive9','bucket-fast-positive9']:
 log=r/(name+'.log')
 if log.exists():
  text=log.read_text();positive[name]=dict(protected_official_pass='SELECTED_OFFICIAL_REPLAY nonce=1046072871510 ok=true shots=9024 classical=0 phase=0 ancilla=0'in text,rows=len(load(name)))
pfail=4144/32768;p=(1-pfail)**141;latest=reports['bucket-fast-1024']['nominal_worker_seconds']/1024
report=dict(source='4b2ec52f',predetermined_nonces=1024,truth_equal=True,all_rejected=all(not x['pass']for x in base.values()),runs=reports,positive_controls=positive,projection_only=dict(candidate_failed_batches=4144,candidate_census_batches=32768,assumed_independent_batches=141,packet_pass_probability=p,expected_nonces=1/p,latest_nominal_worker_seconds_per_nonce=latest,ideal64_worker_hours=latest/p/64/3600),status='VALIDATION_AND_COST_PROJECTION_ONLY_NO_NEW_SEARCH')
(r/'bucket-differential.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
