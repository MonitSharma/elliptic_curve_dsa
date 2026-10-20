"""Seal only terminal component/development evidence; no final gate verdict."""
import hashlib,json,os,shutil,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
ws=Path('/home/hclau/ecdsa_research');name=sys.argv[1]
allowed=['breakthrough-fold-square-20261020','breakthrough-fold-square-ripple-20261020','breakthrough-fold-square-short-20261020','breakthrough-hardcap-audit-20261020','breakthrough-phase-bridge-20261020','breakthrough-phase-fusion-20261020','breakthrough-phase-sites-20261020','breakthrough-hardcarry-20261020','breakthrough-paused-read-20261020','breakthrough-paused-pool-audit-20261020']
assert name in allowed;r=ws/name;assert not(r/'EVIDENCE-MANIFEST.json').exists()
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
site='phase-sites'in name;phase='phase-'in name and not site;v2=any(s in name for s in['phase-bridge','hardcap','hardcarry','paused-pool'])
t=r/('primitive'if phase else'observer');freeze='SOURCE_FREEZE-v2.json'if'phase-bridge'in name else'SOURCE_FREEZE.json'
assert(r/('run-v2.exit'if v2 else'run.exit')).read_text().strip()=='0'
f=json.loads((r/freeze).read_text());assert len(f['protected_files'])==17
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
if'paused-pool'in name:
 result=json.loads((r/'POOL-AUDIT.json').read_text());assert result['status']=='ORIGINAL_CONTROL_EXACT_SAME_CANDIDATE_POOL_FAILURE'
 assert [row['exit']for row in result['cases']]==[0,101]
 result['control_stream_sha256']=sha(t/'ops.bin');assert result['control_stream_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
elif'paused-read'in name:
 result=json.loads((r/'ADMISSION-RESULT.json').read_text());assert [row['exit']for row in result['cases']]==[0,101]
 assert result['cases'][0]['raw_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
 assert 'y42: the payload op changed the set of free wires'in result['cases'][1]['failure_tail']
 log=(r/'tests.log').read_text();assert all(f'test result: ok. {n} passed; 0 failed;'in log for n in[5,3,4,2])
elif phase:
 log=(r/('tests-v2.log'if v2 else'tests.log')).read_text();count=3 if v2 else 4
 assert f'test result: ok. {count} passed; 0 failed;'in log
 result={'status':'NATIVE_COMPONENT_PASS','tests':count,'no_point_add_integration':True}
elif site:
 result=json.loads((r/'PHASE-SITE-AUDIT.json').read_text());assert result['status']=='COMPLETE_RAW_CONTROL_BYTE_IDENTICAL'
elif'hardcap'in name:
 result=json.loads((r/'HARD-CAP-AUDIT.json').read_text());assert result['status']=='BOTH_COMPLETE_RAW_STREAMS_BYTE_IDENTICAL'
else:
 result=json.loads((r/'ADMISSION-RESULT.json').read_text());assert len(result['cases'])==2
 assert result['cases'][0]['raw_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
 assert all(row['exit']==0 for row in result['cases'])
 log=(r/('tests-v2.log'if'hardcarry'in name else'tests.log')).read_text()
 assert 'test result: ok. 2 passed; 0 failed;'in log
 if'hardcarry'in name:assert 'test result: ok. 5 passed; 0 failed;'in log and'test result: ok. 4 passed; 0 failed;'in log
 if'ripple'in name or'short'in name:
  assert(r/'replay.exit').read_text().strip()=='0'
  result['paired_raw_diagnostic']=json.loads((r/'PAIRED-DIAGNOSTIC.json').read_text())
added=r/'added-source';added.mkdir(exist_ok=False)
tracked=set(subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines())
for p in(t/'src/point_add').rglob('*'):
 if p.is_file()and p.relative_to(t).as_posix()not in tracked:
  dest=added/p.relative_to(t/'src/point_add');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
runtime={'sealed_at_utc':datetime.now(timezone.utc).isoformat(),'source_base':f['base'],'protected_files_checked':17,
 'source_freeze_sha256':sha(r/freeze),'result':result,'no_final_gate_nonce_or_scored_result':True,
 'streams_retained_on_server':{str(p):{'sha256':sha(p),'bytes':p.stat().st_size}for p in r.glob('cap*/ops.bin')},
 'native_binaries':{str(p):sha(p)for p in(t/'target/release/deps').glob('build_circuit-*')if p.is_file()and os.access(p,os.X_OK)}}
(r/'TERMINAL-AUDIT.json').write_text(json.dumps(runtime,indent=2)+'\n')
files=[]
for current,dirs,names in os.walk(r):
 dirs[:]=sorted(d for d in dirs if d not in['observer','primitive','target','__pycache__'])
 for n in sorted(names):
  p=Path(current)/n
  if n=='ops.bin'or n.endswith('.ops.bin')or'resource-preflight'in n:continue
  if n in['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','LOCAL-VERIFICATION.json']:continue
  files.append(p)
manifest={'files':{p.relative_to(r).as_posix():sha(p)for p in sorted(files)},'terminal_audit':runtime}
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as archive:
 for p in sorted(files)+[r/'EVIDENCE-MANIFEST.json']:archive.add(p,arcname=p.relative_to(r).as_posix())
receipt={'archive_sha256':sha(r/'evidence.tar.gz'),'archive_bytes':(r/'evidence.tar.gz').stat().st_size,'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')}
(r/'PACKAGE-RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
