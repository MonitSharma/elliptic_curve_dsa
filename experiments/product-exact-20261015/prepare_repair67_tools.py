"""Derive isolated67 admission helpers from the successful53 pipeline."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();created={}
for name in ['prepare_repair53_native.py','qualify_repair53_native.py','run_repair53_census.py','run-repair53-native.sh','run-repair53-census.sh']:
    before=r/name;after=r/name.replace('repair53','repair67');assert not after.exists();text=before.read_text()
    for a,b in [('repair53-native-20261016','repair67-native-20261016'),('frozen_cache_repair53','frozen_cache_repair67'),('REPAIR53_FREEZE.json','REPAIR67_FREEZE.json'),('REPAIR53_FRESH_CENSUS_PLAN.json','REPAIR67_FRESH_CENSUS_PLAN.json'),('prepare_repair53_native.py','prepare_repair67_native.py'),('qualify_repair53_native.py','qualify_repair67_native.py'),('run_repair53_census.py','run_repair67_census.py'),('NATIVE_REPAIRED53','NATIVE_REPAIRED67'),('repair53-census-summary.json','repair67-census-summary.json')]:text=text.replace(a,b)
    # Deliberately retain repair-cache53 A29 input/source snapshots: the parent
    # function and prefix binding are unchanged; only the exact cache endpoint differs.
    assert 'repair-cache67-20261016' not in text;after.write_text(text,newline='\n');created[after.name]={'parent':name,'parent_sha256':sha(before),'sha256':sha(after)}
declaration=r/'repair-to67-rank-20261016/DECLARATION.json';decl=json.loads(declaration.read_text());gate=decl['fresh_gate'];plan=json.loads((r/'REPAIR53_FRESH_CENSUS_PLAN.json').read_text())
assert gate['first_batch']==0 and gate['batches_each']==32768 and gate['shots_per_batch']==64
plan.update(scope='Field-normalized copy of the fresh gate already fixed before generation in repaired67 declaration; no sample or source selection change.',label=gate['label'],candidate='Predetermined final67-stage exact-cache recipe on unchanged frozen A29 parent; final hash and normal native full-byte identity must be established before launch.',declaration_sha256=sha(declaration),source_jobs_sequential=True)
assert plan['original_reference_sha256']==gate['original_stream_sha256'] and plan['runner_sha256']==gate['runner_sha256'];p=r/'REPAIR67_FRESH_CENSUS_PLAN.json';assert not p.exists();p.write_text(json.dumps(plan,indent=2)+'\n',newline='\n');created[p.name]={'sha256':sha(p),'source_declaration_sha256':sha(declaration)}
(r/'REPAIR67_PIPELINE_PROVENANCE.json').write_text(json.dumps(created,indent=2)+'\n',newline='\n');print(json.dumps(created,indent=2),flush=True)
