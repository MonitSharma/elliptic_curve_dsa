import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert (r/'PREPARE-V1-PATH-ERROR.json').exists()
assert not (r/'prepare-v2.pid').exists()
with (r/'prepare-v2.nohup.log').open('wb') as f:
    p=subprocess.Popen(['nohup','bash','run-prepare-v2.sh'],cwd=r,stdin=subprocess.DEVNULL,
        stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'prepare-v2.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'directory':str(r),'job':'prepare-v2'}))
