"""Fetch immutable server archives and verify every member locally."""
import hashlib,json,subprocess,tarfile
from pathlib import Path
ws=Path(__file__).resolve().parent.parent
names=['classical9-final-v3-20261020','classical12-final-20261020','product-classical-twelve-filter-20261019','product-classical-twelve-operational-20261019','product-classical-twelve-gate-audit-20261020','product-copy-cache-native-20261020','product-copy-cache-proof-20261020','autonomous-20261019']
for name in names:
 r=ws/name;r.mkdir(exist_ok=True)
 receipt='REGISTRY20.json' if name=='autonomous-20261019' else 'CYCLE20.json'
 archive='registry20.tar.gz' if name=='autonomous-20261019' else 'cycle20.tar.gz'
 for filename in [receipt,archive]:subprocess.run(['scp','smu_server:/home/hclau/ecdsa_research/'+name+'/'+filename,str(r/filename)],check=True)
 info=json.loads((r/receipt).read_text());sha=hashlib.file_digest((r/archive).open('rb'),'sha256').hexdigest();assert sha==info['sha256']
 with tarfile.open(r/archive) as a:
  manifest=json.load(a.extractfile('SNAPSHOT-MANIFEST.json'));files=manifest['included_files']
  assert len(files)==info['files']
  for key,v in files.items():
   raw=a.extractfile(key).read();assert len(raw)==v['bytes'] and hashlib.sha256(raw).hexdigest()==v['sha256'],key
   # Preserve exact source/row copies inside the archive; extract concise receipts only.
   if key.endswith('.json') and '/' not in key:
    p=r/'cycle20-receipts'/key;p.parent.mkdir(exist_ok=True);p.write_bytes(raw)
 (r/'LOCAL-CYCLE20-VERIFICATION.json').write_text(json.dumps({'status':'ARCHIVE_AND_EVERY_INCLUDED_MEMBER_VERIFIED','archive_sha256':sha,'files':len(files)},indent=2)+'\n')
 print(name,len(files),sha,flush=True)
