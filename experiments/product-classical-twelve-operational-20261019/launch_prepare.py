import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent
assert (ws/'product-classical-twelve-native-20261019/gate.exit').read_text().strip()=='0'
assert (ws/'product-classical-twelve-filter-20261019/qualification.exit').read_text().strip()=='0'
assert not (r/'prepare.pid').exists() and not (r/'tool').exists()
with (r/'prepare-nohup.log').open('xb') as f:
    p=subprocess.Popen(['nohup','bash','run-prepare.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'prepare.pid').write_text(str(p.pid)+'\n');print(json.dumps({'pid':p.pid,'job':'qualified-classical12-operational-port-build-only'}))
