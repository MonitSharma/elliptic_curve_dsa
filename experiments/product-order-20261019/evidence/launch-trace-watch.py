import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert not (r/'trace-watch.pid').exists()
with (r/'trace-watch.log').open('wb') as f:
    p=subprocess.Popen(['nohup','python3','watch-trace.py'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'trace-watch.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'directory':str(r),'job':'wait-for-source-audit-then-physical-RNG-control'}))
