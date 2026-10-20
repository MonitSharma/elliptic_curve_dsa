"""Keep the failed fixture; declare its unused output spectator in metadata."""
import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive'
assert(r/'run.exit').read_text().strip()=='101'
failed=r/'failed-undeclared-spectator-v1';failed.mkdir(exist_ok=False)
for name in['phase_bridge.rs','SOURCE_FREEZE.json','tests.log','run.exit','source.patch','prepare.py']:shutil.copyfile(r/name,failed/name)
p=t/'src/point_add/phase_bridge.rs';before=p.read_bytes()
needle=b'        assert!(apply(&mut c,&b,&rows,comp,cin,output.then_some(out),indices));'
assert before.count(needle)==1
after=before.replace(needle,needle+b'\n        c.declare_qubit_register(&[out]); // Include the untouched output spectator in the fixture interface.')
assert before.split(b'#[cfg(test)]')[0]==after.split(b'#[cfg(test)]')[0]
p.write_bytes(after);(r/'phase_bridge-v2.rs').write_bytes(after)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((r/'SOURCE_FREEZE.json').read_text())
assert all(sha(t/p)==h for p,h in f['protected_files'].items())
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()}
f['repair']='Test-only register declaration includes an unused output spectator when no clean carry is allocated; runtime arithmetic and gate counts unchanged.'
(r/'SOURCE_FREEZE-v2.json').write_text(json.dumps(f,indent=2)+'\n')
try:
    with(r/'tests-v2.log').open('xb')as log:
        subprocess.run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','phase_bridge','--','--nocapture'],cwd=t,stdout=log,stderr=subprocess.STDOUT,check=True)
    assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
except BaseException:
    (r/'run-v2.exit').write_text('1\n');raise
else:(r/'run-v2.exit').write_text('0\n')
