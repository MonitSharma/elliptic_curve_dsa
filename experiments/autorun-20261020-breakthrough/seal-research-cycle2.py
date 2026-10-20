import hashlib,json,re,subprocess,sys,tarfile
from pathlib import Path
names=['breakthrough-stackv3-width-plan7-range-20261020','breakthrough-stackv3-width-plan7-both-20261020','breakthrough-stackv3-plan7-both-stats-20261020','breakthrough-stackv3-plan7-generic-20261020','breakthrough-stackv3-plan7-generic-v2-20261020','breakthrough-stackv3-plan7-zero-donors-20261020','breakthrough-stackv3-plan7-context-clean-20261020','breakthrough-stackv3-plan7-development-20261020','breakthrough-classical-width-audit-20261020','breakthrough-classical-width-audit-v2-20261020','breakthrough-public-e3-context-clean-20261020','breakthrough-public-e3-cache-finished-20261020','breakthrough-public-e3-cache-finished-v2-20261020','breakthrough-public-e3-cache-development-20261020','breakthrough-public-e3-cache-development-v2-20261020','breakthrough-live-products-20261020','breakthrough-live-products-v2-20261020','breakthrough-live-products-absorption-20261020']
ws=Path('/home/hclau/ecdsa_research');r=ws/sys.argv[1];assert r.name in names and not(r/'EVIDENCE-MANIFEST.json').exists();sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();marker='resumed.exit'if r.name=='breakthrough-public-e3-cache-finished-v2-20261020'else'run.exit';assert(r/marker).exists();terminal=(r/marker).read_text().strip();assert terminal in['0','1'];files={};source_count=0;changed=[];streams={};f=None
if(r/'SOURCE-FREEZE.json').exists():
 f=json.loads((r/'SOURCE-FREEZE.json').read_text())
 if 'tool_source_files'in f:
  assert all(sha(r/'tool'/p)==h for p,h in f['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items())
  for p in f['tool_source_files']:files['tool-source/'+p]=r/'tool'/p
 elif 'source_files'in f:
  t=r/('candidate'if(r/'candidate').is_dir()else'observer');assert len(f['protected_files'])==17 and all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());source_count=len(f['source_files'])
  for p,h in f['source_files'].items():
   prior=subprocess.run(['git','-C',str(t),'show',f['base']+':'+p],capture_output=True)
   if prior.returncode or hashlib.sha256(prior.stdout).hexdigest()!=h:changed.append(p)
  with tarfile.open(r/'changed-point-add-source.tar.gz','w:gz')as a:
   for p in sorted(changed):a.add(t/p,arcname=p,recursive=False)
else:
 for p in(r/'tool').glob('*'):
  if p.is_file():files['partial-unfrozen-tool-source/'+p.name]=p
if(r/'UNMODIFIED-CONTROL-FREEZE.json').exists():
 cf=json.loads((r/'UNMODIFIED-CONTROL-FREEZE.json').read_text());ct=r/'unmodified-control';assert all(sha(ct/p)==h for p,h in{**cf['source_files'],**cf['protected_files']}.items());assert json.loads((r/'TEST-BASELINE-AUDIT.json').read_text())['status']=='TWO_UNCHANGED_PARENT_TEST_FAILURES_REPRODUCED_BYTE_IDENTICALLY'
for p in list(r.glob('*.ops.bin'))+list(r.glob('*/ops.bin')):streams[p.relative_to(r).as_posix()]=sha(p)
counts={p.name:re.findall(r'test result: (ok|FAILED)\. (\d+) passed; (\d+) failed;',p.read_text(errors='replace'))for p in r.glob('*tests*.log')}
audit={'status':'COMPLETED_RESEARCH_NOT_SCORED'if terminal=='0'else'FAILED_RESEARCH_OR_PREFLIGHT_OR_FIXTURE_PRESERVED_NOT_SCORED','terminal_marker':marker,'terminal_exit':terminal,'original_run_exit':(r/'run.exit').read_text().strip(),'source_files_checked':source_count,'source_freeze_present':f is not None,'test_log_verdicts':counts,'scope':'Preserve every original failure, source/protected/tool binding, control audit and stream hash. Raw/static/native/development measurements are not scored results. No final gate/nonce verdict is changed.'};(r/'TERMINAL-AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
for p in r.iterdir():
 if p.is_file()and'resource-preflight'not in p.name and not p.name.endswith('ops.bin')and p.name not in['EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','evidence.tar.gz']:files[p.name]=p
manifest={'files':{n:sha(p)for n,p in files.items()},'streams_retained_on_server':streams,'changed_source_files':changed,'audit':audit};(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as a:
 for n,p in sorted(files.items()):a.add(p,arcname=n,recursive=False)
 a.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')},indent=2)+'\n');print(r.name,len(files)+1,'sealed',flush=True)
