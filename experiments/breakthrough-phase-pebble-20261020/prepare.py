import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'primitive';parent=ws/'breakthrough-phase-fusion-20261020';f=json.loads((parent/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not t.exists()and(parent/'run.exit').read_text().strip()=='0';assert all(sha(parent/'primitive'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for name in['builder.rs','phase_fusion.rs','mod.rs']:(t/'src/point_add'/name).write_bytes((parent/'primitive/src/point_add'/name).read_bytes())
(t/'src/point_add/phase_pebble.rs').write_bytes((r/'phase_pebble.rs').read_bytes())
with(t/'src/point_add/mod.rs').open('ab')as stream:stream.write(b'\nmod phase_pebble;\n')
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},'scope':'Early carry erasure with early target-sum write. No regeneration: next-carry measurement corrected by tested two-stage phase kernel on NOT completed sum. Nonadjacent drops save d clean carries at expected0.5*sum(source-row ranks) additional scoredT; unchanged HMR draw count. Component only, no point-add score/final gate/nonce/novelty claim.'},indent=2)+'\n')
