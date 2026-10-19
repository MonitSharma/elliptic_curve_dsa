import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert (r/'last-carry.exit').read_text().strip()=='0'
assert not (r/'commute.pid').exists()
with (r/'commute.nohup.log').open('wb') as f:
    p=subprocess.Popen(['nohup','bash','run-commute.sh'],cwd=r,stdin=subprocess.DEVNULL,
        stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'commute.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'directory':str(r),'log':'commute.nohup.log'}))
