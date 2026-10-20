import hashlib,json,subprocess,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-public8b-repeat-final-20261020';r.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest()
subprocess.run(['scp']+[f'smu_server:/home/hclau/ecdsa_research/breakthrough-public8b-repeat-final-20261020/{n}'for n in ['final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']]+[str(r)],check=True)
manifest=json.loads((r/'EVIDENCE-MANIFEST.json').read_bytes());receipt=json.loads((r/'PACKAGE-RESULT.json').read_bytes());assert sha((r/'final-evidence.tar.gz').read_bytes())==receipt['archive_sha256']
with tarfile.open(r/'final-evidence.tar.gz')as a:
 members=a.getmembers();assert len(members)==receipt['members'];assert{m.name for m in members}==set(manifest['files'])|{'EVIDENCE-MANIFEST.json'}
 for p,h in manifest['files'].items():assert sha(a.extractfile(p).read())==h,p
 assert sha(a.extractfile('EVIDENCE-MANIFEST.json').read())==receipt['manifest_sha256']
 for m in members:
  assert m.isfile()and not Path(m.name).is_absolute()and'..'not in Path(m.name).parts and'resource-preflight'not in m.name
  if '/'not in m.name and m.name!='EVIDENCE-MANIFEST.json':(r/m.name).write_bytes(a.extractfile(m).read())
review=json.loads((r/'FINAL-VERIFICATION.json').read_bytes());f=json.loads((r/'SOURCE-FREEZE.json').read_bytes());assert sha((r/'point-add-source.tar.gz').read_bytes())==review['source_archive_sha256'];assert sha((r/'source.patch').read_bytes())==review['source_patch_sha256']
with tarfile.open(r/'point-add-source.tar.gz')as a:
 assert{m.name for m in a.getmembers()}==set(f['source_files'])
 for p,h in f['source_files'].items():assert p.startswith('src/point_add/')and sha(a.extractfile(p).read())==h
(r/'LOCAL-VERIFICATION.json').write_bytes((json.dumps({'status':'EVERY_FINAL_EVIDENCE_AND_SOURCE_MEMBER_VERIFIED_LOCALLY','archive_sha256':receipt['archive_sha256'],'members':len(members),'source_files':len(f['source_files']),'source_revision':review['source_revision'],'scope':'Complete local benchmark reproduction, ready for authorized automatic submission; not officially evaluated.'},indent=2)+'\n').encode());print('Final evidence and full source verified locally:',len(members),'evidence members;',len(f['source_files']),'source files')
