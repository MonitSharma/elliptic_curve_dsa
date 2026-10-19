"""Verify large archived data by streaming; extract only concise receipts."""
import hashlib,json,subprocess,tarfile
from pathlib import Path
ws=Path(__file__).resolve().parent.parent
for name in ['product-lease-footprint-20261020','product-clean-lease-probe-20261020']:
 r=ws/name
 for filename in ['EVIDENCE-MANIFEST.json','evidence.tar.gz']:subprocess.run(['scp','smu_server:/home/hclau/ecdsa_research/'+name+'/'+filename,str(r/filename)],check=True)
 info=json.loads((r/'EVIDENCE-MANIFEST.json').read_text());sha=hashlib.file_digest((r/'evidence.tar.gz').open('rb'),'sha256').hexdigest();assert sha==info['sha256']
 with tarfile.open(r/'evidence.tar.gz') as a:
  manifest=json.load(a.extractfile('SNAPSHOT-MANIFEST.json'));files=manifest['included_files'];assert len(files)==info['files']
  for key,v in files.items():
   member=a.getmember(key);assert member.size==v['bytes'];assert hashlib.file_digest(a.extractfile(key),'sha256').hexdigest()==v['sha256'],key
   if key in ['RESULT.json','probe.json','base.json','SOURCE.sha256','run.pid','run.exit']:
    (r/key).write_bytes(a.extractfile(key).read())
 (r/'LOCAL-VERIFICATION.json').write_text(json.dumps({'status':'ARCHIVE_AND_EVERY_MEMBER_STREAM_HASH_VERIFIED','files':len(files),'sha256':sha,'scope':'Complete finished diagnostic evidence, not a resource record.'},indent=2)+'\n');print(name,len(files),sha,flush=True)
