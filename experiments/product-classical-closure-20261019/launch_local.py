import hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent
assert not (r/'run.pid').exists() and not (r/'run.exit').exists()
inputs=json.loads((r/'INPUTS.json').read_text())
assert all(hashlib.file_digest((r/p).open('rb'),'sha256').hexdigest()==h for p,h in inputs['hashes'].items())
available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
assert available>10*1024**3
cpu=min(os.sched_getaffinity(0))
with (r/'nohup.log').open('xb') as f:
    p=subprocess.Popen(['nohup','taskset','-c',str(cpu),'bash','run.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'run.pid').write_text(str(p.pid)+'\n')
(r/'LAUNCH.json').write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'pid':p.pid,'cpu':cpu,'available_memory_bytes':available,'address_space_limit_gib':12,'environment':'existing local WSL Ubuntu','server_jobs_changed':False},indent=2)+'\n')
print('Local single-core closure probe PID',p.pid)
