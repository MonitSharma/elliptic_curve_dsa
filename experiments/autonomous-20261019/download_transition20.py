"""Preserve actual launch/retirement/disabled-build artifacts without live rows."""
import hashlib,json,subprocess,tarfile
from pathlib import Path
ws=Path(__file__).resolve().parent.parent
for name,receipt in [('classical9-retirement-20261020','TRANSITION20.json'),('product-classical-twelve-operational-20261019','TRANSITION20.json'),('product-copy-cache-filter-20261020','TRANSITION20.json'),('product-copy-cache-native-20261020','GATE-DECLARATION20.json')]:
 r=ws/name;r.mkdir(exist_ok=True)
 subprocess.run(['scp','smu_server:/home/hclau/ecdsa_research/'+name+'/'+receipt,str(r/receipt)],check=True)
 info=json.loads((r/receipt).read_text());archive=info['archive']
 subprocess.run(['scp','smu_server:/home/hclau/ecdsa_research/'+name+'/'+archive,str(r/archive)],check=True)
 sha=hashlib.file_digest((r/archive).open('rb'),'sha256').hexdigest();assert sha==info['sha256']
 with tarfile.open(r/archive) as a:
  manifest=json.load(a.extractfile('SNAPSHOT-MANIFEST.json'));files=manifest['included_files'];assert len(files)==info['files']
  for key,v in files.items():
   raw=a.extractfile(key).read();assert len(raw)==v['bytes'] and hashlib.sha256(raw).hexdigest()==v['sha256'],key
   if key.endswith(('.json','.py','.sh')) and '/' not in key:
    p=r/'transition20-receipts'/key;p.parent.mkdir(exist_ok=True);p.write_bytes(raw)
 (r/'LOCAL-TRANSITION20-VERIFICATION.json').write_text(json.dumps({'status':'ARCHIVE_AND_EVERY_INCLUDED_MEMBER_VERIFIED','archive_sha256':sha,'files':len(files)},indent=2)+'\n');print(name,len(files),sha,flush=True)
