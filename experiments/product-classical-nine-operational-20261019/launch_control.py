import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert (r/'prepare.exit').read_text().strip()=='0' and not (r/'control.pid').exists() and not (r/'control').exists()
with (r/'control-nohup.log').open('xb') as f:
    p=subprocess.Popen(['nohup','bash','run-control.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'control.pid').write_text(str(p.pid)+'\n');print(json.dumps({'pid':p.pid,'job':'classical9-2-thread-operational-prefix-control'}))
