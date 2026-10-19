import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert (r/'run.exit').read_text().strip()=='0'
assert not (r/'combined.pid').exists()
(r/'borrow-v1.rs').write_bytes((r/'borrow.rs').read_bytes()) if not (r/'borrow-v1.rs').exists() else None
with (r/'combined.nohup.log').open('wb') as f:
    p=subprocess.Popen(['nohup','bash','run-combined.sh'],cwd=r,stdin=subprocess.DEVNULL,
        stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'combined.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'directory':str(r),'log':'combined.nohup.log'}))
