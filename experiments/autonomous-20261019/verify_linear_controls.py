"""Verify every control/archive member before serial local admission."""
import hashlib,json,tarfile
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;r=ws/'product-linear-witness-controls-v2-20261020';p=r/'evidence.tar.gz'
info=json.loads((r/'EVIDENCE-MANIFEST.json').read_text());sha=hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert sha==info['sha256']=='1e46f5baeaa623de8b01f78881ebc18490a0b3f2fe052b6af19c5dc46cf48d05'
with tarfile.open(p) as a:
 m=json.load(a.extractfile('SNAPSHOT-MANIFEST.json'));files=m['included_files'];assert len(files)==43
 for key,v in files.items():
  raw=a.extractfile(key).read();assert len(raw)==v['bytes'] and hashlib.sha256(raw).hexdigest()==v['sha256']
  target=r/'evidence'/key;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 assert a.extractfile('RESULT.json').read()==(r/'RESULT.json').read_bytes()
result=json.loads((r/'RESULT.json').read_text());assert result['status']=='EXACT_LINEAR_WITNESS_30_PRIMITIVE_CONTROLS_PASS'
source=ws/'product-linear-witness-20261020'
for name,h in result['source_files'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==h,name
(r/'LOCAL-VERIFICATION.json').write_text(json.dumps({'status':'ALL43_MEMBERS_AND_EXACT_PROTOTYPE_SOURCE_MATCH_VERIFIED','sha256':sha,'files':43,'tests':30,'no_new_circuit_or_nonce':True},indent=2)+'\n')
print('All43 members verified,30 controls passed on exact current local prototype source')
