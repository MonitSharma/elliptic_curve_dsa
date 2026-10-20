"""Terminal evidence only. Never turn a development outcome into a final gate."""
import hashlib,json,os,shutil,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
ws=Path('/home/hclau/ecdsa_research');name=sys.argv[1]
config={'breakthrough-certified-prefix-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', None, [], 'AUDIT-RESULT.json'), 'breakthrough-public-schedule-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', None, [], 'ADMISSION-RESULT.json'), 'breakthrough-wide-generic-20261020': ('tool', 'SOURCE_FREEZE.json', 'run.exit', None, [], 'AUDIT-RESULT.json'), 'breakthrough-wide-square-budget-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', None, [], 'ADMISSION-RESULT.json'), 'breakthrough-wide-uniform-compare-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', None, [], 'ADMISSION-RESULT.json'), 'breakthrough-spacious-budget-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', None, [], 'ADMISSION-RESULT.json'), 'breakthrough-primed-pool-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', 'tests.log', [2], 'ADMISSION-RESULT.json'), 'breakthrough-wide-stronger-compare-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', None, [], 'ADMISSION-RESULT.json'), 'breakthrough-wide-loan-policy-20261020': ('observer', 'SOURCE_FREEZE.json', 'run-v2.exit', 'tests-v2.log', [1, 1, 1, 1, 1, 1, 3, 1, 4, 3, 2, 3, 1, 1], 'ADMISSION-RESULT.json'), 'breakthrough-local-budget-20261020': ('observer', 'SOURCE_FREEZE.json', 'run-v2.exit', 'tests-v2.log', [1, 1, 1, 1, 1, 3, 1, 4, 3, 2, 3, 1, 1], 'ADMISSION-RESULT.json'), 'breakthrough-local-budget-runtime-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', 'tests.log', [1, 1, 1, 1, 1, 1, 3, 1, 4, 3, 2, 3, 1, 1], 'ADMISSION-RESULT.json'), 'breakthrough-wide-budget-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', None, [], 'ADMISSION-RESULT.json'), 'breakthrough-sparse-polynomial-20261020': ('tool', 'SOURCE_FREEZE.json', 'run.exit', 'tests.log', [3], 'AUDIT-RESULT.json'), 'breakthrough-t0-shared-product-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', 'tests.log', [1, 1, 1, 3, 1, 4, 3, 2, 3, 1, 1], 'ADMISSION-RESULT.json'), 'breakthrough-fin1-loan-native-20261020': ('primitive', 'SOURCE_FREEZE.json', 'run.exit', 'tests.log', [1, 2, 1], None), 'breakthrough-fin1-fold-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', 'tests.log', [1, 1, 1, 1, 3, 1, 4, 3, 2, 3, 1, 1], 'ADMISSION-RESULT.json'), 'breakthrough-reverse-plan7-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', 'tests.log', [1, 1, 1, 1, 1, 3, 1, 4, 3, 3, 3, 1, 1], 'ADMISSION-RESULT.json'), 'breakthrough-reverse-budget-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', 'tests.log', [1, 1, 1, 1, 1, 3, 1, 4, 3, 2, 3, 1, 1], 'ADMISSION-RESULT.json'), 'breakthrough-generic-postpass-20261020': ('observer', 'SOURCE_FREEZE.json', 'run-v2.exit', None, [], 'AUDIT-RESULT-v2.json'), 'breakthrough-truth14-20261020': ('tool', 'SOURCE_FREEZE.json', 'run.exit', 'tests.log', [10], 'AUDIT-RESULT.json'), 'breakthrough-replay-layout-audit-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', None, [], 'LAYOUT-AUDIT.json')}
assert name in config;r=ws/name;assert not(r/'EVIDENCE-MANIFEST.json').exists();sub,freeze,exitfile,log,counts,resultfile=config[name];t=r/sub
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert(r/exitfile).read_text().strip()=='0';f=json.loads((r/freeze).read_text());assert len(f['protected_files'])==17
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
if log:
 import re
 text=(r/log).read_text();actual=[int(x)for x in re.findall(r'test result: ok\. (\d+) passed; 0 failed;',text)];assert actual==counts,(actual,counts)
