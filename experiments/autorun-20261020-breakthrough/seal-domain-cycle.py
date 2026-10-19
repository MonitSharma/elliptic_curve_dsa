"""Seal the three terminal attribution/component studies from this cycle."""
import hashlib,json,os,shutil,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
ws=Path('/home/hclau/ecdsa_research');name=sys.argv[1]
assert name in ['breakthrough-subphase-20261020','breakthrough-domain-profile-20261020','breakthrough-cofactor-rotation-20261020']
r=ws/name
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
if 'subphase' in name:
    t=r/'observer';freeze_file='SOURCE_FREEZE-v2.json'
    assert(r/'run-v2.exit').read_text().strip()=='0'and(r/'refine.exit').read_text().strip()=='0'
    result=json.loads((r/'REFINEMENT-CONTROL.json').read_text())
    status='RAW_LEGACY_NAME_ATTRIBUTION_COMPLETE_WITH_SEMANTIC_ALIAS_LIMITATION'
elif 'domain' in name:
    t=r/'observer';freeze_file='SOURCE_FREEZE.json'
    assert(r/'run.exit').read_text().strip()=='0'
    result=json.loads((r/'REPLAY-CONTROL.json').read_text())
    assert result['status']=='ALL_512_ROWS_MATCH_PREVIOUS_FROZEN_RAW_STREAM'
    status='DIRECT_RAW_MEMBERSHIP_PROFILE_CONTROLS_PASS'
else:
    t=r/'primitive';freeze_file='SOURCE_FREEZE.json'
    assert(r/'run.exit').read_text().strip()=='0'
    log=(r/'tests.log').read_text()
    assert'test result: ok. 8 passed; 0 failed;'in log
    assert'test result: ok. 2 passed; 0 failed;'in log
    result={'status':'EXACT_COMPONENT_ROTATION_TRANSFER_PASS','unique_native_tests':8,'repeated_reflection_tests':2,
       'small_word_basis_cases':8160,'gate_formula_widths':list(range(9,41)),
       'forward_sixteen_bit_component_ccx':86,'previous_forward_sixteen_bit_component_ccx':93,
       'scope':'Component only; existing reflection construction, no novelty or point-add resource claim.'}
    (r/'NATIVE-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    status='COFACTOR_ROTATION_COMPONENT_PASS_CONSERVATIVE_INTEGRATION_DEPRIORITIZED'
freeze=json.loads((r/freeze_file).read_text())
assert len(freeze['protected_files'])==17
assert all(sha(t/p)==h for p,h in{**freeze['source_files'],**freeze['protected_files']}.items())
added=r/'added-source';added.mkdir(exist_ok=False)
tracked=set(subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines())
for p in(t/'src/point_add').rglob('*'):
    if p.is_file()and p.relative_to(t).as_posix()not in tracked:
        dest=added/p.relative_to(t/'src/point_add');dest.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(p,dest)
streams={}
if (t/'ops.bin').exists():
    assert sha(t/'ops.bin')==freeze['expected_native_raw_sha256']
    streams[str(t/'ops.bin')]={'sha256':sha(t/'ops.bin'),'bytes':(t/'ops.bin').stat().st_size}
runtime={'status':status,'sealed_at_utc':datetime.now(timezone.utc).isoformat(),'source_base':freeze['base'],
    'source_freeze_sha256':sha(r/freeze_file),'protected_files_checked':17,'result':result,
    'streams_retained_on_server':streams,'no_candidate_gate_nonce_or_score':True}
if 'rotation' in name:
    runtime['binaries']={str(p):sha(p)for p in(t/'target/release/deps').glob('build_circuit-*')if p.is_file()and os.access(p,os.X_OK)}
else:
    binary=ws/'breakthrough-profile-20261020/tool/target/release/phase-replay'
    runtime['replay_binary_sha256']=sha(binary)
    runtime['unchanged_replay_tool_evidence_archive_sha256']='9a5d3d8785ba5a7c532a85af288f8d3a51bf9ece519e30b7f3cc58b6fcd72271'
(r/'TERMINAL-AUDIT.json').write_text(json.dumps(runtime,indent=2)+'\n')
files=[]
for p in sorted(r.rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(r)
    if any(x in rel.parts for x in['observer','primitive','target','__pycache__']):continue
    if p.name.endswith('.ops.bin')or'resource-preflight'in p.name:continue
    if p.name in['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','LOCAL-VERIFICATION.json']:continue
    files.append(p)
manifest={p.relative_to(r).as_posix():sha(p)for p in files}
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':manifest,'terminal_audit':runtime},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as a:
    for p in files+[r/'EVIDENCE-MANIFEST.json']:a.add(p,arcname=p.relative_to(r).as_posix())
receipt={'status':status,'archive_sha256':sha(r/'evidence.tar.gz'),'archive_bytes':(r/'evidence.tar.gz').stat().st_size,
    'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')}
(r/'PACKAGE-RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
