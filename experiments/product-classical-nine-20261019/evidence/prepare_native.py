import hashlib,json,shutil,socket,subprocess,tarfile
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'candidate';q=ws/'product-pareto-20261019/parent4-qualification';f=ws/'product-classical-factors-refresh-20261019';c=ws/'product-captured-factors-20261019'
assert socket.gethostname()=='LHC-104-070' and not t.exists()
assert (f/'control.exit').read_text().strip()=='0'
assert (r/'control.exit').read_text().strip()=='0'
assert json.loads((f/'CONTROL-parent4.json').read_text())['status']=='PROTECTED_SIMULATOR_CLASSICAL_FACTOR_FULL_TRANSCRIPT_CONTROL_PASS'
choice=json.loads((ws/'product-factor-cost-proof-20261019/RESULT.json').read_text())
assert choice['status']=='ALL_ADDITIONAL_STATIC_REDUCTIONS_ARE_UNIVERSALLY_INACTIVE'
expected=json.loads((r/'RESEARCH.json').read_text());assert expected['output_count']==17889627
assert json.loads((r/'CONTROL-nine.json').read_text())['saved_executed_Toffolis_total_on_512_control_shots']==512
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
archive=q/'point-add-source.tar.gz';assert sha(archive)=='71bbeefcfa21ea9668439210f7dfbb279e0e623aa40b33c1b7516efcb45bb43c'
base='0c3a0751ab66bd9144358d67563bcb79201cf636';repo=ws/'upstream'
before={'hostname':socket.gethostname(),'repo':str(repo),'head':subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(),'branch':subprocess.check_output(['git','-C',str(repo),'branch','--show-current'],text=True).strip(),'status':subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True)}
(r/'REPOSITORY-PREFLIGHT.json').write_text(json.dumps(before,indent=2)+'\n')
subprocess.run(['git','-C',str(repo),'worktree','add','--detach',str(t),base],check=True)
manifest=json.loads((q/'point-add-source.json').read_text())
with tarfile.open(archive) as a:
    members=a.getmembers();assert all((m.isfile() or m.isdir()) and (m.name+'/').startswith('src/point_add/') and '..' not in Path(m.name).parts for m in members)
    assert {m.name for m in members if m.isfile()}==set(manifest)
    a.extractall(t,filter='data')
assert all(sha(t/p)==h for p,h in manifest.items())
point=t/'src/point_add'
for name in ['classical_factors_xor.rs','product7_simplify.rs','tests_classical_factors.rs']:
    assert not (point/name).exists();shutil.copy2(f/'proof'/name,point/name)
shutil.copy2(r/'classical_xor_control.rs',point/'classical_xor_control.rs')
mod=point/'mod.rs';src=mod.read_text();needle='    let nonce: u64 = required_env("TAIL_NONCE");';assert src.count(needle)==1
src=src.replace(needle,'    ops = classical_factors_xor::simplify_classical(ops);\n    ops = classical_xor_control::run(ops);\n'+needle)
mod.write_text(src+'\nmod classical_factors_xor;\nmod classical_xor_control;\n')
subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True)
changed=subprocess.check_output(['git','-C',str(t),'diff','--name-only','HEAD'],text=True).splitlines();assert changed and all(p.startswith('src/point_add/') for p in changed)
protected={}
for p in subprocess.check_output(['git','-C',str(t),'ls-files'],text=True).splitlines():
    if p.startswith('src/point_add/'):continue
    assert (t/p).read_bytes()==subprocess.check_output(['git','-C',str(t),'show','HEAD:'+p]);protected[p]=sha(t/p)
assert len(protected)==17
files={p.relative_to(t).as_posix():sha(p) for p in point.rglob('*') if p.is_file()}
patch=subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']);(r/'candidate-source.patch').write_bytes(patch)
with tarfile.open(r/'point-add-source.tar.gz','x:gz') as a:
    for p in sorted(files):a.add(t/p,arcname=p,recursive=False)
freeze={'status':'SOURCE_FROZEN_BEFORE_NATIVE_TESTS_NO_STATISTICAL_GATE_YET','base_revision':base,'candidate':str(t),'source_files':files,'protected_files':protected,
        'source_archive_sha256':sha(r/'point-add-source.tar.gz'),'patch_sha256':sha(r/'candidate-source.patch'),'expected_raw_sha3_256':expected['output_full_sha3_256'],
        'expected_ops':expected['output_count'],'parent4_source_archive_sha256':sha(archive),'inherited_nonce_unchanged':'1048009047001','submission_mode':'queue',
        'no_nonce_screened_on_this_circuit':True}
(r/'SOURCE_FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')
print(json.dumps({k:v for k,v in freeze.items() if k not in ['source_files','protected_files']},indent=2))
