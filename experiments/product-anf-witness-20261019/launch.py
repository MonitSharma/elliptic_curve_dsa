import json,subprocess
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;assert not (r/'run.pid').exists() and not (r/'run.exit').exists()
assert (r.parent/'product-anf256-20261019/run.exit').read_text().strip()=='0'
assert (r.parent/'portable-rust-20261019/LOCAL-VERIFICATION.json').exists()
with (r/'nohup.log').open('xb') as f:p=subprocess.Popen(['nohup','bash','run.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'run.pid').write_text(str(p.pid)+'\n');(r/'LAUNCH.json').write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'pid':p.pid,'environment':'local WSL Ubuntu','compute_cores':1,'address_space_gib':12,'server_jobs_changed':False},indent=2)+'\n');print('Local exact current-wire witness job',p.pid)
