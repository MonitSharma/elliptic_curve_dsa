import hashlib,json,re,subprocess,tarfile
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';assert r.name=='breakthrough-prefix27-generic-interaction-20261020'and(r/'run.exit').read_text().strip()=='0'and not(r/'EVIDENCE-MANIFEST.json').exists();sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());result=json.loads((r/'RESULT.json').read_text());assert result['compact_minus_control_diagnostic_weight']==51.75 and len(result['cases'])==2
for i,n in enumerate([2,1,1,4,1]):assert re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/f'tests-{i}.log').read_text())==[str(n)]
changed=[]
for p,h in f['source_files'].items():
 prior=subprocess.run(['git','-C',str(t),'show',f['base']+':'+p],capture_output=True)
 if prior.returncode or hashlib.sha256(prior.stdout).hexdigest()!=h:changed.append(p)
with tarfile.open(r/'changed-point-add-source.tar.gz','w:gz')as a:
 for p in sorted(changed):a.add(t/p,arcname=p,recursive=False)
(r/'STREAM-BINDINGS.json').write_text(json.dumps({'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'changed_files':changed,'changed_source_archive_sha256':sha(r/'changed-point-add-source.tar.gz'),'streams':{x['label']:{'sha256':sha(r/x['label']/'ops.bin'),'operations':x['operations'],'diagnostic_weight':x['diagnostic_weight']}for x in result['cases']},'scope':'Generic transform on declared raw streams, no source-bound certificate passes. Control761696.25 and compact761748.0, unchanged+51.75. These are incomplete-pipeline diagnostic weights, never benchmark counts; the public parent includes additional bound exact passes.'},indent=2)+'\n')
files=[p for p in r.iterdir()if p.is_file()and'resource-preflight'not in p.name and p.name not in ['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']]
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p.name:sha(p)for p in files},'scope':'Completed finite generic interaction negative, no scored result or gate/nonce.'},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as a:
 for p in files+[r/'EVIDENCE-MANIFEST.json']:a.add(p,arcname=p.name,recursive=False)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')},indent=2)+'\n');print(len(files)+1,'members sealed')
