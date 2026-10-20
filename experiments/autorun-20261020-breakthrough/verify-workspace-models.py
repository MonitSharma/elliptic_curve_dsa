import gzip,hashlib,json,tarfile
from pathlib import Path
r=Path(__file__).resolve().parents[2];sha=lambda b:hashlib.sha256(b).hexdigest()
p=r/'experiments/breakthrough-core-closure-20261020';m=json.loads((p/'EVIDENCE-MANIFEST.json').read_bytes());receipt=json.loads((p/'PACKAGE-RESULT.json').read_bytes());assert sha((p/'evidence.tar.gz').read_bytes())==receipt['archive_sha256']
with tarfile.open(p/'evidence.tar.gz')as a:
 assert len(a.getmembers())==receipt['members']
 for name,h in m['files'].items():
  assert '/'not in name and '\\'not in name
  data=a.extractfile(name).read();assert sha(data)==h
  (p/name).write_bytes(data)
 assert sha(a.extractfile('EVIDENCE-MANIFEST.json').read())==receipt['manifest_sha256']
(p/'LOCAL-VERIFICATION.json').write_text(json.dumps({'status':'EVERY_LEGACY_MODEL_ARCHIVE_MEMBER_VERIFIED','members':receipt['members'],'archive_sha256':receipt['archive_sha256'],'scope':'Inactive helper only, not a current resource result.'},indent=2)+'\n')
b=r/'experiments/breakthrough-assessment-20261020';latest=json.loads((b/'LATEST.json').read_bytes());p=b/latest['snapshot'];assert not(p/'SNAPSHOT-MANIFEST.json').exists();raw=(p/'public-submissions.json').read_bytes();(p/'public-submissions.json.gz').write_bytes(gzip.compress(raw,mtime=0));files=['leader-product.json','leader-qubits.json','leader-toffoli.json','PUBLIC-RECORDS.json','public-submissions.json.gz'];(p/'SNAPSHOT-MANIFEST.json').write_text(json.dumps({'raw_api_sha256':sha(raw),'files':{n:sha((p/n).read_bytes())for n in files},'scope':'Fresh immutable public snapshot. Prior snapshots remain historical evidence.'},indent=2)+'\n')
p=r/'experiments/breakthrough-live-core-rank-20261020';files=['model.py','FUNCTIONS.json','quadratic-loans.py','QUADRATIC-LOAN-MODEL.json','quadratic-loans-reverse.py','QUADRATIC-LOAN-REVERSE-MODEL.json','factor-loans.py','FACTORED-LOANS.json','sparse-rebuild.py','SPARSE-REBUILD.json'];(p/'WORKSPACE-MODEL-MANIFEST.json').write_text(json.dumps({'files':{n:sha((p/n).read_bytes())for n in files},'scope':'Exact source-function models; native implementation has failed initial phase/roundtrip tests and is under diagnosis. No point-add resource result.'},indent=2)+'\n')
print('Legacy archive verified; public snapshot sealed; workspace model hashes recorded.')
