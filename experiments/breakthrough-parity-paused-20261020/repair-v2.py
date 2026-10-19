"""Preserve compile failure; spell the test Z as supported CZ(q,q)."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive'
assert(r/'run.exit').read_text().strip()=='101'
failed=r/'failed-test-api-v1';failed.mkdir(exist_ok=False)
for name in['SOURCE_FREEZE.json','DERIVATION.json','tests.rs','parity_paused.rs','tests.log','run.exit','source.patch']:
    shutil.copyfile(r/name,failed/name)
p=t/'src/point_add/parity_paused.rs';old=p.read_bytes();assert old.count(b'b.z(out)')==1
new=old.replace(b'b.z(out)',b'b.cz(out,out)');assert old.split(b'#[cfg(test)]')[0]==new.split(b'#[cfg(test)]')[0]
p.write_bytes(new);(r/'parity_paused-v2.rs').write_bytes(new)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((r/'SOURCE_FREEZE.json').read_text());assert all(sha(t/p)==h for p,h in f['protected_files'].items())
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()}
f['repair']='Test consumer uses the supported CZ(q,q) spelling for Z; runtime arithmetic code byte-identical.'
(r/'SOURCE_FREEZE-v2.json').write_text(json.dumps(f,indent=2)+'\n')
try:
    with(r/'tests-v2.log').open('xb')as log:
        subprocess.run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','parity_paused','--','--nocapture'],cwd=t,stdout=log,stderr=subprocess.STDOUT,check=True)
    assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
except BaseException:
    (r/'run-v2.exit').write_text('1\n');raise
else:(r/'run-v2.exit').write_text('0\n')
