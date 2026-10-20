import hashlib,json,re,sys,tarfile
from pathlib import Path
r=Path('/home/hclau/ecdsa_research')/sys.argv[1];assert r.name in ['breakthrough-public322-capacity-grid-20261020','breakthrough-prefix-fresh-aux-20261020'];assert(r/'run.exit').read_text().strip()=='0'and not(r/'EVIDENCE-MANIFEST.json').exists();sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();files={}
if 'capacity-grid'in r.name:
 f=json.loads((r/'SOURCE-FREEZE.json').read_text());t=r/'observer';assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
 for i,n in enumerate([2,1,1,4,1]):assert re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/f'tests-{i}.log').read_text())==[str(n)]
 result=json.loads((r/'RESULT.json').read_text());assert len(result['cases'])==8 and all(row['exit']==0 and row['raw_sha256']=='62c25f615411b8cbf6de5e51442a9e1da9e5ec56f887b5fd465e5b1cff61d5f0'for row in result['cases'])
 with tarfile.open(r/'point-add-source.tar.gz','w:gz')as a:
  for p in sorted(f['source_files']):a.add(t/p,arcname=p,recursive=False)
 for d in r.glob('hard*-square*'):
  for p in d.iterdir():
   if p.is_file()and p.name!='ops.bin':files[p.relative_to(r).as_posix()]=p
else:
 d=json.loads((r/'DECLARATION.json').read_text());assert all(sha(r/p)==h for p,h in d['source_hashes'].items());result=json.loads((r/'RESULT.json').read_text());assert len(result['cases'])==result['declared_auxiliaries']==88 and result['survivor']is None and all(x['interfaces_tested']==651 and not x['survivor']for x in result['cases'])
for p in r.iterdir():
 if p.is_file()and'resource-preflight'not in p.name and p.name not in ['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']:files[p.name]=p
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p:sha(v)for p,v in files.items()},'scope':'Completed fixed research, no benchmark or public resource result. Raw capacity grid byte-exact negative; auxiliary filter excludes only its declared function language. No unrestricted circuit lower bound.'},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as a:
 for p,v in sorted(files.items()):a.add(v,arcname=p,recursive=False)
 a.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')},indent=2)+'\n');print(r.name,len(files)+1)
