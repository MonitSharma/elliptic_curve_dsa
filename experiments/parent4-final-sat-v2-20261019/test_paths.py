"""Read-only finalization input audit, before the corrected watcher is started."""
import hashlib,importlib.util,json,tarfile
from pathlib import Path
r=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('final',r/'finalize.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
accept=json.loads((r.parent/'parent4-operational-sat-20261019/ACCEPTANCE.json').read_text())
assert accept['candidate_stream_sha256']==f.old_stream_hash and sha(f.old_stream)==f.old_stream_hash
assert f.native==r.parent/'product-pareto-20261019/parent4-qualification'
gate=json.loads((f.native/'RESULT.json').read_text())
assert gate['status']=='FAILURE_GATE_PASS' and all(gate['rules'].values())
assert accept['failure_gate']==gate
archive=f.native/'point-add-source.tar.gz';assert sha(archive)==f.archive_hash
manifest=json.loads((f.native/'point-add-source.json').read_text())
with tarfile.open(archive) as a:
    members=a.getmembers()
    assert all((m.isfile() or m.isdir()) and (m.name+'/').startswith('src/point_add/') and '..' not in Path(m.name).parts for m in members)
    assert {m.name for m in members if m.isfile()}==set(manifest)
    for name,h in manifest.items():assert hashlib.sha256(a.extractfile(name).read()).hexdigest()==h,name
for path,h in accept['runtime_artifacts'].items():assert sha(path)==h,path
rows=f.native/'candidate.jsonl';count=sum(1 for _ in rows.open());assert count==32768
assert 'pareto-parent4-gate-20261019-v1'==gate['label']
assert (f.ws/'simd-census-v2-20261016/bin/simd_census_v2').is_file()
assert str(r) in (r/'run-final.sh').read_text()
result={'status':'FROZEN_PARENT4_FINALIZER_ALL_INPUT_PATHS_AND_HASHES_PASS','correct_native_qualification_directory':str(f.native),
        'source_archive_sha256':sha(archive),'source_files':len(manifest),'runtime_artifacts_checked':len(accept['runtime_artifacts']),
        'frozen_gate_sha256':sha(f.native/'RESULT.json'),'existing_gate_rows':count,'no_gate_repetition_or_nonce_search':True,
        'old_stale_path':'/home/hclau/ecdsa_research/product67-native-20261016/product67',
        'scope':'Read-only path/hash/archive/gate audit. Actual native generation and benchmark still wait for a certifiable lowest nonce.'}
(r/'PATH-CONTROL.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
