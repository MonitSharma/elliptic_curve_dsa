import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((r/'SOURCE_FREEZE.json').read_text())
assert(r/'run.exit').read_text().strip()=='101';assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
old=r/'failed-default-cap-fixture-v1';old.mkdir(exist_ok=False)
for p in[r/'SOURCE_FREEZE.json',r/'source.patch',r/'tests.log',t/'src/point_add/y15_onefold.rs']:shutil.copyfile(p,old/p.name)
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();prefix=raw.split(b'#[cfg(test)]mod budget_c3_tests{')[0];needle=b'c.r3_peak(|c|{fold_fwd_v2(c,&acc,';assert raw.count(needle)==1
raw=raw.replace(needle,b'crate::point_add::pingpong::with_phase_cap(Some(1234),||c.r3_peak(|c|{fold_fwd_v2(c,&acc,')
needle=b'fin,None,ttm,2);});FORCE.with';assert raw.count(needle)==1;raw=raw.replace(needle,b'fin,None,ttm,2);}));FORCE.with')
assert raw.split(b'#[cfg(test)]mod budget_c3_tests{')[0]==prefix;p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source-v2.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()};f['scope']+=' V1 fixture used unoverridden default walkcap1251, so oldcontrol exceeded assumed1234 before simulations. V2 uses existing with_phase_cap(Some1234) around each fullfold build, test-only. Runtimeprefix unchanged and failed widthfixture preserved.'
(r/'SOURCE_FREEZE-v2.json').write_text(json.dumps(f,indent=2)+'\n')
