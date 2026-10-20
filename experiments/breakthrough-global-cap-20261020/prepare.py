import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-core-loan-fold-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert not t.exists() and (old/'run.exit').read_text().strip()=='0';assert all(sha(old/'observer'/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in (old/'observer/src/point_add').rglob('*'):
 if p.is_file():q=t/p.relative_to(old/'observer');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
p=t/'src/point_add/mod.rs';raw=p.read_bytes();a=b'std::env::set_var("HEO_PIN_PP_WALK_MAX_QUBITS", &break_cap);';b=b'std::env::set_var("HEO_PIN_PP_WALK_MAX_QUBITS", &hard);';assert raw.count(a)==1;raw=raw.replace(a,b);p.write_bytes(raw);subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in (t/'src/point_add').rglob('*')if p.is_file()};f['scope']='Only set original walk planner cap to the independent hard cap, instead of leaving its budget1234 and retiming emitted primitives afterward. Original square cap1234 remains. Inherit native-validated adapters and complete full-fold loans; source-only resource planning change, no input/cut/window/iteration changes. Full control raw must remain13f6. Generation may fail; preserve failure. No finalgate/nonce/score.';(r/'SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
