import hashlib,json,subprocess,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((r/'SOURCE_FREEZE.json').read_text())
assert(r/'run.exit').read_text().strip()=='0';assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();prefix=raw.split(b'#[cfg(test)]mod weighted_plan_tests{')[0];shutil.copyfile(p,r/'y15-tests-v1.rs')
needle=b'let mut random=Words{data,pos:0};let mut s=Simulator::new';assert raw.count(needle)==1
raw=raw.replace(needle,b'''if probe.is_none(){let mut h=Shake256::default();h.update(b"weighted-phase-chunks-measurements-v2");h.update(&(first as u64).to_le_bytes());h.finalize_xof().read(&mut data);}
            let mut random=Words{data,pos:0};let mut s=Simulator::new''')
assert raw.split(b'#[cfg(test)]mod weighted_plan_tests{')[0]==prefix;p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source-v2.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()};f['scope']+=' V2 fixture-only diagnostic strengthening: full-case measurement words use independent fixed SHAKE label weighted-phase-chunks-measurements-v2, same original input basis cases. Old deterministic multiplication words were correlated and not suitable as unbiased cost estimates. Preserve all v1PASS controls. No circuit/planner/production-prefix change; full15 configurations rerun, no gate/nonce or score.'
(r/'SOURCE_FREEZE-v2.json').write_text(json.dumps(f,indent=2)+'\n')
