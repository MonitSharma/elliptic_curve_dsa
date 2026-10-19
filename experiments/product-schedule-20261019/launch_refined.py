import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert (r/'combined-width-1230.json').exists()
assert not (r/'refined.pid').exists()
with (r/'refined.nohup.log').open('wb') as f:
    p=subprocess.Popen(['nohup','bash','run-refined.sh'],cwd=r,stdin=subprocess.DEVNULL,
        stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'refined.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'directory':str(r),'log':'refined.nohup.log'}))
