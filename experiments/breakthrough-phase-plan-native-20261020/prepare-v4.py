import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((r/'SOURCE_FREEZE-v3.json').read_text())
assert(r/'run-v3.exit').read_text().strip()=='0';assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();runtime=raw.split(b'#[cfg(test)]mod weighted_plan_tests{')[0];shutil.copyfile(p,r/'y15-tests-v3.rs')
needle=b'for probe in 0..140{fixture(pattern,budget,false,inverse,Some(probe));}';assert raw.count(needle)==1;raw=raw.replace(needle,b'for probe in 0..512{fixture(pattern,budget,false,inverse,Some(probe));}')
needle=b'let nr=draws(&ops);let core_nr=draws(&core);';assert raw.count(needle)==1;raw=raw.replace(needle,needle+b'assert!(nr<512);if probe.is_some_and(|p|p>nr+1){return;}')
assert raw.split(b'#[cfg(test)]mod weighted_plan_tests{')[0]==runtime;p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source-v4.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()};f['scope']+=' V4 test-only strengthening: original fixed140 coefficient probes did not cover every draw of inverse circuits. Use512 upper bound, assert actual nr<512, run0..nr+1 probes and stop extra repeats. Planner/runtime prefix unchanged; preserve v3 PASS as narrower controls.'
(r/'SOURCE_FREEZE-v4.json').write_text(json.dumps(f,indent=2)+'\n')
