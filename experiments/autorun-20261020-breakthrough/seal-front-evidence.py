import hashlib,json,re,subprocess,sys,tarfile
from pathlib import Path
r=Path('/home/hclau/ecdsa_research')/sys.argv[1];allowed=['breakthrough-context16384-lease-20261020','breakthrough-exact-native-ports-v3-20261020','breakthrough-exact-ports-development-20261020','breakthrough-native-both-finished-20261020','breakthrough-stackv3-width-20261020','breakthrough-stackv3-width-lean128-20261020','breakthrough-stackv3-width-loan128-20261020','breakthrough-stackv3-width-stats-20261020'];assert r.name in allowed and not(r/'EVIDENCE-MANIFEST.json').exists();sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();marker='resumed.exit'if r.name==allowed[1]else'run.exit';assert(r/marker).read_text().strip()=='0';files={};streams={};source_count=0;test_count=0;changed=[]
if(r/'SOURCE-FREEZE.json').exists():
 f=json.loads((r/'SOURCE-FREEZE.json').read_text())
 if 'tool_source_files'in f:
  assert all(sha(r/'tool'/p)==h for p,h in f['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items())
  for p in f['tool_source_files']:files['tool-source/'+p]=r/'tool'/p
  if r.name==allowed[0]:assert json.loads((r/'RESULT.json').read_text())['leases']==345 and re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/'tests.log').read_text())==['7'];test_count=7
 else:
  t=r/('candidate'if r.name==allowed[3]else'observer');assert len(f['protected_files'])==17 and all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());source_count=len(f['source_files'])
  for p,h in f['source_files'].items():
   before=subprocess.run(['git','-C',str(t),'show',f['base']+':'+p],capture_output=True)
   if before.returncode or hashlib.sha256(before.stdout).hexdigest()!=h:changed.append(p)
  with tarfile.open(r/'changed-point-add-source.tar.gz','w:gz')as archive:
   for p in sorted(changed):archive.add(t/p,arcname=p,recursive=False)
  if r.name==allowed[1]:
   assert(r/'run.exit').read_text().strip()=='1'and 'Independent phase-pebble cap: NotPresent'in(r/'tests-12.log').read_text();expected=[1,2,1,1,1,1,1,1,3,1,4,3,2,3,1,1]
   for i,n in enumerate(expected):assert re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/f'tests-env-{i}.log').read_text())==[str(n)]
   assert 'checked=6416896 phase_fault_batches=55256'in(r/'tests-env-0.log').read_text();test_count=27
  if r.name==allowed[3]:assert json.loads((r/'FINISHED-RESULT.json').read_text())['native_tests']==27;test_count=27
if r.name==allowed[2]:
 d=json.loads((r/'DIAGNOSTIC.json').read_text());assert d['batches']==512 and all(x['dirty_shots']==0 and x['value_shots']==18 for x in d['summaries'].values());assert len(d['comparisons']['both']['different_target_lanes'])==7 and d['comparisons']['both']['target_differences_confined_to_both_value_failing'];assert all(not x['new_value_failing_shots']and not x['different_other_lanes']for x in d['comparisons'].values())
if r.name in allowed[4:7]:
 a=json.loads((r/'RESULT.json').read_text());rows=a['cases'];assert rows[0]['mode']=='public'and rows[0]['stream_sha256']=='714c4e4c1c2c5c59544dcc3ade28587663b616d46a168b0fcd22a06c29c0916f';assert all(x['exit']==101 for x in rows if x['mode'].startswith(('cap1233','cap1232')))
for path in list(r.glob('*.ops.bin'))+list(r.glob('*/ops.bin'))+list(r.glob('*/raw.ops.bin')):streams[path.relative_to(r).as_posix()]=sha(path)
audit={'status':'COMPLETED_RESEARCH_NATIVE_SOURCE_DIAGNOSTIC_NOT_SCORED','source_files_checked':source_count,'native_controls':test_count,'scope':'All source/protected/tool bytes and original terminal logs preserved. Native/static/development counts are not benchmark records. Original construction/parser/compile/environment/final-gate verdicts stand; no old guard is weakened.'};(r/'TERMINAL-AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
for p in r.iterdir():
 if p.is_file()and'resource-preflight'not in p.name and not p.name.endswith('ops.bin')and p.name not in['EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','evidence.tar.gz']:files[p.name]=p
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{n:sha(p)for n,p in files.items()},'streams_retained_on_server':streams,'changed_source_files':changed,'audit':audit},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as archive:
 for n,p in sorted(files.items()):archive.add(p,arcname=n,recursive=False)
 archive.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')},indent=2)+'\n');print(r.name,len(files)+1,'members sealed',flush=True)
