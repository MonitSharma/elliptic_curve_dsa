import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'primitive';parent=ws/'breakthrough-phase-pebble-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((parent/'SOURCE_FREEZE.json').read_text())
assert not t.exists()and(parent/'run.exit').read_text().strip()=='0';assert all(sha(parent/'primitive'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for name in['builder.rs','phase_fusion.rs','mod.rs']:(t/'src/point_add'/name).write_bytes((parent/'primitive/src/point_add'/name).read_bytes())
(t/'src/point_add/phase_pebble.rs').write_bytes((r/'phase_pebble.rs').read_bytes());assert all(sha(t/p)==h for p,h in f['protected_files'].items())
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},'scope':'General phase-pebble: all valid nonadjacent schedules, exact carry-birth phase hooks, paused consumers with explicitly completed target sums where views are None. Targets/sources/carries must restore through consumer. No source borrowing or chunk-plan change; unchanged HMR count; component only, no gate/nonce/score.'},indent=2)+'\n')
