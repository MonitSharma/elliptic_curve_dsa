import subprocess,json,socket
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent
assert socket.gethostname()=='LHC-104-070' and not (r/'replay.pid').exists()
available=int(next(line for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:')).split()[1])
assert available>100*1024*1024
(r/'replay-resource-preflight.json').write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'mem_available_kib':available,'uptime':subprocess.check_output(['uptime']).decode(),'processes':subprocess.check_output(['ps','-eo','pid,pcpu,pmem,args','--sort=-pcpu']).decode(),'threads':2,'library_threads':1,'max_memory_gib':32},indent=2)+'\n')
with (r/'replay-nohup.log').open('xb') as log:
 p=subprocess.Popen(['nohup','bash',str(r/'run-replay.sh')],cwd=r,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(r/'replay.pid').write_text(str(p.pid)+'\n');print(p.pid)
