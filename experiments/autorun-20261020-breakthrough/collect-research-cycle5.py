import hashlib,json,subprocess,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
names=['breakthrough-grouped-compact-width-v7-20261020', 'breakthrough-grouped-compact-width-v8-20261020', 'breakthrough-grouped-compact-width-v9-20261020', 'breakthrough-zero-lifetime-audit-20261020']
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
for name in names:
 r=root/'experiments'/name;r.mkdir(exist_ok=True)
 for filename in ['PACKAGE-RESULT.json','EVIDENCE-MANIFEST.json','evidence.tar.gz']:
  dest=r/filename;assert not dest.exists();subprocess.run(['scp',f'smu_server:/home/hclau/ecdsa_research/{name}/{filename}',str(dest)],check=True)
 receipt=json.loads((r/'PACKAGE-RESULT.json').read_text());manifest=json.loads((r/'EVIDENCE-MANIFEST.json').read_text());assert sha(r/'evidence.tar.gz')==receipt['archive_sha256']and sha(r/'EVIDENCE-MANIFEST.json')==receipt['manifest_sha256']
 with tarfile.open(r/'evidence.tar.gz')as archive:
  members=archive.getmembers();assert len(members)==receipt['members']and{m.name for m in members}==set(manifest['files'])|{'EVIDENCE-MANIFEST.json'}
  for member in members:
   assert member.isfile();data=archive.extractfile(member).read();expected=receipt['manifest_sha256']if member.name=='EVIDENCE-MANIFEST.json'else manifest['files'][member.name];assert hashlib.sha256(data).hexdigest()==expected
   path=Path(member.name);assert not path.is_absolute()and'..'not in path.parts
   dest=r/path
   if dest.exists():assert dest.read_bytes()==data,member.name
   else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 (r/'LOCAL-VERIFICATION.json').write_text(json.dumps({'status':'EVERY_ARCHIVE_MEMBER_VERIFIED_LOCALLY','members':len(members),'archive_sha256':receipt['archive_sha256'],'terminal_status':manifest['audit']['status']},indent=2)+'\n')
 (r/'.gitattributes').write_text('* -text\n')
 p=r/'.gitignore';prior=p.read_text()if p.exists()else'';p.write_text(prior+''.join(x+'\n'for x in['observer/','candidate/','unmodified-control/','tool/','__pycache__/','evidence.tar.gz','*resource-preflight*','*.records.bin']if x not in prior.splitlines()))
 print(name,len(members),'verified',flush=True)
