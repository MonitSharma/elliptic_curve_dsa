"""Terminal evidence only. Never turn a development outcome into a final gate."""
import hashlib,json,os,shutil,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
ws=Path('/home/hclau/ecdsa_research');name=sys.argv[1]
config={'breakthrough-sparse-polynomial-20261020': ('tool', 'SOURCE_FREEZE.json', 'run.exit', 'tests.log', [3], 'AUDIT-RESULT.json'), 'breakthrough-t0-shared-product-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', 'tests.log', [1, 1, 1, 3, 1, 4, 3, 2, 3, 1, 1], 'ADMISSION-RESULT.json'), 'breakthrough-fin1-loan-native-20261020': ('primitive', 'SOURCE_FREEZE.json', 'run.exit', 'tests.log', [1, 2, 1], None), 'breakthrough-fin1-fold-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', 'tests.log', [1, 1, 1, 1, 3, 1, 4, 3, 2, 3, 1, 1], 'ADMISSION-RESULT.json'), 'breakthrough-reverse-plan7-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', 'tests.log', [1, 1, 1, 1, 1, 3, 1, 4, 3, 3, 3, 1, 1], 'ADMISSION-RESULT.json'), 'breakthrough-reverse-budget-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', 'tests.log', [1, 1, 1, 1, 1, 3, 1, 4, 3, 2, 3, 1, 1], 'ADMISSION-RESULT.json'), 'breakthrough-generic-postpass-20261020': ('observer', 'SOURCE_FREEZE.json', 'run-v2.exit', None, [], 'AUDIT-RESULT-v2.json'), 'breakthrough-truth14-20261020': ('tool', 'SOURCE_FREEZE.json', 'run.exit', 'tests.log', [10], 'AUDIT-RESULT.json'), 'breakthrough-replay-layout-audit-20261020': ('observer', 'SOURCE_FREEZE.json', 'run.exit', None, [], 'LAYOUT-AUDIT.json')}
assert name in config;r=ws/name;assert not(r/'EVIDENCE-MANIFEST.json').exists();sub,freeze,exitfile,log,counts,resultfile=config[name];t=r/sub
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert(r/exitfile).read_text().strip()=='0';f=json.loads((r/freeze).read_text());assert len(f['protected_files'])==17
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
if log:
 import re
 text=(r/log).read_text();actual=[int(x)for x in re.findall(r'test result: ok\. (\d+) passed; 0 failed;',text)];assert actual==counts,(actual,counts)
result=json.loads((r/resultfile).read_text())if resultfile else{'status':'NATIVE_COMPONENT_PASS','tests':sum(counts),'scope':'Component only, no point-add resource result or novelty claim.'}
if resultfile=='ADMISSION-RESULT.json':
 cases=result['cases'];assert len(cases)==(2 if name=='breakthrough-t0-shared-product-20261020'else 3)
 assert cases[0]['raw_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
 expected=[0,0,101]if name in['breakthrough-fin1-fold-20261020','breakthrough-reverse-plan7-20261020']else[0]*len(cases)
 assert [c['exit']for c in cases]==expected
 if 101 in expected:result['preserved_negative_case']='cap1232 generation failed; successful controls are raw only'
if resultfile=='AUDIT-RESULT-v2.json':
 assert len(result['cases'])==3 and all(c['exit']==0 for c in result['cases'])
 assert result['cases'][0]['stream_sha256']=='125deb3a03b460ec991df012e6aa8e6a6b67fc96ffc525a165b5ca3e67282501'
if resultfile=='AUDIT-RESULT.json':assert result['exit']==0
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
 'streams_retained_on_server':streams,'native_binaries':{str(p):sha(p)for p in(t/'target/release/deps').glob('build_circuit-*')if p.is_file()and os.access(p,os.X_OK)},'no_final_gate_nonce_or_scored_result':True,'scope_correction':'Direct profile constants stay fixed, but tighter global caps change derived replay boundaries. Component equivalence does not establish complete point-add equivalence; exact streams and differing replay metadata preserved in breakthrough-replay-layout-audit-20261020.'}
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
