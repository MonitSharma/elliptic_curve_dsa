import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;assert (r/'BUILD_PREPARED').exists() and not (r/'watch.pid').exists()
assert not (r/'QUALIFICATION-START.json').exists()
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
bound={p.name:sha(p) for p in r.iterdir() if p.suffix in ['.py','.sh']};(r/'WATCH_SOURCE.json').write_text(json.dumps(bound,indent=2)+'\n')
with (r/'watch-nohup.log').open('xb') as f:w=subprocess.Popen(['nohup','python3','after_gate.py'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'watch.pid').write_text(str(w.pid)+'\n');print(json.dumps({'watch_pid':w.pid,'new_source_nonce_tests_started':False,'wait_for':'sole copy-cache gate PASS and completed successful build'}))
