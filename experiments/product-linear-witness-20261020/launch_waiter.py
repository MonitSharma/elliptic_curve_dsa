import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;assert not (r/'watch.pid').exists() and not (r/'run.pid').exists()
assert (r.parent/'product-linear-witness-controls-v2-20261020/LOCAL-VERIFICATION.json').exists()
bound={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in r.iterdir() if p.suffix in ['.py','.rs','.sh']};(r/'WATCH_SOURCE.json').write_text(json.dumps(bound,indent=2)+'\n')
with (r/'watch-nohup.log').open('xb') as f:p=subprocess.Popen(['nohup','python3','watch.py'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'watch.pid').write_text(str(p.pid)+'\n');print('Idle local linear-screen waiter',p.pid)
