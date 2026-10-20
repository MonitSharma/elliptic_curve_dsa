import json,subprocess,socket
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent
assert socket.gethostname()=='LHC-104-070'and not(r/'run-v3.pid').exists()
available=int(next(l for l in Path('/proc/meminfo').read_text().splitlines()if l.startswith('MemAvailable:')).split()[1]);assert available>100*1024*1024
(r/'resource-preflight.json').write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'mem_available_kib':available,'uptime':subprocess.check_output(['uptime']).decode(),'processes':subprocess.check_output(['ps','-eo','pid,pcpu,pmem,comm','--sort=-pcpu']).decode(),'build_threads':2,'library_threads':1,'memory_limit_gib':32},indent=2)+'\n')
with(r/'nohup-v3.log').open('xb')as log:p=subprocess.Popen(['nohup','bash',str(r/'run-v3.sh')],cwd=r,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(r/'run-v3.pid').write_text(str(p.pid)+'\n');print(p.pid)
