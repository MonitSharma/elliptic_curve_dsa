import json,resource,socket,subprocess
from datetime import datetime,timezone
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research')
assert socket.gethostname()=='LHC-104-070'
available=int(next(l for l in Path('/proc/meminfo').read_text().splitlines()if l.startswith('MemAvailable:')).split()[1]);assert available>100*1024*1024
for name,script,prefix in [('breakthrough-profile-20261020','verify-replay.py','original-control'),('breakthrough-cap-cost-20261020','continue-v2.py','continuation')]:
 r=ws/name;assert not(r/(prefix+'.pid')).exists()
 (r/(prefix+'-resource-preflight.json')).write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'mem_available_kib':available,'uptime':subprocess.check_output(['uptime']).decode(),'processes':subprocess.check_output(['ps','-eo','pid,pcpu,pmem,args','--sort=-pcpu']).decode(),'threads_max':2,'library_threads':1,'memory_limit_gib':32},indent=2)+'\n')
 with(r/(prefix+'.log')).open('xb')as log:
  p=subprocess.Popen(['nohup','python3',str(r/script)],cwd=r,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,
   preexec_fn=lambda:resource.setrlimit(resource.RLIMIT_AS,(32*1024**3,32*1024**3)))
 (r/(prefix+'.pid')).write_text(str(p.pid)+'\n');print(name,p.pid)
