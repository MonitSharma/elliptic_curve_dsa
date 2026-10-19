"""Refine attribution on the same frozen stream and existing fresh inputs."""
import hashlib,json,os,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert(r/'run-v2.exit').read_text().strip()=='0'
freeze=json.loads((r/'SOURCE_FREEZE-v2.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(r/'observer'/p)==h for p,h in{**freeze['source_files'],**freeze['protected_files']}.items())
assert sha(r/'observer/ops.bin')==freeze['expected_native_raw_sha256']
try:
 with(r/'segments-v2.log').open('xb')as log:
  subprocess.run(['python3',str(r/'segments-v2.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
 env=os.environ.copy();env['PHASE_MAP']=str(r/'segment-map-v2.tsv')
 with(r/'replay-v2.out').open('xb')as out,(r/'replay-v2.err').open('xb')as err:
  subprocess.run([str(r.parent/'breakthrough-profile-20261020/tool/target/release/phase-replay'),str(r/'observer/ops.bin'),
  'breakthrough-raw-subphase-cost-v1','0','512','2',str(r/'region-census-v2.jsonl'),'8'],env=env,stdout=out,stderr=err,check=True)
 a=[json.loads(l)for l in(r/'region-census.jsonl').read_text().splitlines()]
 b=[json.loads(l)for l in(r/'region-census-v2.jsonl').read_text().splitlines()]
 assert len(a)==len(b)==512
 for x,y in zip(a,b):
  assert sum(x.pop('regional_toffoli'))==x['toffoli'];assert sum(y.pop('regional_toffoli'))==y['toffoli'];assert x==y
 (r/'REFINEMENT-CONTROL.json').write_text(json.dumps({'status':'ALL_512_REFINED_ROWS_MATCH_ORIGINAL_DIAGNOSTIC_ROWS','source_unchanged':True,
 'old_rows_sha256':sha(r/'region-census.jsonl'),'refined_rows_sha256':sha(r/'region-census-v2.jsonl'),'scope':'Same existing inputs, no statistical gate or circuit variation.'},indent=2)+'\n')
except BaseException:
 (r/'refine.exit').write_text('1\n');raise
else:(r/'refine.exit').write_text('0\n')
