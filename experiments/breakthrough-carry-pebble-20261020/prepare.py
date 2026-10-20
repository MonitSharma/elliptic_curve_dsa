import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'primitive';base='90e777ea8242faa0acb2462c5cb5be7c318a2d64';assert not t.exists()
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),base],check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();names=subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines();protected={p:sha(t/p)for p in names if not p.startswith('src/point_add/')};assert len(protected)==17
(t/'src/point_add/carry_pebble.rs').write_bytes((r/'carry_pebble.rs').read_bytes())
with(t/'src/point_add/mod.rs').open('ab')as stream:stream.write(b'\nmod carry_pebble;\n')
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':base,'protected_files':protected,'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},'scope':'Exact plain affine/parity adder with a live incoming carry, n>=5, source/target/cin disjoint. Early measurement-erasure and late regeneration of first carry. One fewer clean carry, one extra CCX/HMR. No source exclusivity or chunk-plan change. Component only, no resource record/final gate/nonce.'},indent=2)+'\n')
