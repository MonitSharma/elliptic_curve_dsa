import json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;assert not (r/'run.pid').exists() and not (r/'run.exit').exists()
available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024;assert available>10*1024**3
with (r/'nohup.log').open('xb') as f:p=subprocess.Popen(['nohup','bash','run.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'run.pid').write_text(str(p.pid)+'\n');(r/'LAUNCH.json').write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'pid':p.pid,'available_memory_bytes':available,'compute_cores':1,'address_space_gib':12,'server_jobs_changed':False},indent=2)+'\n');print('Local exact-cap11 job PID',p.pid)
