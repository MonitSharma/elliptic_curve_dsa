"""Suspend only these two verified owned process trees; preserve live state."""
import os,signal,socket,json,time,hashlib
from pathlib import Path
from datetime import datetime,timezone
ws=Path('/home/hclau/ecdsa_research');assert socket.gethostname()=='LHC-104-070'
receipt=ws/'RESEARCH-BREAK-20261021-PAUSE.json';assert not receipt.exists(),'Already paused: inspect saved receipt, do not duplicate'
def proc(pid):
 p=Path('/proc')/str(pid);s=(p/'stat').read_text();tail=s[s.rindex(')')+2:].split();return {'pid':pid,'ppid':int(tail[1]),'pgid':int(tail[2]),'start_ticks':int(tail[19]),'state':tail[0],'cwd':str((p/'cwd').resolve()),'comm':(p/'comm').read_text().strip(),'uid':p.stat().st_uid}
allp={}
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  try:allp[int(p.name)]=proc(int(p.name))
  except(FileNotFoundError,ProcessLookupError,PermissionError):pass
jobs=[]
for name,pidname in [('breakthrough-public-semantic-nonce-20261021','run.pid'),('breakthrough-current-compact-grid-20261021','pipeline.pid')]:
 r=ws/name;pid=int((r/pidname).read_text());group=[]
 if pid in allp:
  argv=(Path('/proc')/str(pid)/'cmdline').read_bytes().split(b'\0')
  expected=str(r/('run.py'if pidname=='run.pid'else'server-run.py')).encode()
  assert argv[:3]==[b'python3',b'-u',expected],(pid,argv)
  assert allp[pid]['uid']==os.getuid()
  selected={pid};changed=True
  while changed:
   new={q for q,p in allp.items()if p['ppid']in selected};changed=not new<=selected;selected|=new
  for q in selected:
   assert allp[q]['uid']==os.getuid()and(q==pid or Path(allp[q]['cwd']).is_relative_to(r)),(name,allp[q])
  # Stop controller first to prevent spawning a new child during traversal.
  os.kill(pid,signal.SIGSTOP)
  for q in sorted(selected-{pid},reverse=True):
   try:os.kill(q,signal.SIGSTOP)
   except ProcessLookupError:pass
  time.sleep(.1)
  for q in sorted(selected):
   try:
    now=proc(q);assert now['start_ticks']==allp[q]['start_ticks'];assert now['state']in['T','t'],now;group.append(now)
   except FileNotFoundError:pass
 jobs.append({'experiment':name,'root_pid':pid,'status':'SIGSTOP_PAUSED_PRESERVE_IN_MEMORY_STATE'if group else'ALREADY_FINISHED','processes':group})
search=ws/'breakthrough-public-semantic-nonce-20261021/production.jsonl';data=search.read_bytes();rows=[];partial=0
for line in data.splitlines(keepends=True):
 try:rows.append(json.loads(line))
 except json.JSONDecodeError:partial+=len(line)
numbers={row['nonce']for row in rows};prefix=0
while prefix+1 in numbers:prefix+=1
report={'at_utc':datetime.now(timezone.utc).isoformat(),'hostname':socket.gethostname(),'reason':'Human explicitly requested stop and break; no new experiments or automatic resume.','jobs':jobs,'search_snapshot':{'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'complete_rows':len(rows),'unique_nonces':len(numbers),'complete_prefix':prefix,'highest_screened':max(numbers)if numbers else None,'passes':[row['nonce']for row in rows if row.get('pass')],'partial_tail_bytes_preserved':partial},'resume_policy':'Only on subsequent human resume. Recheck /proc start_ticks and cwd for EVERY saved PID before SIGCONT; never trust reused PID. Resume same search in memory, no duplicate search, label, circuit, nonce cap or policy changes. Original retired6192 search stays retired. Grid has GNU timeout child: after a long pause its real-time alarm may expire upon resume. Preserve that generation timeout as interruption; allow existing controller to record failure and continue fixed grid. Any retry of interrupted generation goes to separate evidence directory with same frozen source; no gate is involved. Never kill unrelated jobs or edit chemistry.'}
receipt.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
