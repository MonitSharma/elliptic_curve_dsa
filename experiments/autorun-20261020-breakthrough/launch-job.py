"""Resource-checked launcher restricted to the ECDSA research directory."""
import json,os,re,resource,socket,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
assert len(sys.argv)==4
directory,script,prefix=sys.argv[1:]
assert all(re.fullmatch(r'[a-zA-Z0-9_.-]+',v)for v in(directory,script,prefix))
ws=Path('/home/hclau/ecdsa_research');r=ws/directory
assert r.is_dir()and(r/script).is_file()and not(r/(prefix+'.pid')).exists()
assert socket.gethostname()=='LHC-104-070'
available=int(next(l for l in Path('/proc/meminfo').read_text().splitlines()if l.startswith('MemAvailable:')).split()[1]);assert available>100*1024*1024
(r/(prefix+'-resource-preflight.json')).write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'mem_available_kib':available,'uptime':subprocess.check_output(['uptime']).decode(),'processes':subprocess.check_output(['ps','-eo','pid,pcpu,pmem,args','--sort=-pcpu']).decode(),'threads_max':2,'library_threads':1,'memory_limit_gib':32},indent=2)+'\n')
env=os.environ.copy();env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',RAYON_NUM_THREADS='1',CARGO_BUILD_JOBS='2')
with(r/(prefix+'.log')).open('xb')as log:
 p=subprocess.Popen(['nohup','python3',str(r/script)],cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,preexec_fn=lambda:resource.setrlimit(resource.RLIMIT_AS,(32*1024**3,32*1024**3)))
(r/(prefix+'.pid')).write_text(str(p.pid)+'\n');print(p.pid)
