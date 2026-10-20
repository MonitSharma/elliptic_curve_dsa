import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((r/'SOURCE_FREEZE.json').read_text())
assert(r/'run.exit').read_text().strip()=='101';assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
old=r/'failed-comment-spelling-v1';old.mkdir(exist_ok=False)
for p in[r/'SOURCE_FREEZE.json',r/'source.patch',r/'tests.log',t/'src/point_add/width_composition.rs']:shutil.copyfile(p,old/p.name)
p=t/'src/point_add/width_composition.rs';raw=p.read_bytes();needle=b'// Exact plain mapped chunk in any arithmetic phase; outer boundary callbacks stay intact.';assert raw.count(needle)==1;p.write_bytes(raw.replace(needle,b'/* Exact plain mapped chunk in any arithmetic phase; outer boundary callbacks stay intact. */'))
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source-v2.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()};f['scope']+=' V1 comment spelling swallowed following declarations on the original compressed source line, causing E0425 before any circuit/test ran. V2 uses block comment only; intended policy/tests unchanged; preserve compiler failure.'
(r/'SOURCE_FREEZE-v2.json').write_text(json.dumps(f,indent=2)+'\n')
