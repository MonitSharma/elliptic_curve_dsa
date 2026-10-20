import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive';f=json.loads((r/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (r/'run.exit').read_text().strip()=='101';assert all(sha(t/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();(r/'y15-tests-v1.rs').write_bytes(raw);a=b'32*(if guarded{guard_word.count_ones()}else{64})';b=b'32*u64::from(if guarded{guard_word.count_ones()}else{64})';assert raw.count(a)==1;raw=raw.replace(a,b);p.write_bytes(raw)
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in (t/'src/point_add').rglob('*')if p.is_file()};f['fixture_change']='Only Stats expected type u32->u64 compile repair. Runtime prefix/certificate unchanged.'
(r/'SOURCE_FREEZE-v2.json').write_text(json.dumps(f,indent=2)+'\n');(r/'source-v2.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
