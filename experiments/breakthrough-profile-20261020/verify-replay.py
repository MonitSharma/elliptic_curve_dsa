"""Compare every diagnostic row with the unchanged original replay binary."""
import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert (r/'replay.exit').read_text().strip()=='0'
with (r/'original-replay.out').open('xb')as out,(r/'original-replay.err').open('xb')as err:
 p=subprocess.Popen([str(r.parent/'simd-census-v2-20261016/bin/simd_census_v2'),str(r/'observer/ops.bin'),
  'breakthrough-cost-profile-20261020-v1','0','512','2',str(r/'original-replay.jsonl'),'0'],stdout=out,stderr=err)
 (r/'original-replay-child.pid').write_text(str(p.pid)+'\n')
 rc=p.wait()
assert rc==0
a=[json.loads(l)for l in(r/'phase-census.jsonl').read_text().splitlines()]
b=[json.loads(l)for l in(r/'original-replay.jsonl').read_text().splitlines()]
assert len(a)==len(b)==512
for x,y in zip(a,b):
 region=x.pop('regional_toffoli')
 assert sum(region)==x['toffoli']
 assert x==y,(x['batch'],x,y)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(r/'REPLAY-VERIFICATION.json').write_text(json.dumps({'status':'ALL_512_DIAGNOSTIC_ROWS_EXACTLY_MATCH_UNCHANGED_REPLAY','shots':32768,
 'scalar_full_state_phase_rng_and_toffoli_verified_batches':8,'original_binary_sha256':sha(r.parent/'simd-census-v2-20261016/bin/simd_census_v2'),
 'original_rows_sha256':sha(r/'original-replay.jsonl'),'regional_rows_sha256':sha(r/'phase-census.jsonl'),
 'all_region_sums_equal_original_total':True,'no_new_gate_or_score':True},indent=2)+'\n')
print('All512 rows match unchanged replay exactly.',flush=True)
(r/'original-control.exit').write_text('0\n')
