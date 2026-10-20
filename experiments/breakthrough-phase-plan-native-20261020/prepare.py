import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'primitive';old=ws/'breakthrough-phase-pebble-paused-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert not t.exists()and(old/'run.exit').read_text().strip()=='0'
assert all(sha(old/'primitive'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'primitive/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'primitive');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
for name in['phase_plan.rs','phase_fit.rs']:(t/'src/point_add'/name).write_bytes((r/name).read_bytes())
with(t/'src/point_add/mod.rs').open('ab')as out:out.write(b'\nmod phase_fit;\nmod phase_plan;\n')
with(t/'src/point_add/y15_onefold.rs').open('ab')as out:out.write((r/'tests.rs').read_bytes())
assert not(t/'target').exists();subprocess.run(['cp','-a','--reflink=auto',str(old/'primitive/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'scope':'Component native weighted chunk plans. Preserve all production entry points; new executor is test-only inside original Y15 module. Exact actual-core/affine addition, phase, all RNG coefficients and inverse controls. No point-add score, final gate, nonce or source novelty claim.'},indent=2)+'\n')
