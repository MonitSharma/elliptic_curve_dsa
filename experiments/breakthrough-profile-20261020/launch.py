"""Launch a recorded diagnostic workload without holding the SSH session."""
import subprocess
import json
import os
import socket
from datetime import datetime, timezone
from pathlib import Path
r = Path(__file__).resolve().parent
assert not (r / 'run.pid').exists()
assert socket.gethostname() == 'LHC-104-070'
memory = Path('/proc/meminfo').read_text()
available_kib = int(next(line for line in memory.splitlines() if line.startswith('MemAvailable:')).split()[1])
assert available_kib > 100 * 1024 * 1024
(r / 'resource-preflight.json').write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),
    'hostname':socket.gethostname(),'cpus':os.cpu_count(),'mem_available_kib':available_kib,
    'uptime':subprocess.check_output(['uptime']).decode(),
    'processes':subprocess.check_output(['ps','-eo','pid,pcpu,pmem,args','--sort=-pcpu']).decode(),
    'build_threads':2,'library_threads':1,'memory_limit_gib':32},indent=2)+'\n')
with (r / 'nohup.log').open('xb') as log:
    p = subprocess.Popen(['nohup', 'bash', str(r / 'run.sh')], cwd=r,
                         stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                         start_new_session=True)
(r / 'run.pid').write_text(str(p.pid)+'\n')
print(p.pid)
