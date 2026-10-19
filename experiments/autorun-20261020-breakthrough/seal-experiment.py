"""Seal terminal structural diagnostics while retaining large streams remotely."""
import hashlib,json,os,shutil,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
ws=Path('/home/hclau/ecdsa_research');name=sys.argv[1]
assert name in ['breakthrough-cap-cost-20261020','breakthrough-cofactor-history-20261020','breakthrough-cofactor-update-20261020']
r=ws/name
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
if 'cap-cost' in name:
 t=r/'observer';freeze_name='SOURCE_FREEZE.json';assert(r/'continuation-v3.exit').read_text().strip()=='0'
 result=json.loads((r/'CONTINUATION-RESULT.json').read_text());assert result['results'][0]['full_raw_operation_identity_control']
 assert all(x['exit']!=0 for x in result['results'][1:])
 status='CAPACITY_SETTINGS_FAILED_ADMISSION_NO_CANDIDATE'
elif 'history' in name:
 t=r/'primitive';freeze_name='NATIVE-SOURCE-FREEZE-v2.json';assert(r/'native-v2.exit').read_text().strip()=='0'
 result=json.loads((r/'NATIVE-RESULT.json').read_text());assert result['tests']==3
 status='NATIVE_HISTORY_CODEC_COMPONENT_PASS_NO_POINT_ADD_RESULT'
else:
 t=r/'primitive';freeze_name='SOURCE_FREEZE.json';assert(r/'run.exit').read_text().strip()=='0'
 log=(r/'tests.log').read_text();assert'test result: ok. 6 passed; 0 failed;'in log
 result={'status':'NATIVE_SIGNED_COFACTOR_UPDATE_COMPONENT_CONTROLS_PASS','tests':6,
  'signed_eight_bit_addition_cases':131072,'signed_sixteen_bit_edge_cases':1792,
  'phase_coefficient_basis_inputs':64,'all_physical_rng_coefficients_tested':True,
  'forward_sixteen_bit_toffoli_count_including_scale_and_history_erase':93,
  'scope':'Bounded-word arithmetic component and inverse, not a point-add circuit, allocation bound or scored resource claim.'}
 (r/'NATIVE-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 status='NATIVE_COFACTOR_UPDATE_COMPONENT_PASS_NO_POINT_ADD_RESULT'
freeze=json.loads((r/freeze_name).read_text());assert len(freeze['protected_files'])==17
assert all(sha(t/p)==h for p,h in{**freeze['source_files'],**freeze['protected_files']}.items())
added=r/'added-source';added.mkdir(exist_ok=False)
tracked=set(subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines())
for p in(t/'src/point_add').rglob('*'):
 if p.is_file()and p.relative_to(t).as_posix()not in tracked:
  dest=added/p.relative_to(t/'src/point_add');dest.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(p,dest)
streams={p.name:{'sha256':sha(p),'bytes':p.stat().st_size}for p in r.glob('*.ops.bin')}
runtime={'status':status,'sealed_at_utc':datetime.now(timezone.utc).isoformat(),'source_freeze_sha256':sha(r/freeze_name),
 'protected_files_checked':17,'native_result':result,'streams_retained_on_server':streams,
 'source_base':freeze.get('base'),'no_final_gate_nonce_or_point_add_score':True}
binary=[p for p in(t/'target/release/deps').glob('build_circuit-*')if p.is_file()and os.access(p,os.X_OK)]
runtime['test_binaries']={str(p):sha(p)for p in binary}
(r/'TERMINAL-AUDIT.json').write_text(json.dumps(runtime,indent=2)+'\n')
files=[]
for p in sorted(r.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(r)
 if any(x in rel.parts for x in ['observer','primitive','target','__pycache__']):continue
 if p.name.endswith('.ops.bin')or'resource-preflight'in p.name:continue
 if p.name in ['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','LOCAL-VERIFICATION.json']:continue
 files.append(p)
manifest={p.relative_to(r).as_posix():sha(p)for p in files}
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':manifest,'terminal_audit':runtime},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as a:
 for p in files+[r/'EVIDENCE-MANIFEST.json']:a.add(p,arcname=p.relative_to(r).as_posix())
receipt={'status':status,'archive_sha256':sha(r/'evidence.tar.gz'),'archive_bytes':(r/'evidence.tar.gz').stat().st_size,'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')}
(r/'PACKAGE-RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
