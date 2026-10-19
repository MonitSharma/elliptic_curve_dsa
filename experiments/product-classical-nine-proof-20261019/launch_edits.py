import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert (r/'run.exit').read_text().strip()=='0' and not (r/'edits.pid').exists()
with (r/'edits-nohup.log').open('xb') as f:
    p=subprocess.Popen(['nohup','bash','run-edits.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'edits.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'job':'independent-full-nine-edit-audit'}))
