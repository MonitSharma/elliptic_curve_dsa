import hashlib,json,re,subprocess,tarfile
from pathlib import Path
r=Path('/home/hclau/ecdsa_research/breakthrough-prefix-tick-isolated-20261020');t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert not(r/'EVIDENCE-MANIFEST.json').exists();f=json.loads((r/'SOURCE-FREEZE.json').read_text());result=json.loads((r/'RESULT.json').read_text());assert(r/'run.exit').read_text().strip()=='0'and all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert all(x['exit']=='101'for x in result['cases']);assert sum(result['native_test_counts'])==13
assert'rebind y42_bound: region of 489932 ops found 0 times'in(r/'generate-tick129.log').read_text();log=(r/'generate-tick130.log').read_text();assert 'left: 11446821'in log and'right: 11453250'in log and'square_finish.rs:13:1'in log
changed=[]
for p,h in f['source_files'].items():
 old=subprocess.run(['git','-C',str(t),'show',f['base']+':'+p],capture_output=True)
 if old.returncode or hashlib.sha256(old.stdout).hexdigest()!=h:changed.append(p)
with tarfile.open(r/'changed-point-add-source.tar.gz','w:gz')as archive:
 for p in sorted(changed):archive.add(t/p,arcname=p,recursive=False)
audit={'status':'BOTH_ISOLATED_CONSTRUCTIONS_STOP_AT_UNCHANGED_BOUND_PASSES','native_controls':13,'tick129':'Y42 region489932 not found','tick130':'square_finish original11453250 rejects11446821','scope':'No original table/assertion changed. Construction failures, no final gate, nonce or scored result.'};(r/'TERMINAL-AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');files={p.name:p for p in r.iterdir()if p.is_file()and'resource-preflight'not in p.name and p.name not in['EVIDENCE-MANIFEST.json','evidence.tar.gz','PACKAGE-RESULT.json']};streams={}
for mode in['tick129','tick130']:
 for p in(r/mode).iterdir():
  if p.is_file():
   if p.name.endswith('ops.bin'):streams[p.relative_to(r).as_posix()]=sha(p)
   else:files[p.relative_to(r).as_posix()]=p
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p:sha(v)for p,v in files.items()},'streams_retained_on_server':streams,'changed_source_files':changed,'audit':audit},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as archive:
 for p,v in sorted(files.items()):archive.add(v,arcname=p,recursive=False)
 archive.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'evidence.tar.gz'),'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json'),'members':len(files)+1},indent=2)+'\n');print(len(files)+1,'isolated members sealed')
