import json,os,socket,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;s=r.parent/'parent4-operational-sat-20261019'
assert socket.gethostname()=='LHC-104-070'
assert (s/'search.exit').read_text().strip()=='0'
assert json.loads((r/'ROOT_TERMINAL_AUDIT.json').read_text())['status']=='LOWEST_PASS_COMPLETE_JSONL_AUDIT_PASS'
memory=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
assert memory>=160*1024**3
processes=subprocess.check_output(['ps','-u','hclau','-o','pid=,stat=,nlwp=,%cpu=,comm=','--sort=-%cpu'],text=True)
assert os.getloadavg()[0]<len(os.sched_getaffinity(0))-12
print(json.dumps({'at_unix':time.time(),'hostname':socket.gethostname(),'memory_available_bytes':memory,'load_average':os.getloadavg(),
    'process_snapshot':processes,'build_threads':4,'census_threads':6,'library_threads':1},indent=2))
