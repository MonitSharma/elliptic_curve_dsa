import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive';f=json.loads((r/'SOURCE_FREEZE-v4.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (r/'run-v4.exit').read_text().strip()=='0';assert all(sha(t/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();(r/'y15-tests-v4.rs').write_bytes(raw);a=b'32*u64::from(if guarded{guard_word.count_ones()}else{64})';b=b'11*u64::from(if guarded{guard_word.count_ones()}else{64})';assert raw.count(a)==1;raw=raw.replace(a,b);p.write_bytes(raw)
p=t/'src/point_add/core_loan_certificate.rs';(r/'certificate-v4.rs').write_bytes(p.read_bytes());p.write_bytes((r/'certificate-sparse.rs').read_bytes())
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in (t/'src/point_add').rglob('*')if p.is_file()};f['fixture_change']='After native32-AND roundtrip passes, replace regeneration witnesses by separately verified one-AND-per-helper identities, expected11. Same linear basis, HMR Clifford erasure, exhaustive inputs, guards, allocation reuse and uninterrupted control.'
(r/'SOURCE_FREEZE-v5.json').write_text(json.dumps(f,indent=2)+'\n');(r/'source-v5.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
