import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert not (r/'control.pid').exists()
with (r/'control-nohup.log').open('wb') as f:
    p=subprocess.Popen(['nohup','bash','run-control.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'control.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'directory':str(r),'job':'full-current-classical-factor-transcript-controls'}))
