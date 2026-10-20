"""Verify all archived bytes locally; only copy selected root artifacts."""
import hashlib,json,subprocess,sys,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
allowed=['breakthrough-fold-square-20261020','breakthrough-fold-square-ripple-20261020','breakthrough-fold-square-short-20261020','breakthrough-hardcap-audit-20261020','breakthrough-phase-bridge-20261020','breakthrough-phase-fusion-20261020','breakthrough-phase-sites-20261020','breakthrough-hardcarry-20261020','breakthrough-paused-read-20261020','breakthrough-paused-pool-audit-20261020']
for name in sys.argv[1:]:
 assert name in allowed;r=root/'experiments'/name;r.mkdir(exist_ok=True)
 subprocess.run(['scp']+[f'smu_server:/home/hclau/ecdsa_research/{name}/{file}'for file in['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']]+[str(r)],check=True)
 receipt=json.loads((r/'PACKAGE-RESULT.json').read_bytes());manifest=json.loads((r/'EVIDENCE-MANIFEST.json').read_bytes())
 assert hashlib.sha256((r/'evidence.tar.gz').read_bytes()).hexdigest()==receipt['archive_sha256']
 with tarfile.open(r/'evidence.tar.gz')as archive:
  members=archive.getmembers();assert len(members)==receipt['members'];assert{m.name for m in members}==set(manifest['files'])|{'EVIDENCE-MANIFEST.json'}
  for path,sha in manifest['files'].items():assert hashlib.sha256(archive.extractfile(path).read()).hexdigest()==sha,path
  assert hashlib.sha256(archive.extractfile('EVIDENCE-MANIFEST.json').read()).hexdigest()==receipt['manifest_sha256']
  for m in members:
   if '/'not in m.name and(m.name.endswith('.json')or m.name.endswith('.rs'))and m.name!='EVIDENCE-MANIFEST.json':(r/m.name).write_bytes(archive.extractfile(m).read())
 (r/'LOCAL-VERIFICATION.json').write_text(json.dumps({'status':'EVERY_ARCHIVE_MEMBER_VERIFIED_LOCALLY','archive_sha256':receipt['archive_sha256'],'members':len(members)},indent=2)+'\n')
 print(name,len(members),'members verified',flush=True)
