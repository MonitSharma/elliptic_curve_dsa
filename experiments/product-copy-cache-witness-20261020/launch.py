import json,subprocess
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;assert not (r/'run.pid').exists()
assert (r.parent/'product-copy-cache-20261019/run.exit').read_text().strip()=='0'
with (r/'nohup.log').open('xb') as f:p=subprocess.Popen(['nohup','bash','run.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'run.pid').write_text(str(p.pid)+'\n');(r/'LAUNCH.json').write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'pid':p.pid,'local_cores':1,'address_space_gib':12},indent=2)+'\n');print(p.pid)
