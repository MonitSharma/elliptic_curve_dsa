"""Add fully enabled exhaustive cases, preserving passed mixed-guard evidence."""
import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive';f=json.loads((r/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert(r/'run.exit').read_text().strip()=='0';assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
saved=r/'passed-mixed-guard-v1';saved.mkdir(exist_ok=False)
for name in['tests.log','run.exit','SOURCE_FREEZE.json','source.patch','zero_carry.rs']:shutil.copyfile(r/name,saved/name)
p=t/'src/point_add/zero_carry.rs';before=p.read_bytes();needle=b'fixture(n,pattern,&ds,false,true,0xA5963C78F012DE4B,None);';assert before.count(needle)==1
after=before.replace(needle,needle+b'fixture(n,pattern,&ds,false,true,u64::MAX,None);');assert before.split(b'#[cfg(test)]')[0]==after.split(b'#[cfg(test)]')[0]
p.write_bytes(after);(r/'zero_carry-v2.rs').write_bytes(after);f['source_files']={p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()}
f['additional_test']='Every enumerated basis input now also runs with all classical lanes enabled, in addition to the original mixed guard. Runtime prefix unchanged.'
(r/'SOURCE_FREEZE-v2.json').write_text(json.dumps(f,indent=2)+'\n');(r/'source-v2.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
