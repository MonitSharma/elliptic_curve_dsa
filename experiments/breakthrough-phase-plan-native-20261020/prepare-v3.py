import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((r/'SOURCE_FREEZE-v2.json').read_text())
assert(r/'run-v2.exit').read_text().strip()=='101';assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
old=r/'failed-comment-spelling-v2';old.mkdir(exist_ok=False)
for p in[r/'SOURCE_FREEZE-v2.json',r/'source-v2.patch',r/'tests-v2.log',t/'src/point_add/phase_plan.rs']:shutil.copyfile(p,old/p.name)
p=t/'src/point_add/phase_plan.rs';raw=p.read_bytes();needle=b'// Retained carry erasure also peaks at kept + width - 1.';assert raw.count(needle)==1
p.write_bytes(raw.replace(needle,b'/* Retained carry erasure also peaks at kept + width - 1. */'))
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source-v3.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()};f['scope']+=' V3 fixes comment spelling only: v2 line comment accidentally hid the following m declaration, so no v2 native circuit was built.'
(r/'SOURCE_FREEZE-v3.json').write_text(json.dumps(f,indent=2)+'\n')
