"""Extend frozen classical9 only with the independent wider exact factors."""
import hashlib,json,shutil,socket,subprocess,tarfile
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;n=ws/'product-classical-nine-20261019';w=ws/'product-classical-factors-wide-20261019';t=r/'candidate'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
assert socket.gethostname()=='LHC-104-070' and not t.exists()
assert (w/'run-v2.exit').read_text().strip()=='0'
control=json.loads((w/'CONTROL.json').read_text());assert control['status']=='PROTECTED_SIMULATOR_CLASSICAL_FACTOR_FULL_TRANSCRIPT_CONTROL_PASS'
assert control['saved_executed_Toffolis_total_on_512_control_shots']==493
expected=json.loads((w/'wide9.json').read_text());assert expected['static_Toffolis_removed']==3 and expected['output_count']==17889635
assert expected['output_full_sha3_256']=='2ef31475f03b40a72d5522d830717aef4c1675d0e1a061bf0bfed78ab7d2f265'
parent=json.loads((n/'SOURCE_FREEZE.json').read_text());archive=n/'point-add-source.tar.gz'
assert sha(archive)=='2932b6cf662e2d6be05679b0d5e34a9149ccbceaca57f8ce92cfccd13b8c8f6e'==parent['source_archive_sha256']
base='0c3a0751ab66bd9144358d67563bcb79201cf636';repo=ws/'upstream'
pre={'hostname':socket.gethostname(),'head':subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(),'branch':subprocess.check_output(['git','-C',str(repo),'branch','--show-current'],text=True).strip(),'status':subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True)}
(r/'REPOSITORY-PREFLIGHT.json').write_text(json.dumps(pre,indent=2)+'\n')
subprocess.run(['git','-C',str(repo),'worktree','add','--detach',str(t),base],check=True)
with tarfile.open(archive) as a:
    members=a.getmembers();assert all((m.isfile() or m.isdir()) and (m.name+'/').startswith('src/point_add/') and '..' not in Path(m.name).parts for m in members)
    assert {m.name for m in members if m.isfile()}==set(parent['source_files']);a.extractall(t,filter='data')
assert all(sha(t/p)==h for p,h in parent['source_files'].items())
point=t/'src/point_add';target=point/'classical_wide';target.mkdir()
s=(w/'proof/classical_factors_xor.rs').read_text().replace('at most seven immutable','at most nine immutable').replace('include!("../table.rs")','include!("table.rs")').replace('#[path="../tests_table.rs"]','#[path="tests_table.rs"]')
(target/'mod.rs').write_text(s)
s=(w/'table.rs').read_text();needle='fn support_cap()->usize{';start=s.index(needle)
end=s.index('\nimpl Truth {',start)
s=s[:start]+'fn support_cap()->usize{9}\n'+s[end:]
assert 'CLASSICAL_WIDE_CAP' not in s and 'OnceLock' not in s
(target/'table.rs').write_text(s)
for source,dest in [('proof/product7_simplify.rs','product7_simplify.rs'),('proof/tests_classical_factors.rs','tests_classical_factors.rs'),('tests_table.rs','tests_table.rs')]:shutil.copy2(w/source,target/dest)
mod=point/'mod.rs';s=mod.read_text();needle='    ops = classical_xor_control::run(ops);';assert s.count(needle)==1
mod.write_text(s.replace(needle,needle+'\n    ops = classical_wide::simplify_classical(ops);')+'\nmod classical_wide;\n')
subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True)
changed=subprocess.check_output(['git','-C',str(t),'diff','--name-only','HEAD'],text=True).splitlines();assert all(p.startswith('src/point_add/') for p in changed)
protected={}
for p in subprocess.check_output(['git','-C',str(t),'ls-files'],text=True).splitlines():
    if p.startswith('src/point_add/'):continue
    assert (t/p).read_bytes()==subprocess.check_output(['git','-C',str(t),'show','HEAD:'+p]);protected[p]=sha(t/p)
assert protected==parent['protected_files'] and len(protected)==17
files={p.relative_to(t).as_posix():sha(p) for p in point.rglob('*') if p.is_file()}
patch=subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']);(r/'candidate-source.patch').write_bytes(patch)
with tarfile.open(r/'point-add-source.tar.gz','x:gz') as a:
    for p in sorted(files):a.add(t/p,arcname=p,recursive=False)
freeze={'status':'SOURCE_FROZEN_BEFORE_NATIVE_TESTS_NO_STATISTICAL_GATE_DECLARED','base_revision':base,'candidate':str(t),'source_files':files,'protected_files':protected,
 'source_archive_sha256':sha(r/'point-add-source.tar.gz'),'patch_sha256':sha(r/'candidate-source.patch'),'expected_raw_sha3_256':expected['output_full_sha3_256'],'expected_ops':expected['output_count'],
 'parent_source_archive_sha256':sha(archive),'inherited_nonce_unchanged':'1048009047001','submission_mode':'queue','no_nonce_screened_on_this_circuit':True,
 'scope':'Twelve static CCX reductions relative to parent4; do not call this twelve executed Toffolis. Wider extension saves493/512 in raw controls, not a scored result.'}
(r/'SOURCE_FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n');print(json.dumps({k:v for k,v in freeze.items() if k not in ['source_files','protected_files']},indent=2))
