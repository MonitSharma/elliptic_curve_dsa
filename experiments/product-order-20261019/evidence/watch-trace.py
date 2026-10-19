import json,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent
while not (r/'run-v3.exit').exists():time.sleep(20)
assert (r/'run-v3.exit').read_text().strip()=='0','Primary source screen failed; no transcript control launched'
assert not (r/'trace.pid').exists()
with (r/'trace.nohup.log').open('wb') as f:
    p=subprocess.Popen(['nohup','bash','run-trace.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'trace.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'directory':str(r),'job':'protected-complete-physical-RNG-transcript-control'}))
