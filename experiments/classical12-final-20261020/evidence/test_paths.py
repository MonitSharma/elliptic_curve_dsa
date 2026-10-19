"""Native inputs can be checked early; complete readiness requires every gate."""
import hashlib,importlib.util,json,struct,sys,tarfile
from pathlib import Path
r=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('final',r/'finalize.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
assert f.native==r.parent/'product-classical-twelve-native-20261019'
assert f.old_stream==f.native/'candidate/ops.bin' and f.N_OPS==17889635
freeze=json.loads((f.native/'SOURCE_FREEZE.json').read_text());manifest=freeze['source_files']
assert len(manifest)==180 and len(freeze['protected_files'])==17
archive=f.native/'point-add-source.tar.gz';assert sha(archive)==f.archive_hash==freeze['source_archive_sha256']
with tarfile.open(archive) as a:
    members=a.getmembers();assert all((m.isfile() or m.isdir()) and (m.name+'/').startswith('src/point_add/') and '..' not in Path(m.name).parts for m in members)
    assert {m.name for m in members if m.isfile()}==set(manifest)
    for name,h in manifest.items():assert hashlib.sha256(a.extractfile(name).read()).hexdigest()==h,name
assert all(sha(f.native/'candidate'/p)==h for p,h in {**manifest,**freeze['protected_files']}.items())
assert sha(f.old_stream)==f.old_stream_hash
with f.old_stream.open('rb') as stream:header=stream.read(16)
assert header[:8]==b'QECCOPSZ' and struct.unpack_from('<Q',header,8)[0]==f.N_OPS
complete='--complete' in sys.argv
result={'status':'NATIVE_INPUTS_VERIFIED_OTHER_GATES_PENDING','native_directory':str(f.native),'source_files':len(manifest),'protected_files':17,'source_archive_sha256':sha(archive),'old_stream_sha256':sha(f.old_stream),'scope':'Read-only source/path audit, not a native benchmark, nonce result or complete readiness claim.'}
if complete:
    search=r.parent/'product-classical-twelve-operational-20261019';acc=json.loads((search/'ACCEPTANCE.json').read_text());gate=json.loads((f.native/'qualification/RESULT.json').read_text())
    assert gate['status']=='FAILURE_GATE_PASS' and all(gate['rules'].values()) and acc['failure_gate']==gate
    assert gate['label']=='pareto-parent4-classical12-gate-20261019-v1' and gate['batches']==262144
    for p,h in acc['runtime_artifacts'].items():assert sha(Path(p))==h,p
    for name,h in gate['census_sha256'].items():assert sha(f.native/'qualification'/(name+'.jsonl'))==h
    assert sum(1 for _ in (f.native/'qualification/candidate.jsonl').open())==262144
    assert json.loads((search/'CONTROL.json').read_text())['status']=='CONTROL_ROWS_EQUAL_QUALIFIED_PREFIX'
    binding=json.loads((r/'RUNTIME-BINDING.json').read_text());assert binding['acceptance_sha256']==sha(search/'ACCEPTANCE.json') and binding['binary_sha256']==sha(search/'tool/target/release/value_prefilter')
    assert binding['auditor_sha256']==sha(r/'audit-terminal.py')
    assert (f.ws/'simd-census-v2-20261016/bin/simd_census_v2').is_file()
    result.update(status='CLASSICAL12_FINALIZER_ALL_INPUT_PATHS_AND_HASHES_PASS',runtime_artifacts_checked=len(acc['runtime_artifacts']),gate_sha256=sha(f.native/'qualification/RESULT.json'),existing_gate_rows=262144)
out=r/('PATH-CONTROL.json' if complete else 'NATIVE-INPUT-CONTROL.json');assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
