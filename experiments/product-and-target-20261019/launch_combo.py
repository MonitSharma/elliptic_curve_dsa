import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
assert not (r/'combo.pid').exists()
with (r/'combo-nohup.log').open('wb') as f:
    p=subprocess.Popen(['nohup','bash','run-combo.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'combo.pid').write_text(str(p.pid)+'\n')
print(json.dumps({'pid':p.pid,'directory':str(r),'job':'integration-gated-combined-carry-peak-screen'}))
