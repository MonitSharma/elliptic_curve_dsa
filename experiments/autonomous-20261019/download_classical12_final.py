"""Verify complete native final evidence locally before documenting a result."""
import hashlib,json,subprocess,tarfile
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;r=ws/'classical12-final-20261020'
for name in ['FINAL-EVIDENCE.json','QUEUED-READY.json','final-evidence.tar.gz']:
 subprocess.run(['scp','smu_server:/home/hclau/ecdsa_research/'+r.name+'/'+name,str(r/name)],check=True)
info=json.loads((r/'FINAL-EVIDENCE.json').read_text());p=r/'final-evidence.tar.gz';sha=hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert sha==info['sha256']
with tarfile.open(p) as a:
 manifest=json.load(a.extractfile('SNAPSHOT-MANIFEST.json'));files=manifest['included_files'];assert len(files)==info['files']
 for key,v in files.items():
  assert a.getmember(key).isfile() and '..' not in Path(key).parts and not Path(key).is_absolute()
  data=a.extractfile(key).read();assert len(data)==v['bytes'] and hashlib.sha256(data).hexdigest()==v['sha256'],key
  target=r/'evidence'/key;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 for key in ['BENCHMARK_RESULT.json','INDEPENDENT-FINAL-AUDIT.json','SOURCE_FREEZE.json','NATIVE_RECEIPT.json','ROOT_TERMINAL_AUDIT.json','TAILCHECK.json','SUBMISSION-NOTE.md','PUBLIC-FINAL-CHECK.json','DISCLOSED-CENSUS-COUNTS.json']:
  data=a.extractfile(key).read();target=r/key;assert not target.exists() or target.read_bytes()==data;target.write_bytes(data)
audit=json.loads((r/'INDEPENDENT-FINAL-AUDIT.json').read_text());score=json.loads((r/'evidence/score.json').read_text());bench=json.loads((r/'BENCHMARK_RESULT.json').read_text());freeze=json.loads((r/'SOURCE_FREEZE.json').read_text())
assert audit['status']=='ALL_FINAL_REQUIREMENTS_INDEPENDENTLY_VERIFIED_COMPLETE_LOCAL_PRODUCT_IMPROVEMENT'
assert audit['product']==bench['product']==score['score']==audit['qubits']*audit['rounded_mean_executed_toffoli']<audit['public_product']
assert audit['nonce']==7614812 and audit['production_unique_screened']==7811072 and audit['unchanged_benchmark_shots']==9024 and audit['benchmark_failures']==0
archive=r/'evidence/point-add-source.tar.gz';assert hashlib.file_digest(archive.open('rb'),'sha256').hexdigest()==freeze['selected_source_archive_sha256']
with tarfile.open(archive) as a:
 assert {m.name for m in a.getmembers() if m.isfile()}==set(freeze['source_files']) and len(freeze['source_files'])==180
 for name,h in freeze['source_files'].items():assert hashlib.sha256(a.extractfile(name).read()).hexdigest()==h
log=(r/'evidence/benchmark.log').read_text();assert 'all 9024 shots OK' in log and '=== experiment OK ===' in log
(r/'LOCAL-FINAL-VERIFICATION.json').write_text(json.dumps({'status':'COMPLETE_FINAL_ARCHIVE_ALL_MEMBERS_AND_SELECTED_SOURCE_VERIFIED_LOCALLY','files':len(files),'sha256':sha,'metrics':audit,'no_official_upload':True},indent=2)+'\n')
print(json.dumps(audit,indent=2),flush=True)
