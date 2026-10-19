import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';base='90e777ea8242faa0acb2462c5cb5be7c318a2d64'
assert not t.exists();primitive=ws/'breakthrough-parity-bridge-20261020'
assert(primitive/'run.exit').read_text().strip()=='0'
f=json.loads((primitive/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(primitive/'primitive'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),base],check=True)
protected=f['protected_files'];assert len(protected)==17;assert all(sha(t/p)==h for p,h in protected.items())
old=ws/'breakthrough-cap-cost-20261020/observer'
for name in['builder.rs','record.rs','break_profile.rs','mod.rs']:
    (t/'src/point_add'/name).write_bytes((old/'src/point_add'/name).read_bytes())
(t/'src/point_add/parity_bridge.rs').write_bytes((primitive/'primitive/src/point_add/parity_bridge.rs').read_bytes())
with(t/'src/point_add/mod.rs').open('ab')as stream:stream.write(b'\nmod parity_bridge;\n')
p=t/'src/point_add/leapfrog.rs';raw=p.read_bytes()
needle=b'fn ladder_parity_add(c: &mut Builder, acc: &[QubitId], add: &[Vec<QubitId>], cin: Option<QubitId>) {'
assert raw.count(needle)==1;raw=raw.replace(needle,needle+b'\n    if parity_bridge_try(c,acc,add,cin){return;}\n')
raw+=(r/'adapter.rs').read_bytes();p.write_bytes(raw)
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':base,'protected_files':protected,
    'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
    'primitive_source_sha256':sha(t/'src/point_add/parity_bridge.rs'),'workspace_policy_target':1200,
    'scope':'Raw complete-arithmetic integration diagnostic. Only source-exclusive plain ladders without pending carry hooks can change. Every arithmetic/window/iteration/cap setting remains accepted1234. No final gate/nonce or scored claim.'},indent=2)+'\n')
