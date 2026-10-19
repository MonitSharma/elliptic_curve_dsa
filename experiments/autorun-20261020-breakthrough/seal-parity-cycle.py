"""Seal terminal parity component and byte-identical source-site audit."""
import hashlib,json,os,shutil,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
ws=Path('/home/hclau/ecdsa_research');name=sys.argv[1]
assert name in ['breakthrough-parity-bridge-20261020','breakthrough-parity-sites-20261020']
r=ws/name;assert(r/'run.exit').read_text().strip()=='0'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
f=json.loads((r/'SOURCE_FREEZE.json').read_text())
if 'bridge' in name:
    t=r/'primitive';log=(r/'tests.log').read_text();assert'test result: ok. 3 passed; 0 failed;'in log
    proof=json.loads((r/'LOCAL-LEMMAS.json').read_text());assert len(proof['queries'])==4
    result={'status':'NATIVE_PARITY_SOURCE_BRIDGE_COMPONENT_PASS','tests':3,'small_basis_evaluations':523776,
        'some_small_bridge_patterns_duplicate':True,'physical_rng_phase_basis_states':64,'exact_inverse_checked':True,
        'unsafe_admission_emits_zero_ops':True,'local_boolean_smt_unsat':4,'missing_cz_negative_control':'SAT',
        'scope':'Component only; one clean carry saved per extra CCX. No complete point-add record.'}
    (r/'NATIVE-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
else:
    t=r/'observer';result=json.loads((r/'SITE-AUDIT.json').read_text());assert result['sites']==946
    assert sha(t/'ops.bin')==f['expected_native_raw_sha256']
assert len(f['protected_files'])==17
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
added=r/'added-source';added.mkdir(exist_ok=False)
tracked=set(subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines())
for p in(t/'src/point_add').rglob('*'):
    if p.is_file()and p.relative_to(t).as_posix()not in tracked:
        dest=added/p.relative_to(t/'src/point_add');dest.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(p,dest)
runtime={'sealed_at_utc':datetime.now(timezone.utc).isoformat(),'source_base':f['base'],'protected_files_checked':17,
    'source_freeze_sha256':sha(r/'SOURCE_FREEZE.json'),'result':result,'no_final_gate_nonce_or_score':True}
if(t/'ops.bin').exists():runtime['server_retained_stream']={'path':str(t/'ops.bin'),'sha256':sha(t/'ops.bin'),'bytes':(t/'ops.bin').stat().st_size}
runtime['binaries']={str(p):sha(p)for p in(t/'target/release/deps').glob('build_circuit-*')if p.is_file()and os.access(p,os.X_OK)}
(r/'TERMINAL-AUDIT.json').write_text(json.dumps(runtime,indent=2)+'\n')
files=[]
for p in sorted(r.rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(r)
    if any(x in rel.parts for x in['primitive','observer','target','__pycache__']):continue
    if p.name.endswith('.ops.bin')or'resource-preflight'in p.name:continue
    if p.name in['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','LOCAL-VERIFICATION.json']:continue
    files.append(p)
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p.relative_to(r).as_posix():sha(p)for p in files},'terminal_audit':runtime},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as archive:
    for p in files+[r/'EVIDENCE-MANIFEST.json']:archive.add(p,arcname=p.relative_to(r).as_posix())
receipt={'archive_sha256':sha(r/'evidence.tar.gz'),'archive_bytes':(r/'evidence.tar.gz').stat().st_size,'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')}
(r/'PACKAGE-RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
