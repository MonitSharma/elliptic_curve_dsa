import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((r/'SOURCE_FREEZE.json').read_text())
assert(r/'run.exit').read_text().strip()=='101';assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
old=r/'failed-unsupported-fixture-v1';old.mkdir(exist_ok=False)
for p in[r/'SOURCE_FREEZE.json',r/'source.patch',r/'tests.log',t/'src/point_add/modular.rs']:shutil.copyfile(p,old/p.name)
p=t/'src/point_add/modular.rs';raw=p.read_bytes();prefix=raw.split(b'#[cfg(test)]mod terminal_contract_tests{')[0]
needle=b'for k in[1,6,7,8]{for desired in[false,true]{for probe in 0..15';assert raw.count(needle)==1
raw=raw.replace(needle,b'for k in[1,7,8,9]{for desired in[false,true]{for probe in 0..17')
needle=b'fixture(8,k,has_cin,desired,&ds,guard,Some(probe))';assert raw.count(needle)==1;raw=raw.replace(needle,b'fixture(9,k,has_cin,desired,&ds,guard,Some(probe))')
assert raw.split(b'#[cfg(test)]mod terminal_contract_tests{')[0]==prefix;p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source-v2.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()};f['scope']+=' V1 allsmall/offpromise channel and alias tests PASS; coefficient fixture requested zero-cin n8 drops[2,4], an inadmissible prefix. V2 fixture-only uses n9, padding1/7/8/9 and all17 originalmeasurement/reset probes. Runtime/module prefix unchanged; preserve v1FAIL.'
(r/'SOURCE_FREEZE-v2.json').write_text(json.dumps(f,indent=2)+'\n')
