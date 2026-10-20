import hashlib,json,subprocess,tarfile
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';assert r.name=='breakthrough-prefix-tick-profile-20261020'and(r/'run.exit').read_text().strip()=='0'and not(r/'EVIDENCE-MANIFEST.json').exists();sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());result=json.loads((r/'RESULT.json').read_text());plan=json.loads((r/'TICK-CHOICES.json').read_text());assert len(result['cases'])==22 and plan['ticks_chosen']==2 and plan['sum_predicted_tick_savings']==7.75;assert sha(r/'SOURCE-FREEZE.json')==plan['source_profile_freeze_sha256']and sha(r/'RESULT.json')==plan['profile_result_sha256'];files={};streams={}
for case in result['cases']:
 directory=r/case['label'];assert sha(directory/'ops.bin')==case['raw_sha256']==case['expected_raw_sha256'];assert sha(directory/'TICKS.json')==plan['tick_table_hashes'][case['label']];assert len(json.loads((directory/'TICKS.json').read_text()))==550
 for p in directory.iterdir():
  if p.is_file():
   if p.name.endswith('ops.bin'):streams[p.relative_to(r).as_posix()]=sha(p)
   else:files[p.relative_to(r).as_posix()]=p
changed=[]
for p,h in f['source_files'].items():
 prior=subprocess.run(['git','-C',str(t),'show',f['base']+':'+p],capture_output=True)
 if prior.returncode or hashlib.sha256(prior.stdout).hexdigest()!=h:changed.append(p)
with tarfile.open(r/'changed-point-add-source.tar.gz','w:gz')as a:
 for p in sorted(changed):a.add(t/p,arcname=p,recursive=False)
for p in r.iterdir():
 if p.is_file()and'resource-preflight'not in p.name and p.name not in ['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']:files[p.name]=p
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p:sha(v)for p,v in files.items()},'streams_retained_on_server':streams,'changed_source_files':changed,'scope':'All22 raw streams byte-identical to frozen controls;550 unique whole-tick interfaces each. Structural two-tick choice7.75 predicted saving, not a complete build or score. No packet/census/nonce used. Prior failed cases unchanged and omitted from this profile rerun.'},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as a:
 for p,v in sorted(files.items()):a.add(v,arcname=p,recursive=False)
 a.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')},indent=2)+'\n');print(len(files)+1,'members sealed')
