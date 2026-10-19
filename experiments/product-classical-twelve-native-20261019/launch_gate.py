import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent
assert (r/'run.exit').read_text().strip()=='0'
assert (ws/'product-classical-twelve-proof-20261019/run.exit').read_text().strip()=='0'
assert (ws/'product-classical-nine-20261019/gate-v2.exit').exists(),'Existing classical9 gate still running; preserve it'
assert (ws/'product-classical-nine-filter-20261019/WATCH_RESULT.json').exists(),'Wait for existing gate-dependent validation to finish or refuse'
assert json.loads((ws/'product-classical-nine-operational-20261019/CONTROL.json').read_text())['status']=='CONTROL_ROWS_EQUAL_QUALIFIED_PREFIX'
assert not (r/'gate.pid').exists() and not (r/'qualification').exists()
assert b'\r' not in (r/'run-gate.sh').read_bytes()
with (r/'gate-nohup.log').open('xb') as f:
    p=subprocess.Popen(['nohup','bash','run-gate.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'gate.pid').write_text(str(p.pid)+'\n');print(json.dumps({'pid':p.pid,'job':'single-independent-planned-classical12-gate'}))
