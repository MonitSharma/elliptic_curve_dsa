"""Verify every saved member and replay rank with the other pivot order."""
import hashlib,json,subprocess,tarfile
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;r=ws/'product-peak-parity-probe-20261020'
for filename in ['EVIDENCE-MANIFEST.json','evidence.tar.gz']:subprocess.run(['scp','smu_server:/home/hclau/ecdsa_research/'+r.name+'/'+filename,str(r/filename)],check=True)
info=json.loads((r/'EVIDENCE-MANIFEST.json').read_text());sha=hashlib.file_digest((r/'evidence.tar.gz').open('rb'),'sha256').hexdigest();assert sha==info['sha256']
with tarfile.open(r/'evidence.tar.gz') as a:
 manifest=json.load(a.extractfile('SNAPSHOT-MANIFEST.json'));files=manifest['included_files'];assert len(files)==info['files']
 for key,v in files.items():
  assert a.getmember(key).size==v['bytes'] and hashlib.file_digest(a.extractfile(key),'sha256').hexdigest()==v['sha256'],key
  if key in ['RESULT.json','base.json','probe.json'] or key.startswith('snapshot-'):
   (r/key).write_bytes(a.extractfile(key).read())
result=json.loads((r/'RESULT.json').read_text());assert (r/'base.json').read_bytes()==(r/'probe.json').read_bytes();replays=[]
for state in result['states']:
 p=r/f"snapshot-{state['after_source_op']}.json";assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==state['snapshot_sha256']
 q=json.loads(p.read_text())['q'][:-1];terms=sorted({tuple(m) for poly in q for m in poly if m});cols={m:i for i,m in enumerate(terms)};basis={}
 for poly in q:
  row=sum(1<<cols[tuple(m)] for m in poly if m)
  while row:
   pivot=(row&-row).bit_length()-1  # Opposite pivot order from server.
   if pivot not in basis:basis[pivot]=row;break
   row^=basis[pivot]
 assert len(basis)==state['rank']==1233
 replays.append({'after_source_op':state['after_source_op'],'rank':len(basis),'rows':len(q),'monomials':len(terms),'opposite_pivot_order':True})
(r/'LOCAL-VERIFICATION.json').write_text(json.dumps({'status':'ALL_ARCHIVE_MEMBERS_AND_OPPOSITE_PIVOT_RANK_REPLAY_PASS','files':len(files),'sha256':sha,'replays':replays,'no_width_lower_bound_or_score':True},indent=2)+'\n');print('Verified complete prefix/rank evidence; both opposite-pivot rank replays1233',flush=True)