result=json.loads((r/resultfile).read_text())if resultfile else{'status':'NATIVE_COMPONENT_PASS','tests':sum(counts),'scope':'Component only, no point-add resource result or novelty claim.'}
if resultfile=='ADMISSION-RESULT.json':
 cases=result['cases']
 special={'breakthrough-public-schedule-20261020':[0,0,0],'breakthrough-wide-square-budget-20261020':[0,0,0],'breakthrough-wide-uniform-compare-20261020':[0,0,101,101,101,101],'breakthrough-spacious-budget-20261020':[0,101,101,101,101,101,101,101,101],'breakthrough-primed-pool-20261020':[0,101,101,101,101,0,0,0,0]}
 if name in special:
  assert[c['exit']for c in cases]==special[name]
  assert cases[0]['raw_sha256']=='7fe2bb94f6b68965b87f7af4debd245d53c4b84df91ee0260e032499d49c14df'
 elif name=='breakthrough-wide-stronger-compare-20261020':
  assert len(cases)==2 and[c['mode']for c in cases]==[0,2]
  assert cases[0]['raw_sha256']=='7fe2bb94f6b68965b87f7af4debd245d53c4b84df91ee0260e032499d49c14df' and cases[1]['raw_sha256']=='f97bc5a1be3546e5d123a9007344936fd6a0e769725a941619e1441d0099887c'
 else:
  assert len(cases)==len(f['caps'])
  assert cases[0]['raw_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
 expected=special.get(name,{'breakthrough-fin1-fold-20261020':[0,0,101],'breakthrough-reverse-plan7-20261020':[0,0,101],'breakthrough-local-budget-20261020':[0,101,101],'breakthrough-wide-budget-20261020':[0,0,0,0,0,101,101,101],'breakthrough-wide-loan-policy-20261020':[0,0,0,0,101,101,101]}.get(name,[0]*len(cases)))
 assert [c['exit']for c in cases]==expected
 if 101 in expected:result['preserved_negative_cases']=[c['cap']for c in cases if c['exit']!=0]
if resultfile=='AUDIT-RESULT-v2.json':
 assert len(result['cases'])==3 and all(c['exit']==0 for c in result['cases'])
 assert result['cases'][0]['stream_sha256']=='125deb3a03b460ec991df012e6aa8e6a6b67fc96ffc525a165b5ca3e67282501'
if resultfile=='AUDIT-RESULT.json':
 if name=='breakthrough-certified-prefix-20261020':
  assert len(result['cases'])==2 and all(c['exit']==0 for c in result['cases'])
  assert result['cases'][0]['stream_sha256']=='40a55e81af487e4f830eca1827d9904f60ed215b33d3bee9f12a801a46c4479c'
  assert result['cases'][1]['stream_sha256']=='85958b9f90cc93c7bba94d158cba2b4dde890bf9f4231cd70dc5b4fd9f1218b2'
 elif name=='breakthrough-wide-generic-20261020':
  assert result['status']=='COMPLETE_GENERIC_WIDE_AUDIT_NOT_SCORED' and[c['cap']for c in result['cases']]==[1234,1256,1264]
  assert result['cases'][0]['output_records']=={'operations':11268527,'record_sha256':'63eb09e3df3ecc6dc84330089f7100c369a21d8b50380bf792ab253debdf35c0'}
 else:assert result['exit']==0
if resultfile=='LAYOUT-AUDIT.json':
 assert len(result['cases'])==3 and all(c['exit']==0 for c in result['cases'])
 assert all(not c['identical_site_multiset']for c in result['comparisons'])
added=r/'added-source';added.mkdir(exist_ok=False);tracked=set(subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines())
for p in(t/'src/point_add').rglob('*'):
 if p.is_file()and p.relative_to(t).as_posix()not in tracked:
  dest=added/p.relative_to(t/'src/point_add');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
streams={str(p):{'sha256':sha(p),'bytes':p.stat().st_size,'complete':True}for p in list(r.glob('*/ops.bin'))+list(r.glob('*.ops.bin'))}
if(t/'failure-prefix.ops.bin').exists():streams[str(t/'failure-prefix.ops.bin')]={'sha256':sha(t/'failure-prefix.ops.bin'),'bytes':(t/'failure-prefix.ops.bin').stat().st_size,'complete':False,'scope':'Failed debug prefix, never a scored circuit.'}
runtime={'sealed_at_utc':datetime.now(timezone.utc).isoformat(),'base':f['base'],'protected_files_checked':17,'source_freeze_sha256':sha(r/freeze),'result':result,
 'streams_retained_on_server':streams,'native_binaries':{str(p):sha(p)for p in(t/'target/release/deps').glob('build_circuit-*')if p.is_file()and os.access(p,os.X_OK)},'no_final_gate_nonce_or_scored_result':True,'scope_correction':'Arithmetic scope is defined by the frozen source and experiment report. Budget changes can move derived predicates; stronger-comparison experiments explicitly increase precision. Component equivalence does not establish complete point-add equivalence.'}
(r/'TERMINAL-AUDIT.json').write_text(json.dumps(runtime,indent=2)+'\n');files=[]
for current,dirs,names in os.walk(r):
 dirs[:]=sorted(d for d in dirs if d not in['observer','primitive','tool','target','__pycache__'])
 for n in sorted(names):
  p=Path(current)/n
  if n=='ops.bin'or n.endswith('.ops.bin')or'resource-preflight'in n or n in['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','LOCAL-VERIFICATION.json']:continue
  files.append(p)
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p.relative_to(r).as_posix():sha(p)for p in files},'terminal_audit':runtime},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as archive:
 for p in sorted(files)+[r/'EVIDENCE-MANIFEST.json']:archive.add(p,arcname=p.relative_to(r).as_posix())
receipt={'archive_sha256':sha(r/'evidence.tar.gz'),'archive_bytes':(r/'evidence.tar.gz').stat().st_size,'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')}
(r/'PACKAGE-RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
