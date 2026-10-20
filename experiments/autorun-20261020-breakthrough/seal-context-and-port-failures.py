import hashlib,json,re,subprocess,sys,tarfile
from pathlib import Path
r=Path('/home/hclau/ecdsa_research')/sys.argv[1];sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();allowed=['breakthrough-context-lease-20261020','breakthrough-exact-native-ports-20261020','breakthrough-exact-native-ports-v2-20261020'];assert r.name in allowed and not(r/'EVIDENCE-MANIFEST.json').exists();files={};streams={};changed=[]
if r.name==allowed[0]:
 f=json.loads((r/'SOURCE-FREEZE.json').read_text());a=json.loads((r/'RESULT.json').read_text());assert(r/'run.exit').read_text().strip()=='0'and a['leases']==213 and a['native_controls']==7 and a['diagnostic_saving']==213.0;assert re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/'tests.log').read_text())==['7'];assert all(sha(r/'tool'/p)==h for p,h in f['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items());assert sha(r/'context16.ops.bin')==a['output_stream_sha256'];streams['context16.ops.bin']=sha(r/'context16.ops.bin')
 for p in f['tool_source_files']:files['tool-source/'+p]=r/'tool'/p
 audit={'status':'EXACT_EARLIER_CONTEXT_PROOF_COMPONENT213_LEASES','native_controls':7,'leases':213,'proposed':1877,'rejected':1664,'diagnostic_saving':213.0,'max_donor':1479,'scope':'Exact value/phase proof component, not a benchmark. New self-contained frozen integration and own final gate/nonce/benchmark remain mandatory.'}
else:
 assert(r/'run.exit').read_text().strip()=='1'
 if r.name==allowed[1]:
  old=r.parent/'breakthrough-public322-square-final-20261020';f=json.loads((old/'SOURCE-FREEZE.json').read_text());assert all(sha(r/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert 'AssertionError'in(r/'prepare.log').read_text();(r/'BASELINE-SOURCE-VERIFICATION.json').write_text(json.dumps({'parent_freeze_sha256':sha(old/'SOURCE-FREEZE.json'),'source_files':f['source_files'],'protected_files':f['protected_files'],'status':'All parent bytes unchanged; empty hunk parser assertion failed before patch apply.'},indent=2)+'\n');audit={'status':'PREPARATION_EMPTY_HUNK_PARSER_FAILURE_BEFORE_SOURCE_CHANGE','native_controls':0,'scope':'Not arithmetic/circuit/final-gate failure. Original source/worktree/logs retained.'}
 else:
  f=json.loads((r/'SOURCE-FREEZE.json').read_text());t=r/'observer';assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert 'cannot find value `bit0` in this scope'in(r/'tests-0.log').read_text();assert not(r/'tests-0.log').read_text().count('running 1 test')
  for p,h in f['source_files'].items():
   old=subprocess.run(['git','-C',str(t),'show',f['base']+':'+p],capture_output=True)
   if old.returncode or hashlib.sha256(old.stdout).hexdigest()!=h:changed.append(p)
  with tarfile.open(r/'changed-point-add-source.tar.gz','w:gz')as archive:
   for p in sorted(changed):archive.add(t/p,arcname=p,recursive=False)
  audit={'status':'RESEARCH_SELECTOR_BIT0_SCOPE_COMPILE_FAILURE_BEFORE_TESTS','native_controls':0,'scope':'Full frozen source/patch/compiler failure retained. No native test/arithmetic/gate/nonce verdict. Corrected selector repair proceeds separately.'}
(r/'TERMINAL-AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
for p in r.iterdir():
 if p.is_file()and'resource-preflight'not in p.name and p.name not in['EVIDENCE-MANIFEST.json','evidence.tar.gz','PACKAGE-RESULT.json']and not p.name.endswith('ops.bin'):files[p.name]=p
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p:sha(v)for p,v in files.items()},'streams_retained_on_server':streams,'changed_source_files':changed,'audit':audit},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as archive:
 for p,v in sorted(files.items()):archive.add(v,arcname=p,recursive=False)
 archive.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')},indent=2)+'\n');print(r.name,len(files)+1,'members sealed')
