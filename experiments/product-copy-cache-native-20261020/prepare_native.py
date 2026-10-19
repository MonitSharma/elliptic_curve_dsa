import hashlib,json,socket,subprocess,tarfile,shutil
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;n=ws/'product-classical-twelve-native-20261019';t=r/'candidate';sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
assert socket.gethostname()=='LHC-104-070' and not t.exists()
assert (n/'run.exit').read_text().strip()=='0' and (n/'gate.exit').read_text().strip()=='0'
gate=json.loads((n/'qualification/RESULT.json').read_text());assert gate['status']=='FAILURE_GATE_PASS' and all(gate['rules'].values())
control=json.loads((r/'prototype-RESULT.json').read_text());assert control['status']=='REVERSIBLE_COPY_CACHE_SOURCE_SCREEN_COMPLETED' and control['cache_pairs']==1
assert control['control']['saved_executed_Toffolis_total_on_512_control_shots']==512
expected=control['source'];assert expected['output_ops']==17889637 and expected['output_sha3_256']=='d343ca717c726c9136505edb1ba3602a58f7bfe063151d8a9e82b4f39d71a6a5'
assert expected['sites'][0]['first']==14241681 and expected['sites'][0]['last']==14245297 and expected['sites'][0]['storage']==558
parent=json.loads((n/'SOURCE_FREEZE.json').read_text());archive=n/'point-add-source.tar.gz'
assert sha(archive)=='4b7c6d3bcfc1ee1540d57c2a3e991281408ed90d09c192c5ce60e0fa15ce3d17'==parent['source_archive_sha256']
base='0c3a0751ab66bd9144358d67563bcb79201cf636';repo=ws/'upstream'
pre={'hostname':socket.gethostname(),'head':subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(),'branch':subprocess.check_output(['git','-C',str(repo),'branch','--show-current'],text=True).strip(),'status':subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True)}
(r/'REPOSITORY-PREFLIGHT.json').write_text(json.dumps(pre,indent=2)+'\n');subprocess.run(['git','-C',str(repo),'worktree','add','--detach',str(t),base],check=True)
with tarfile.open(archive) as a:
    members=a.getmembers();assert all((m.isfile() or m.isdir()) and (m.name+'/').startswith('src/point_add/') and '..' not in Path(m.name).parts for m in members)
    assert {m.name for m in members if m.isfile()}==set(parent['source_files']);a.extractall(t,filter='data')
assert all(sha(t/p)==h for p,h in parent['source_files'].items())
point=t/'src/point_add';assert {p.relative_to(t).as_posix() for p in point.rglob('*') if p.is_file()}==set(parent['source_files'])
for name in ['copy_cache_one.rs','tests_copy_cache_one.rs']:shutil.copy2(r/name,point/name)
p=point/'mod.rs';s=p.read_text();needle='    ops = classical_wide::simplify_classical(ops);';assert s.count(needle)==1;p.write_text(s.replace(needle,needle+'\n    ops = copy_cache_one::run(ops);')+'\nmod copy_cache_one;\n')
subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True)
assert all(p.startswith('src/point_add/') for p in subprocess.check_output(['git','-C',str(t),'diff','--name-only','HEAD'],text=True).splitlines())
protected={}
for name in subprocess.check_output(['git','-C',str(t),'ls-files'],text=True).splitlines():
    if name.startswith('src/point_add/'):continue
    assert (t/name).read_bytes()==subprocess.check_output(['git','-C',str(t),'show','HEAD:'+name]);protected[name]=sha(t/name)
assert protected==parent['protected_files'] and len(protected)==17
files={p.relative_to(t).as_posix():sha(p) for p in point.rglob('*') if p.is_file()};assert len(files)==182
(r/'candidate-source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']))
with tarfile.open(r/'point-add-source.tar.gz','x:gz') as a:
    for name in sorted(files):a.add(t/name,arcname=name,recursive=False)
freeze={'status':'SOURCE_FROZEN_BEFORE_PINNED_NATIVE_TESTS_NO_NEW_GATE','at_utc':datetime.now(timezone.utc).isoformat(),'base_revision':base,'candidate':str(t),'source_files':files,'protected_files':protected,'source_archive_sha256':sha(r/'point-add-source.tar.gz'),'patch_sha256':sha(r/'candidate-source.patch'),'expected_raw_sha3_256':expected['output_sha3_256'],'expected_ops':expected['output_ops'],'parent_source_archive_sha256':sha(archive),'parent_passing_gate_sha256':sha(n/'qualification/RESULT.json'),'inherited_nonce_unchanged':'1048009047001','submission_mode':'queue','no_nonce_screened_on_this_circuit':True,'scope':'One additional unconditional executed Toffoli saved by a reversible idle-wire cache; native generation, independent proofs and own final gate remain due. No scored record.'}
(r/'SOURCE_FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n');print(json.dumps({k:v for k,v in freeze.items() if k not in ['source_files','protected_files']},indent=2))
