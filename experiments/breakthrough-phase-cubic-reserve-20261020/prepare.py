import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-phase-cubic-cap-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert not t.exists() and (old/'run-v2.exit').read_text().strip()=='0'
assert all(sha(old/'observer'/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in (old/'observer/src/point_add').rglob('*'):
 if p.is_file():q=t/p.relative_to(old/'observer');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();a=b'Y29_FAULT==0&&k1!=k2&&hard<1234&&c.active_qubits()as usize+1>hard';b=b'Y29_FAULT==0&&k1!=k2&&hard<1234';assert raw.count(a)==1;raw=raw.replace(a,b);p.write_bytes(raw)
subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in (t/'src/point_add').rglob('*')if p.is_file()},'caps':[1234,1233],'scope':'Reserve the long-lived T0Phase letter-product wire whenever independent hard cap1233. Same tested exact direct cubic phase; no immediate-allocation-only restriction. Trace proves single multiply constructor at live523 whose retained temporary contributes late1234 peak. No final gate, nonce or score.'},indent=2)+'\n')
