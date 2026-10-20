import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'primitive';old=ws/'breakthrough-live-core-rank-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert not t.exists() and (old/'run.exit').read_text().strip()=='0';assert all(sha(old/'primitive'/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in (old/'primitive/src/point_add').rglob('*'):
 if p.is_file():q=t/p.relative_to(old/'primitive');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();a=b'    #[cfg(test)] if live_core_tests::capture(&add,&k){return Vec::new();}';assert raw.count(a)==1;raw=raw.replace(a,a+b'\n    #[cfg(test)] if core_loan_tests::capture(&add,&k){return Vec::new();}\n');raw+=(r/'tests.rs').read_bytes();p.write_bytes(raw)
(t/'src/point_add/core_loan_certificate.rs').write_bytes((r/'certificate.rs').read_bytes());subprocess.run(['cp','-a','--reflink=auto',str(old/'primitive/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in (t/'src/point_add').rglob('*')if p.is_file()},'scope':'Test-only native active forward-prefix compression31->20 retained helpers, exact11 HMR Clifford repairs and32AND regeneration, all16384inputs, guards and allmeasurementcoefficients. No production implementation, full point-add score or finalgate.'},indent=2)+'\n')
