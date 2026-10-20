import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'primitive';old=ws/'breakthrough-core-rank-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE-v2.json').read_text())
assert not t.exists()and(old/'run-v2.exit').read_text().strip()=='0';assert all(sha(old/'primitive'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'primitive/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'primitive');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();needle=b'    let mut add = if Y16_CORE { addend_prog(c, &mut recs, &k, &Y16_FWD_GATES, &Y16_FWD_OUT, mw) } else { addend_from_k(c, &mut recs, &k, mw) };';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'\n    #[cfg(test)] if live_core_tests::capture(&add,&k){return Vec::new();}\n');raw+=(r/'tests.rs').read_bytes();p.write_bytes(raw)
(t/'src/point_add/live_core_expected.dat').write_bytes((r/'expected.dat').read_bytes())
assert not(t/'target').exists();subprocess.run(['cp','-a','--reflink=auto',str(old/'primitive/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'functions_sha256':sha(r/'FUNCTIONS.json'),'expected_table_sha256':sha(r/'expected.dat'),'scope':'Test-only snapshot of actual active fold_fwd_v2 fin0 prefix; compiled production behavior unchanged. Independent full14-bit source model vsnative31held/21field/8derivedk functions. No point-add score, finalgate, nonce, inputrestriction or arithmeticcut.'},indent=2)+'\n')
