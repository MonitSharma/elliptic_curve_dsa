import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert (r/'run.exit').read_text().strip()=='0' and not (r/'controls.pid').exists()
with (r/'controls.nohup.log').open('wb') as f:
    p=subprocess.Popen(['nohup','bash','run-controls.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'controls.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'job':'both-combined-method-protected-transcript-controls'}))
