import hashlib,json,os,socket,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;stream=r.parent/'product-pareto-20261019/parent/ops.bin'
assert socket.gethostname()=='LHC-104-070'
assert hashlib.file_digest(stream.open('rb'),'sha256').hexdigest()=='99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683'
available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
assert available>160*1024**3
ps=subprocess.check_output(['ps','-u','hclau','-o','pid=,stat=,nlwp=,%cpu=,comm=','--sort=-%cpu'],text=True)
own=[]
for row in ps.splitlines():
    pid,state,threads,cpu,command=row.split(maxsplit=4)
    if state.startswith(('T','Z')) or int(pid)==os.getpid():continue
    try:cwd=Path(f'/proc/{pid}/cwd').resolve()
    except OSError:continue
    if str(cwd).startswith('/home/hclau/ecdsa_research'):own.append({'pid':int(pid),'threads':int(threads),'command':command})
assert sum(p['threads'] for p in own)+4<=66,'Research thread budget exceeded'
assert os.getloadavg()[0]<len(os.sched_getaffinity(0))-8
print(json.dumps({'at_unix':time.time(),'available_memory_bytes':available,'load':os.getloadavg(),'own_jobs':own,
    'process_snapshot':ps,'build_threads':4,'screen_threads':1,'scheduler_available':subprocess.run(['sh','-c','command -v squeue'],capture_output=True).returncode==0},indent=2))
