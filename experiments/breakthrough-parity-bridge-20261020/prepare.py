import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'primitive'
base='90e777ea8242faa0acb2462c5cb5be7c318a2d64'
assert not t.exists()
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),base],check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines()
protected={p:sha(t/p)for p in paths if not p.startswith('src/point_add/')};assert len(protected)==17
(t/'src/point_add/parity_bridge.rs').write_bytes((r/'parity_bridge.rs').read_bytes())
with(t/'src/point_add/mod.rs').open('ab')as f:f.write(b'\nmod parity_bridge;\n')
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':base,'protected_files':protected,
    'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
    'scope':'Parity-addend source-pivot borrowing component; no point-add integration, candidate, iteration envelope, approximate comparison or resource score.'},indent=2)+'\n')
