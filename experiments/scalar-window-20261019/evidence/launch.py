import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;assert not (r/'run.pid').exists()
# Launch only after the existing validator's immutable admission check.
q=ws/'product-classical-nine-filter-20261019';assert (q/'qualification.pid').exists()
pre=json.loads((q/'qualification-preflight.json').read_text());assert not pre['unknown_active_research']
with (r/'nohup.log').open('xb') as f:
    p=subprocess.Popen(['nohup','bash','run.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'run.pid').write_text(str(p.pid)+'\n');print(json.dumps({'pid':p.pid,'job':'isolated-exact-public-scalar-window-comparison'}))
