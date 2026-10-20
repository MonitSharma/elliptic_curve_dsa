import hashlib,json,subprocess,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
names=['breakthrough-value-dominance-audit-20261020','breakthrough-value-boolean-reset-audit-20261020']
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
for name in names:
 r=root/'experiments'/name;r.mkdir(exist_ok=True)
 for filename in ['PACKAGE-RESULT.json','EVIDENCE-MANIFEST.json','evidence.tar.gz']:
  dest=r/filename
  if not dest.exists():subprocess.run(['scp',f'smu_server:/home/hclau/ecdsa_research/{name}/{filename}',str(dest)],check=True)
 receipt=json.loads((r/'PACKAGE-RESULT.json').read_bytes());manifest=json.loads((r/'EVIDENCE-MANIFEST.json').read_bytes())
 assert sha(r/'evidence.tar.gz')==receipt['archive_sha256']and sha(r/'EVIDENCE-MANIFEST.json')==receipt['manifest_sha256']
 conflicts=[]
 with tarfile.open(r/'evidence.tar.gz')as archive:
  members=archive.getmembers();assert len(members)==receipt['members']and{m.name for m in members}==set(manifest['files'])|{'EVIDENCE-MANIFEST.json'}
  for member in members:
   assert member.isfile();path=Path(member.name);assert not path.is_absolute()and'..'not in path.parts
   data=archive.extractfile(member).read();expected=receipt['manifest_sha256']if member.name=='EVIDENCE-MANIFEST.json'else manifest['files'][member.name]
   assert hashlib.sha256(data).hexdigest()==expected
   existing=r/path
   if existing.exists()and existing.read_bytes()!=data:conflicts.append(member.name)
   dest=r/'original-evidence'/path
   if dest.exists():assert dest.read_bytes()==data
   else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 (r/'LOCAL-VERIFICATION.json').write_text(json.dumps({'status':'EVERY_ARCHIVE_MEMBER_VERIFIED_LOCALLY_IN_ORIGINAL_EVIDENCE','members':len(members),'archive_sha256':receipt['archive_sha256'],'terminal_status':manifest['audit']['status'],'local_metadata_differences_preserved':conflicts},indent=2)+'\n')
 (r/'.gitattributes').write_text('* -text\n')
 p=r/'.gitignore';prior=p.read_text()if p.exists()else''
 for line in ['tool/','evidence.tar.gz','*resource-preflight*']:
  if line not in prior.splitlines():prior+=line+'\n'
 p.write_text(prior)
 print(name,len(members),'verified; local differences preserved:',','.join(conflicts),flush=True)
