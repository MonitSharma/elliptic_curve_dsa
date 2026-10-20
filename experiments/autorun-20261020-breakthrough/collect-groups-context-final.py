import hashlib,json,subprocess,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-groups-context-final-20261020';r.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest()
for filename in['final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']:
 dest=r/filename;assert not dest.exists();subprocess.run(['scp',f'smu_server:/home/hclau/ecdsa_research/breakthrough-groups-context-final-20261020/{filename}',str(dest)],check=True)
manifest=json.loads((r/'EVIDENCE-MANIFEST.json').read_bytes());receipt=json.loads((r/'PACKAGE-RESULT.json').read_bytes());assert sha((r/'final-evidence.tar.gz').read_bytes())==receipt['archive_sha256']
with tarfile.open(r/'final-evidence.tar.gz')as archive:
 members=archive.getmembers();assert len(members)==receipt['members']and{m.name for m in members}==set(manifest['files'])|{'EVIDENCE-MANIFEST.json'}
 for p,h in manifest['files'].items():assert sha(archive.extractfile(p).read())==h,p
 assert sha(archive.extractfile('EVIDENCE-MANIFEST.json').read())==receipt['manifest_sha256']
 for member in members:
  assert member.isfile()and not Path(member.name).is_absolute()and'..'not in Path(member.name).parts and'resource-preflight'not in member.name
  if '/'not in member.name and member.name!='EVIDENCE-MANIFEST.json':
   dest=r/member.name;data=archive.extractfile(member).read()
   if dest.exists():assert dest.read_bytes()==data,member.name
   else:dest.write_bytes(data)
review=json.loads((r/'FINAL-VERIFICATION.json').read_bytes());f=json.loads((r/'SOURCE-FREEZE.json').read_bytes());assert len(f['source_files'])==205 and len(f['protected_files'])==17;assert sha((r/'point-add-source.tar.gz').read_bytes())==review['source_archive_sha256']and sha((r/'source.patch').read_bytes())==review['source_patch_sha256']
with tarfile.open(r/'point-add-source.tar.gz')as archive:
 assert{m.name for m in archive.getmembers()}==set(f['source_files'])
 for p,h in f['source_files'].items():assert p.startswith('src/point_add/')and sha(archive.extractfile(p).read())==h
(r/'LOCAL-VERIFICATION.json').write_bytes((json.dumps({'status':'EVERY_FINAL_EVIDENCE_AND_SOURCE_MEMBER_VERIFIED_LOCALLY','archive_sha256':receipt['archive_sha256'],'members':len(members),'source_files':205,'source_revision':review['source_revision'],'scope':'Complete local benchmark reproduction, ready for authorized automatic submission; not officially evaluated.'},indent=2)+'\n').encode());print('Verified every final native-both evidence/source member:',len(members),'evidence,205 source')
