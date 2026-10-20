import json,os,shutil,socket,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent
try:
 start=time.time();c=ws/'breakthrough-groups-context-finished-20261020';d=ws/'breakthrough-groups-context-development-20261020'
 while not(c/'run.exit').exists()or not(d/'DEVELOPMENT-CONTROLLER.exit').exists():assert time.time()-start<7200;time.sleep(2)
 assert(c/'run.exit').read_text().strip()=='0'and(d/'DEVELOPMENT-CONTROLLER.exit').read_text().strip()=='0';assert socket.gethostname()=='LHC-104-070'and os.cpu_count()>=64;available=int(next(x for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')).split()[1]);assert available>100*1024*1024;(r/'census-resource-preflight.json').write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'cpus':os.cpu_count(),'mem_available_kib':available,'workers_total':16,'library_threads':1,'uptime':subprocess.check_output(['uptime']).decode(),'schedulers':{x:shutil.which(x)for x in['sbatch','qsub','bsub']},'processes':subprocess.check_output(['ps','-eo','pid,pcpu,pmem,args','--sort=-pcpu']).decode()},indent=2)+'\n');subprocess.run(['python3',str(r/'declare.py')],cwd=r,check=True);subprocess.run(['python3',str(r/'census.py')],cwd=r,check=True);(r/'controller.exit').write_text('0\n')
except Exception:
 (r/'controller.exit').write_text('1\n');raise
