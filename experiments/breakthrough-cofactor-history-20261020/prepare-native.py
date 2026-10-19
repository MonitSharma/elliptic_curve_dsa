import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'primitive'
assert not t.exists()
base='90e777ea8242faa0acb2462c5cb5be7c318a2d64'
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),base],check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines()
protected={name:sha(t/name)for name in paths if not name.startswith('src/point_add/')};assert len(protected)==17
(t/'src/point_add/cofactor_history.rs').write_bytes((r/'cofactor_history.rs').read_bytes())
with(t/'src/point_add/mod.rs').open('ab')as f:f.write(b'\nmod cofactor_history;\n')
assert all(sha(t/name)==h for name,h in protected.items())
freeze={'status':'NATIVE_PRIMITIVE_ONLY_NOT_INTEGRATED','base':base,'protected_files':protected,
 'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
 'scope':'No generation, statistical gate, nonce or score. Primitive codec only, first-step/tail/scaling unresolved.'}
(r/'NATIVE-SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')
(r/'native-source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
