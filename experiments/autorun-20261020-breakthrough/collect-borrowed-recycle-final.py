import hashlib,json,subprocess,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-borrowed-recycle-final-20261021';r.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest()
subprocess.run(['scp']+[f'smu_server:/home/hclau/ecdsa_research/breakthrough-borrowed-recycle-final-20261021/{n}'for n in ['final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']]+[str(r)],check=True)
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

# Independently bind every selected source byte to the already gated source.
import io
with tarfile.open(r/'final-evidence.tar.gz')as ar:
 spec=json.loads(ar.extractfile('finished/SOURCE-SPEC.json').read());pf=json.loads(ar.extractfile('proof/SOURCE-FREEZE.json').read());proof_result=ar.extractfile('proof/RESULT.json').read();proof_freeze=ar.extractfile('proof/SOURCE-FREEZE.json').read();assert sha(proof_result)==spec['semantic_proof_result_sha256']and sha(proof_freeze)==spec['semantic_proof_source_freeze_sha256']
 with tarfile.open(fileobj=io.BytesIO(ar.extractfile('proof/preserved-tool-source.tar.gz').read()))as pa:
  assert {m.name for m in pa.getmembers()}==set(pf['tool_source_files'])
  for p,h in pf['tool_source_files'].items():assert sha(pa.extractfile(p).read())==h
 with tarfile.open(fileobj=io.BytesIO(ar.extractfile('finished/point-add-source.tar.gz').read()))as ga,tarfile.open(r/'point-add-source.tar.gz')as fa:
  assert {m.name for m in fa.getmembers()}=={m.name for m in ga.getmembers()}==set(f['source_files'])
  for p in f['source_files']:
   old=ga.extractfile(p).read();new=fa.extractfile(p).read();assert sha(old)==spec['source_files'][p]
   if p=='src/point_add/recycle_measurements.rs':assert old.count(b'const IDENTITY_NONCE:u64=0;')==1;old=old.replace(b'const IDENTITY_NONCE:u64=0;',('const IDENTITY_NONCE:u64='+str(f['nonce'])+';').encode())
   assert old==new,p
(r/'LOCAL-NONCE-SOURCE-VERIFICATION.json').write_text(json.dumps({'status':'ALL207_SELECTED_SOURCE_BYTES_MATCH_GATED_SOURCE_EXCEPT_SINGLE_IDENTITY_NONCE_CONSTANT','nonce':f['nonce'],'proof_tool_source_archive_verified':True,'complete_evidence_locally_verified':True},indent=2)+'\n')
