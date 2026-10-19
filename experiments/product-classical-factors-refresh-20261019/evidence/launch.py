import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert not (r/'run.pid').exists()
with (r/'nohup.log').open('wb') as f:
    p=subprocess.Popen(['nohup','bash','run.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'run.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'directory':str(r),'job':'current-source-classical-factor-refresh'}))
