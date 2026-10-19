import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert (r/'refined.exit').read_text().strip()=='0'
assert not (r/'last-carry.pid').exists()
with (r/'last-carry.nohup.log').open('wb') as f:
    p=subprocess.Popen(['nohup','bash','run-last-carry.sh'],cwd=r,stdin=subprocess.DEVNULL,
        stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'last-carry.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'directory':str(r),'log':'last-carry.nohup.log'}))
