import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-phase-pebble-bridge-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert not t.exists()and(old/'run-v2.exit').read_text().strip()=='0'
assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'observer/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'observer');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();needle=b'fn ladder_chunk(c: &mut Builder, acc: &[QubitId], add: &[Lin], lo: usize, w: usize, cin: QubitId, last: bool) -> Option<QubitId> {';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'\n    if let Some(out)=phase_chunk_try(c,&acc[lo..lo+w],&add[lo..lo+w],cin,!last,last&&w>=2){return out;}\n');p.write_bytes(raw)
assert not(t/'target').exists();subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'scope':'Apply existing exact phase chunk adapter inside original ladder_chunk, preserving original plan8/9 boundary-drop lifetimes and erasures. All prior fresh-source exclusions and exact control remain. No final gate, nonce or score.'},indent=2)+'\n')
