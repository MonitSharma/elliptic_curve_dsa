"""Admit known recorded jobs; account for the corrected final verifier."""
import hashlib,json,os,socket,subprocess,time
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research');s=ws/'parent4-operational-sat-20261019'
assert socket.gethostname()=='LHC-104-070'
stream=ws/'product-pareto-20261019/parent/ops.bin'
assert hashlib.file_digest(stream.open('rb'),'sha256').hexdigest()=='99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683'
def live(pid):
    p=Path(f'/proc/{pid}/status')
    return p.exists() and not next(x.split()[1] for x in p.read_text().splitlines() if x.startswith('State:')).startswith('Z')
def parent(pid):return int(next(x.split()[1] for x in Path(f'/proc/{pid}/status').read_text().splitlines() if x.startswith('PPid:')))
table=[tuple(map(int,x.split())) for x in subprocess.check_output(['ps','-e','-o','pid=,ppid='],text=True).splitlines()]
def descendants(pid):
    found={pid}
    while True:
        n=len(found);found.update(p for p,pp in table if pp in found)
        if len(found)==n:return found
allowed=set();pid=os.getpid()
while pid>1:allowed.add(pid);pid=parent(pid)
own_ancestors=set(allowed)
active_workers=[];active_roots=[]
for search_name in ['parent4-operational-sat-20261019','product-classical-nine-operational-20261019']:
    search_root=ws/search_name;members=[]
    for lane in range(4):
        record=search_root/f'worker{lane}.pid'
        if not record.exists():continue
        p=int(record.read_text())
        if not live(p):continue
        assert Path(f'/proc/{p}/cwd').resolve()==search_root
        expected=search_root/'tool/target/release/value_prefilter'
        assert Path(f'/proc/{p}/exe').resolve()==expected.resolve()
        assert str(expected).encode() in Path(f'/proc/{p}/cmdline').read_bytes().split(b'\0')
        members.append(p);active_workers.append(p);allowed.update([p,parent(p)])
    record=search_root/'search.pid'
    if record.exists():
        p=int(record.read_text())
        if live(p):
            assert Path(f'/proc/{p}/cwd').resolve()==search_root
            allowed.add(p)
    if members:active_roots.append({'directory':str(search_root),'workers':members,'reserved_slots':15*len(members)})

registered=[];extra_slots=0
for directory,pidfile,slots in [
 ('parent4-final-sat-20261019','watch.pid',0),('parent4-final-sat-v2-20261019','watch.pid',0),
 ('parent4-final-sat-v2-20261019','final.pid',8),
 ('product-classical-factors-refresh-20261019','run.pid',1),
 ('product-classical-factors-refresh-20261019','control.pid',2),
 ('product-captured-factors-20261019','run.pid',1),
 ('product-captured-factors-20261019','control.pid',2),
 ('product-captured-factors-native-20261019','run.pid',1),
 ('product-classical-factors-native-20261019','run.pid',1),
 ('product-classical-type-probe-20261019','run.pid',1),
 ('product-classical-control-expression-20261019','run.pid',1),
 ('product-classical-nine-20261019','run.pid',1),
 ('product-classical-nine-proof-20261019','run.pid',1),
 ('product-classical-nine-20261019','gate.pid',3),
 ('product-classical-nine-20261019','gate-v2.pid',3),
 ('product-classical-nine-filter-20261019','build.pid',1),
 ('product-classical-nine-filter-20261019','watch.pid',0),
 ('product-classical-nine-filter-20261019','qualification.pid',3),
 ('product-classical-factors-wide-20261019','run-v2.pid',1),
 ('product-classical-nine-operational-20261019','prepare.pid',1),
 ('product-classical-twelve-native-20261019','run.pid',1),
 ('product-classical-twelve-native-20261019','gate.pid',3),
 ('rail-sx-20261019','run.pid',1),
 ('rail-sx-20261019','branch.pid',1),
 ('rail-sx-prefix-20261019','run.pid',1),
 ('scalar-window-20261019','run.pid',1),
 ('product-classical-twelve-proof-20261019','component.pid',1),
 ('classical9-final-20261019','watch.pid',0),
 ('classical9-final-20261019','final.pid',3),
 ('product-classical-twelve-proof-20261019','run.pid',1),
 ('product-classical-nine-operational-20261019','control.pid',3),
]:
    root=ws/directory;record=root/pidfile
    if not record.exists():continue
    p=int(record.read_text())
    if not live(p):continue
    cwd=Path(f'/proc/{p}/cwd').resolve()
    if cwd!=root and root not in cwd.parents:continue
    command=Path(f'/proc/{p}/cmdline').read_bytes().split(b'\0')
    expected={'run.pid':b'run.sh','control.pid':b'run-control.sh','watch.pid':b'watch.py','final.pid':b'run-final.sh','gate.pid':b'run-gate.sh','gate-v2.pid':b'run-gate-v2.sh','build.pid':b'run-build.sh','qualification.pid':b'run-qualify.sh','run-v2.pid':b'run-v2.sh','prepare.pid':b'run-prepare.sh','component.pid':b'run-component.sh','branch.pid':b'run-branch.sh'}[pidfile]
    if directory=='product-classical-nine-filter-20261019' and pidfile=='watch.pid':expected=b'after_gate.py'
    if expected not in command:continue
    members=descendants(p);allowed.update(members)
    if p not in own_ancestors:extra_slots+=slots
    registered.append({'directory':directory,'pidfile':pidfile,'pid':p,'reserved_slots':slots,'tree':sorted(members)})
processes=subprocess.check_output(['ps','-u','hclau','-o','pid=,stat=,nlwp=,%cpu=,comm=','--sort=-%cpu'],text=True)
unknown=[]
for line in processes.splitlines():
    p,state,threads,cpu,command=line.split(maxsplit=4)
    if state.startswith(('T','Z')) or int(p) in allowed:continue
    try:cwd=Path(f'/proc/{p}/cwd').resolve()
    except OSError:continue
    if str(cwd).startswith(str(ws)):unknown.append({'pid':int(p),'cwd':str(cwd),'command':command})
available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
own_slots=int(os.environ.get('RESEARCH_SLOTS','1'));reserved=15*len(active_workers)+extra_slots+own_slots
record={'at_unix':time.time(),'hostname':socket.gethostname(),'memory_available_bytes':available,'load_average':os.getloadavg(),
        'active_search_workers':active_workers,'active_search_roots':active_roots,'search_slots_including_worker_mains':15*len(active_workers),
        'other_recorded_job_slots':extra_slots,'own_job_slots':own_slots,'total_reserved_research_slots':reserved,
        'registered_jobs':registered,'unknown_active_research':unknown,'process_snapshot':processes}
print(json.dumps(record,indent=2),flush=True)
assert not unknown and reserved<=64 and available>192*1024**3
assert os.getloadavg()[0]<len(os.sched_getaffinity(0))-8
