"""Seal terminal exact-carry development results; never issue a gate verdict."""
import hashlib,json,os,shutil,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
ws=Path('/home/hclau/ecdsa_research');name=sys.argv[1]
assert name in ['breakthrough-parity-integration-20261020','breakthrough-parity-cap-20261020','breakthrough-parity-paused-20261020','breakthrough-fold-plan7-20261020']
r=ws/name
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
if 'paused' in name:
    t=r/'primitive';freeze='SOURCE_FREEZE-v2.json';assert(r/'run-v2.exit').read_text().strip()=='0'
    assert'test result: ok. 3 passed; 0 failed;'in(r/'tests-v2.log').read_text()
    result={'status':'PAUSED_COMPONENT_AND_DECLARED_CALLBACK_CONTRACT_PASS','tests':3,'small_basis_evaluations':261888,
        'some_bridge_patterns_duplicate':True,'physical_rng_phase_basis_states':64,'intended_nonzero_phase_consumer':True,
        'initial_compile_failure_preserved':True,'scope':'Component only; caller must honor its source/target read set and restoration contract.'}
    (r/'NATIVE-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
else:
    t=r/'observer';freeze='SOURCE_FREEZE.json';assert(r/'run.exit').read_text().strip()=='0'
    if 'integration' in name:
        assert(r/'replay.exit').read_text().strip()=='0'
        result=json.loads((r/'PAIRED-DIAGNOSTIC.json').read_text())
        parent=[json.loads(l)for l in(r/'parent-census.jsonl').read_text().splitlines()]
        candidate=[json.loads(l)for l in(r/'candidate-census.jsonl').read_text().splitlines()]
        def value_cases(rows):
            return {(row['batch'],x['lane']):(x['k1'],x['k2'])for row in rows for x in row['failures']if x['value']}
        assert value_cases(parent)==value_cases(candidate)
        semantic={'status':'EXACT_SAME_52_VALUE_FAILING_SHOT_IDENTITIES','value_failing_shots':len(value_cases(parent)),
            'scope':'Compares existing diagnostic failed-shot identities and paired inputs; not a full-output equality proof on failing inputs or a final gate.'}
        (r/'DIAGNOSTIC-SEMANTIC-AUDIT.json').write_text(json.dumps(semantic,indent=2)+'\n')
    elif 'fold-plan7' in name:
        result=json.loads((r/'ADMISSION-RESULT.json').read_text());assert len(result['cases'])==4
        assert result['cases'][0]['raw_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
        assert'test result: ok. 2 passed; 0 failed;'in(r/'tests.log').read_text()
    else:
        result=json.loads((r/'ADMISSION-RESULT.json').read_text());assert len(result['cases'])==7
        assert result['cases'][0]['stream_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
f=json.loads((r/freeze).read_text());assert len(f['protected_files'])==17
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
added=r/'added-source';added.mkdir(exist_ok=False)
tracked=set(subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines())
for p in(t/'src/point_add').rglob('*'):
    if p.is_file()and p.relative_to(t).as_posix()not in tracked:
        dest=added/p.relative_to(t/'src/point_add');dest.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(p,dest)
streams={}
for p in r.rglob('ops.bin'):
    if 'target'in p.parts:continue
    streams[str(p)]={'sha256':sha(p),'bytes':p.stat().st_size}
runtime={'sealed_at_utc':datetime.now(timezone.utc).isoformat(),'source_base':f['base'],'protected_files_checked':17,
    'source_freeze_sha256':sha(r/freeze),'result':result,'streams_retained_on_server':streams,'no_final_gate_nonce_or_scored_result':True}
runtime['binaries']={str(p):sha(p)for p in(t/'target/release/deps').glob('build_circuit-*')if p.is_file()and os.access(p,os.X_OK)}
(r/'TERMINAL-AUDIT.json').write_text(json.dumps(runtime,indent=2)+'\n')
files=[]
for p in sorted(r.rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(r)
    if any(x in rel.parts for x in['primitive','observer','target','__pycache__']):continue
    if p.name.endswith('.ops.bin')or p.name=='ops.bin'or'resource-preflight'in p.name:continue
    if p.name in['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','LOCAL-VERIFICATION.json']:continue
    files.append(p)
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p.relative_to(r).as_posix():sha(p)for p in files},'terminal_audit':runtime},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as archive:
    for p in files+[r/'EVIDENCE-MANIFEST.json']:archive.add(p,arcname=p.relative_to(r).as_posix())
receipt={'archive_sha256':sha(r/'evidence.tar.gz'),'archive_bytes':(r/'evidence.tar.gz').stat().st_size,'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')}
(r/'PACKAGE-RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
