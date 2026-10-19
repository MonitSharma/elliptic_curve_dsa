"""Reserve worst-case search worker slots; use just one build job."""
import hashlib,json,os,socket,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;s=r.parent/'parent4-operational-sat-20261019'
assert socket.gethostname()=='LHC-104-070'
stream=r.parent/'product-pareto-20261019/parent/ops.bin'
assert hashlib.file_digest(stream.open('rb'),'sha256').hexdigest()=='99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683'
run=json.loads((s/'run-record.json').read_text());assert run['workers']==4 and run['threads_each']==14
workers={int((s/f'worker{i}.pid').read_text()) for i in range(4)}
parent=lambda pid:int(next(x.split()[1] for x in Path(f'/proc/{pid}/status').read_text().splitlines() if x.startswith('PPid:')))
allowed=workers|{int((s/'search.pid').read_text()),int((r.parent/'parent4-final-sat-20261019/watch.pid').read_text())}
allowed.update(parent(pid) for pid in workers)
pid=os.getpid()
while pid>1:allowed.add(pid);pid=parent(pid)
processes=subprocess.check_output(['ps','-u','hclau','-o','pid=,stat=,nlwp=,%cpu=,comm=','--sort=-%cpu'],text=True)
unknown=[]
for line in processes.splitlines():
    pid,state,threads,cpu,command=line.split(maxsplit=4)
    if state.startswith(('T','Z')) or int(pid) in allowed:continue
    try:cwd=Path(f'/proc/{pid}/cwd').resolve()
    except OSError:continue
    if str(cwd).startswith('/home/hclau/ecdsa_research'):unknown.append({'pid':int(pid),'state':state,'threads':int(threads),'command':command})
available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
record={'at_unix':time.time(),'available_memory_bytes':available,'load':os.getloadavg(),'process_snapshot':processes,
    'search_compute_threads':56,'search_worker_slots_including_waiting_mains':60,'build_jobs':1,'screen_threads':1,
    'known_idle_managers_and_ancestors':sorted(allowed-workers),'unknown_active_research':unknown,
    'admission_note':'Reserve worst-case worker slots rather than a transient /proc thread count; helper threads are repeatedly created/destroyed between windows.'}
print(json.dumps(record,indent=2),flush=True)
assert not unknown and available>160*1024**3
assert 60+record['build_jobs']<=64
assert os.getloadavg()[0]<len(os.sched_getaffinity(0))-8
