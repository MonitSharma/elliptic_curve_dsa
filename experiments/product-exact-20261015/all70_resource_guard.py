"""Conservative future-phase admission; record and wait, never stop other work."""
from pathlib import Path
import os,json,sys,time,socket
root=Path('/home/hclau/ecdsa_research');own=os.getpgrp();groups={};ignored={'bash','sh','sleep','sshd','taskset','time','timeout'}
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  pid=int(p.name);pg=os.getpgid(pid)
  if pg==own or p.stat().st_uid!=os.getuid():continue
  stat=(p/'stat').read_text().split(') ',1)[1].split();state=stat[0]
  if state=='Z':continue
  args=(p/'cmdline').read_bytes().split(b'\0');argv=[a.decode(errors='replace')for a in args if a];cwd=os.readlink(p/'cwd')
  if not(cwd.startswith(str(root))or any(str(root)in a for a in argv)):continue
  name=(p/'comm').read_text().strip();g=groups.setdefault(pg,{'pids':[],'cpus':set(),'threads':0,'compute_threads':0,'compute':False,'configured_workers':0})
  nt=len(list((p/'task').iterdir()));g['pids'].append({'pid':pid,'name':name,'state':state,'threads':nt});g['threads']+=nt
  if name not in ignored:g['cpus'].update(os.sched_getaffinity(pid));g['compute_threads']+=nt;g['compute']=True
  if name=='value_prefilter'and len(argv)>4 and argv[4].isdigit():g['configured_workers']+=int(argv[4])
  if name in ['failure_census','simd_census_v2']and len(argv)>5 and argv[5].isdigit():g['configured_workers']+=int(argv[5])
 except(FileNotFoundError,ProcessLookupError,PermissionError):continue
rows=[]
for pg,g in groups.items():
 if not g['compute']:continue
 budget=min(len(g['cpus']),g['configured_workers']if g['configured_workers']else g['compute_threads']);rows.append({'pgid':pg,'estimated_cpu_ceiling':budget,'affinity_count':len(g['cpus']),'threads_in_group':g['threads'],'compute_threads_in_group':g['compute_threads'],'configured_worker_count':g['configured_workers'],'processes':g['pids']})
requested=int(sys.argv[1]);reserve=requested*24*1024**3;available=int(next(x.split()[1]for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))*1024;used=sum(x['estimated_cpu_ceiling']for x in rows)
passed=socket.gethostname()=='LHC-104-070'and available>=100*1024**3+reserve and used+requested<=64
receipt={'checked_at_unix':time.time(),'hostname':socket.gethostname(),'phase_requested_workers':requested,'ecdsa_other_estimated_cpu_ceiling':used,'total_with_requested':used+requested,'maximum_research_cpu_ceiling':64,'available_memory_bytes':available,'reserved_own_phase_bytes':reserve,'per_process_address_limit_bytes':24*1024**3,'minimum_system_available_after_reservation_bytes':100*1024**3,'admitted':passed,'research_groups':rows,'other_jobs_modified':False}
with Path(sys.argv[2]).open('a')as out:out.write(json.dumps(receipt)+'\n')
print(json.dumps({k:v for k,v in receipt.items()if k!='research_groups'}),flush=True);sys.exit(0 if passed else 2)
