import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert (r/'run.exit').read_text().strip()=='0' and not (r/'component.pid').exists()
with (r/'component-nohup.log').open('xb') as f:
    p=subprocess.Popen(['nohup','bash','run-component.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'component.pid').write_text(str(p.pid)+'\n');print(json.dumps({'pid':p.pid,'job':'component-only-valid-point-count-and-equality-control'}))
