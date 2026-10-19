import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert not (r/'watch.pid').exists()
assert json.loads((r/'PATH-CONTROL.json').read_text())['status']=='CLASSICAL12_FINALIZER_ALL_INPUT_PATHS_AND_HASHES_PASS'
with (r/'watch-nohup.log').open('xb') as f:
    p=subprocess.Popen(['nohup','python3','watch.py'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'watch.pid').write_text(str(p.pid)+'\n');print(json.dumps({'pid':p.pid,'job':'queue-only-classical12-final-audit-and-benchmark'}))
