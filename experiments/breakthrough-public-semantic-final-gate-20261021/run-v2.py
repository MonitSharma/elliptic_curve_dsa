import json,os,shutil,socket,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent
try:
 start=time.time();c=ws/'breakthrough-public-semantic-finished-20261021';d=ws/'breakthrough-public-semantic-finished-development-20261021'
 while not(c/'validation-v2.exit').exists()or not(d/'controller.exit').exists():assert time.time()-start<21600;time.sleep(2)
 assert(c/'validation-v2.exit').read_text().strip()=='0'and(d/'controller.exit').read_text().strip()=='0';assert socket.gethostname()=='LHC-104-070'and os.cpu_count()>=64;available=int(next(x for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')).split()[1]);assert available>100*1024*1024;(r/'census-resource-preflight.json').write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'cpus':os.cpu_count(),'mem_available_kib':available,'workers_total':16,'library_threads':1,'uptime':subprocess.check_output(['uptime']).decode(),'schedulers':{x:shutil.which(x)for x in['sbatch','qsub','bsub']},'processes':subprocess.check_output(['ps','-eo','pid,comm,pcpu,rss','--sort=-pcpu']).decode()},indent=2)+'\n');subprocess.run(['python3',str(r/'declare-v2.py')],cwd=r,check=True);subprocess.run(['python3',str(r/'census.py')],cwd=r,check=True);(r/'controller.exit').write_text('0\n')
except Exception:
 (r/'controller.exit').write_text('1\n');raise
