import json,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent
assert (r/'run.exit').read_text().strip()=='0'
assert json.loads((ws/'product-copy-cache-proof-20261020/TRANSFER.json').read_text())['status']=='COPY_CACHE_VALUE_PHASE_AND_PHYSICAL_RNG_TRANSFER_AUDIT_PASS'
assert (ws/'product-classical-twelve-operational-20261019/control.exit').read_text().strip()=='0','Finish the existing qualified source12 control first'
control_pid=int((ws/'product-classical-twelve-operational-20261019/control.pid').read_text())
for _ in range(100):
    p=Path('/proc')/str(control_pid)/'status'
    if not p.exists() or next(x.split()[1] for x in p.read_text().splitlines() if x.startswith('State:'))=='Z':break
    time.sleep(.05)
else:raise RuntimeError('Recorded control manager still live; preserve it and inspect, do not restart')
assert not (r/'gate.pid').exists() and not (r/'qualification').exists()
assert b'\r' not in (r/'run-gate.sh').read_bytes()
with (r/'gate-nohup.log').open('xb') as f:p=subprocess.Popen(['nohup','bash','run-gate.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'gate.pid').write_text(str(p.pid)+'\n');print(json.dumps({'pid':p.pid,'job':'sole declared reversible-copy-cache failure-rate gate'}))
