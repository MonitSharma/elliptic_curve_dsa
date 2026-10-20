"""Terminal evidence only. Never turn a development outcome into a final gate."""
import hashlib,json,os,shutil,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
ws=Path('/home/hclau/ecdsa_research');name=sys.argv[1]
config={
 'breakthrough-phase-pebble-boundary-20261020':('observer','SOURCE_FREEZE.json','run-v2.exit','tests.log',[3,1,4,3],'ADMISSION-RESULT.json'),
 'breakthrough-boundary-storage-audit-20261020':('observer','SOURCE_FREEZE.json','run.exit',None,[],'BOUNDARY-STORAGE-AUDIT.json'),
 'breakthrough-phase-pebble-plan7-20261020':('observer','SOURCE_FREEZE.json','run.exit','tests.log',[3,1,4,3,2],'ADMISSION-RESULT.json'),
 'breakthrough-phase-plan-native-20261020':('primitive','SOURCE_FREEZE-v4.json','run-v4.exit','tests-v4.log',[3],None)}
assert name in config;r=ws/name;assert not(r/'EVIDENCE-MANIFEST.json').exists();sub,freeze,exitfile,log,counts,resultfile=config[name];t=r/sub
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert(r/exitfile).read_text().strip()=='0';f=json.loads((r/freeze).read_text());assert len(f['protected_files'])==17
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
if log:
 text=(r/log).read_text();assert all(f'test result: ok. {n} passed; 0 failed;'in text for n in counts)
result=json.loads((r/resultfile).read_text())if resultfile else{'status':'NATIVE_COMPONENT_PASS','tests':sum(counts),'scope':'Component only, no point-add resource result or novelty claim.'}
if resultfile=='ADMISSION-RESULT.json':
 assert len(result['cases'])==2 and [row['exit']for row in result['cases']]==([0,101]if name=='breakthrough-phase-pebble-boundary-20261020'else[0,0])
 assert result['cases'][0]['raw_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
if resultfile=='BOUNDARY-STORAGE-AUDIT.json':
 assert result['status']=='CONTROL_EXACT_SAME_FAILED_CANDIDATE_DIAGNOSED';assert result['cases'][0]['raw_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b';assert result['cases'][1]['debug_prefix_incomplete']
if resultfile=='FOLD-STORAGE-AUDIT.json':
 assert result['status']=='EXACT_COMPLETE_CONTROL_AND_FAILED_DEBUG_PREFIX';assert result['cases'][1]['failed_debug_prefix_sha256']=='66ba9d6c055d7d8bbe9260c36f754359ca4df9bea1fe24a689dbc197588288c2'
added=r/'added-source';added.mkdir(exist_ok=False);tracked=set(subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines())
for p in(t/'src/point_add').rglob('*'):
 if p.is_file()and p.relative_to(t).as_posix()not in tracked:
  dest=added/p.relative_to(t/'src/point_add');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
streams={str(p):{'sha256':sha(p),'bytes':p.stat().st_size,'complete':True}for p in r.glob('cap*/ops.bin')}
if(t/'failure-prefix.ops.bin').exists():streams[str(t/'failure-prefix.ops.bin')]={'sha256':sha(t/'failure-prefix.ops.bin'),'bytes':(t/'failure-prefix.ops.bin').stat().st_size,'complete':False,'scope':'Failed debug prefix, never a scored circuit.'}
runtime={'sealed_at_utc':datetime.now(timezone.utc).isoformat(),'base':f['base'],'protected_files_checked':17,'source_freeze_sha256':sha(r/freeze),'result':result,
 'streams_retained_on_server':streams,'native_binaries':{str(p):sha(p)for p in(t/'target/release/deps').glob('build_circuit-*')if p.is_file()and os.access(p,os.X_OK)},'no_final_gate_nonce_or_scored_result':True}
(r/'TERMINAL-AUDIT.json').write_text(json.dumps(runtime,indent=2)+'\n');files=[]
for current,dirs,names in os.walk(r):
 dirs[:]=sorted(d for d in dirs if d not in['observer','primitive','target','__pycache__'])
 for n in sorted(names):
  p=Path(current)/n
  if n=='native-test-binary'or n=='ops.bin'or n.endswith('.ops.bin')or'resource-preflight'in n or n in['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','LOCAL-VERIFICATION.json']:continue
  files.append(p)
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p.relative_to(r).as_posix():sha(p)for p in files},'terminal_audit':runtime},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as archive:
 for p in sorted(files)+[r/'EVIDENCE-MANIFEST.json']:archive.add(p,arcname=p.relative_to(r).as_posix())
receipt={'archive_sha256':sha(r/'evidence.tar.gz'),'archive_bytes':(r/'evidence.tar.gz').stat().st_size,'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')}
(r/'PACKAGE-RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
