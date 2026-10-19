import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert (r/'trace.exit').read_text().strip()=='101'
assert not (r/'TRACE-CONTROL.json').exists() and not (r/'trace-v2.pid').exists()
with (r/'trace-v2.nohup.log').open('wb') as f:
    p=subprocess.Popen(['nohup','bash','run-trace-v2.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'trace-v2.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'directory':str(r),'job':'protected-simulator-transcript-control-iterator-fix'}))
