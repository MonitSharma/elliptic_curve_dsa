from pathlib import Path
import hashlib,json,shutil,tarfile
r=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert (r/'final.exit').read_text().strip()=='0'
result=json.loads((r/'BENCHMARK_RESULT.json').read_text())
assert result['status']=='UNCHANGED_BENCHMARK_PASS'
freeze=json.loads((r/'SOURCE_FREEZE.json').read_text())
assert sha(r/'SOURCE_FREEZE.json')==result['source_freeze_sha256']
assert sha(r/'candidate/ops.bin')==result['candidate_stream_sha256']
for p,h in freeze['source_files'].items(): assert sha(r/'candidate'/p)==h,p
with tarfile.open(r/'point-add-source.tar.gz') as a:
    assert {m.name:hashlib.sha256(a.extractfile(m).read()).hexdigest() for m in a.getmembers()}==freeze['source_files']
dest=r/'benchmark-artifacts';assert not dest.exists();dest.mkdir()
for p in sorted(r.iterdir()):
    if p.is_file() and p.suffix in ('.json','.py','.sh','.log','.pid','.exit','.patch','.md','.tsv'):
        shutil.copy2(p,dest/p.name)
for p in ['score.json','results.tsv','point-add-source.tar.gz']:
    shutil.copy2(r/p,dest/p)
for p in ['benchmark.sh','src/bin/build_circuit.rs','src/bin/eval_circuit.rs',
          'target/release/build_circuit','target/release/eval_circuit','ops.bin']:
    out=dest/'native'/p;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/'candidate'/p,out)
for p,h in freeze['protected_files'].items():
    assert sha(r/'candidate'/p)==h,p
    out=dest/'protected'/p;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/'candidate'/p,out)
files={str(p.relative_to(dest)):sha(p) for p in sorted(dest.rglob('*')) if p.is_file()}
(dest/'MANIFEST.json').write_text(json.dumps(files,indent=2)+'\n')
archive=r/'benchmark-evidence.tar.gz'
with tarfile.open(archive,'w:gz',compresslevel=6) as a:
    for p in sorted(dest.rglob('*')):
        if p.is_file(): a.add(p,arcname=str(p.relative_to(dest)),recursive=False)
parts=[]
with archive.open('rb') as f:
    index=1
    while data:=f.read(40*1024*1024):
        p=r/f'benchmark-evidence.tar.gz.part{index:02d}';p.write_bytes(data)
        parts.append({'name':p.name,'bytes':len(data),'sha256':sha(p)});index+=1
receipt={'status':'UNCHANGED_BENCHMARK_NATIVE_SOURCE_ARCHIVED','archive':archive.name,
  'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'files':len(files),
  'parts':parts,'candidate_stream_sha256':result['candidate_stream_sha256'],
  'source_freeze_sha256':result['source_freeze_sha256'],'benchmark_result_sha256':sha(r/'BENCHMARK_RESULT.json'),
  'final_fresh_census':'separate parent-owned predeclared gate; not included or claimed here',
  'submission_mode':'queue','reassembly':'Concatenate parts in listed order; verify archive SHA256; extract and verify MANIFEST.json.'}
(r/'benchmark-evidence.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2),flush=True)
