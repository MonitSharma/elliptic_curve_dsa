import json,os,shutil,socket,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent
assert socket.gethostname()=='LHC-104-070'
assert (r/'prepare-v2.exit').read_text().strip()=='0'
assert json.loads((r/'CONTROL.json').read_text())['status']=='CONTROL_ROWS_EQUAL_QUALIFIED_PREFIX'
leader=json.loads((r/'PUBLIC-RECORD.json').read_text())['leader']
assert leader['id']=='9dc3798c-93e0-4da4-a6a9-37586737c4af','Public product parent changed; no search started'
memory=int(next(s.split()[1] for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:')))*1024
assert memory>=180*1024**3,'Insufficient memory headroom; no search started'
disk=shutil.disk_usage(r);assert disk.free>=150*1024**3,'Insufficient disk space for retained nonce evidence'
cpus=len(os.sched_getaffinity(0));loads=os.getloadavg()
text=subprocess.check_output(['ps','-u','hclau','-o','pid=,stat=,nlwp=,%cpu=,comm=','--sort=-%cpu'],text=True)
research=[]
for line in text.splitlines():
    fields=line.split(maxsplit=4)
    if len(fields)!=5:continue
    pid,state,nlwp,percent,comm=fields
    if int(pid)==os.getpid() or state.startswith(('T','Z')):continue
    try:cwd=Path(f'/proc/{pid}/cwd').resolve()
    except OSError:continue
    if str(cwd).startswith('/home/hclau/ecdsa_research'):
        research.append({'pid':int(pid),'state':state,'threads':int(nlwp),'cpu_percent':float(percent),'command':comm})
other_threads=sum(p['threads'] for p in research)
capacity=min(cpus-loads[0]-8,64-other_threads)
threads_each=min(14,int(capacity//4))
assert threads_each>=8,'Node too busy for this search; defer rather than oversubscribe'
candidate=r.parent/'product-pareto-20261019/candidate-parent4'
record={'hostname':socket.gethostname(),'at_unix':time.time(),'cpus':cpus,'load_average':loads,
    'memory_available_bytes':memory,'disk_free_bytes':disk.free,'other_active_research_processes':research,
    'threads_each':threads_each,'workers':4,'requested_search_threads':threads_each*4,
    'scheduler_available':shutil.which('squeue') is not None,'public_product_parent':leader['id'],
    'candidate_revision':subprocess.check_output(['git','-C',str(candidate),'rev-parse','HEAD'],text=True).strip(),
    'candidate_status':subprocess.check_output(['git','-C',str(candidate),'status','--short'],text=True),
    'process_snapshot':text}
print(json.dumps(record,indent=2))
