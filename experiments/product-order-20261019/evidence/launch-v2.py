import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert (r/'run.exit').read_text().strip()=='1'
assert not (r/'tests.log').exists() and not (r/'run-v2.pid').exists()
with (r/'nohup-v2.log').open('wb') as f:
    p=subprocess.Popen(['nohup','bash','run-v2.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'run-v2.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'directory':str(r),'job':'one-build-thread-exact-scheduling'}))
