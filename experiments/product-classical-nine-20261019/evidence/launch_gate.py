import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert (r/'run.exit').read_text().strip()=='0'
assert not (r/'gate.pid').exists() and not (r/'qualification').exists()
with (r/'gate-nohup.log').open('xb') as f:
    p=subprocess.Popen(['nohup','bash','run-gate.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'gate.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'job':'single-final-predeclared-classical9-failure-gate'}))
