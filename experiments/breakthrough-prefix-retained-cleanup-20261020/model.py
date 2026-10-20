"""Exact retained-value matching and lifetime frontier on all14 inputs."""
import hashlib,itertools,json,re
from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'runtime-source.rs').read_text();one=(1<<16384)-1
inputs=[sum(1<<v for v in range(16384)if v>>i&1)for i in range(14)]
def form(q,mask):
 out=one if mask&1 else 0
 for i,v in enumerate(q):
  if mask>>(i+1)&1:out^=v
 return out
def pairs(s):return[(int(a),int(b))for a,b in re.findall(r'\((\d+),(\d+)\)',s)]
def phase(q,terms):
 out=0
 for a,b in terms:out^=(one if a==0 else q[a-1])&(one if b==0 else q[b-1])
 return out
stage_text=s[s.index('const STAGES:'):s.index('fn form(')];q=inputs.copy();erased=[];events=[];ng=0
for line in stage_text.splitlines():
 if not line.startswith('Stage{'):continue
 gate=re.search(r'gate:Some\(\((\d+),(\d+)\)\)',line)
 if gate:
  a,b=map(int,gate.groups());q.append(form(q,a)&form(q,b));ng+=1;events.append(('gate',None,len(q)-14))
 cx=re.search(r'cx:&\[(.*?)\],x:',line)
 for a,b in pairs(cx[1]):q[b]^=q[a]
 x=int(re.search(r'],x:(\d+),erase:',line)[1])
 for i in range(len(q)):
  if x>>i&1:q[i]^=one
 for at,terms in re.findall(r'Erase\{at:(\d+),terms:&\[(.*?)\]\}',line):
  at=int(at);value=q[at];assert value==phase(q,pairs(terms));erased.append(value);events.append(('erase',len(erased)-1,len(q)-14));q.pop(at)
assert ng==31 and len(erased)==11 and len(q)==34
matches=[];cleanup_events=[];cleanup=s[s.index('const CLEANUP:'):s.index('pub(super)fn finish(')];rebuilds=0;cleanup_erases=0
for line in cleanup.splitlines():
 if a:=re.match(r'CleanupStep::Cx\((\d+),(\d+)\)',line):i,j=map(int,a.groups());q[j]^=q[i]
 elif a:=re.match(r'CleanupStep::X\((\d+)\)',line):q[int(a[1])]^=one
 elif a:=re.match(r'CleanupStep::Rebuild\{at:(\d+),linear:(\d+),products:&\[(.*?)\]\}',line):
  at=int(a[1]);value=form(q,int(a[2]))
  for x,y in pairs(a[3]):value^=form(q,x)&form(q,y)
  hits=[i for i,t in enumerate(erased)if t==value];assert len(hits)==1;matches.append(hits[0]);q.insert(at,value);rebuilds+=1;cleanup_events.append(('rebuild',hits[0],len(q)-14))
 elif a:=re.match(r'CleanupStep::Erase\{at:(\d+),terms:&\[(.*?)\]\}',line):
  at=int(a[1]);assert q[at]==phase(q,pairs(a[2]));cleanup_events.append(('erase',None,len(q)-14));q.pop(at);cleanup_erases+=1
assert rebuilds==11 and cleanup_erases==31 and len(q)==14 and sorted(matches)==list(range(11))
assert q[6:]==inputs[6:]
frontier=[]
for k in range(12):
 choices=[]
 for ids in itertools.combinations(range(11),k):
  keep=sum(1<<i for i in ids);saved=0;peak=0;area=0
  for kind,index,n in events:
   peak=max(peak,n+saved);area+=saved
   if kind=='erase'and keep>>index&1:saved+=1
  assert saved==k
  for kind,index,n in cleanup_events:
   if kind=='rebuild'and keep>>index&1:saved-=1
   peak=max(peak,n+saved)
  assert saved==0;choices.append((peak,area,keep,ids))
 peak,area,mask,ids=min(choices);frontier.append({'retained':k,'mask':mask,'forward_erasure_ids':ids,'prefix_peak_helpers':peak,'held_through_ladder':20+k,'core_ANDs':42-k,'core_HMRs':42-k,'minimum_room_with_eight_ladder_wires':max(peak,28+k)})
result={'status':'EXACT_ALL16384_RETAINED_HELPER_MODEL_NOT_NATIVE','rebuild_to_forward_erasure':matches,'frontier':frontier,'forward_ANDs':31,'unretained_cleanup_ANDs':11,'forward_phase_coefficients_verified':11,'cleanup_phase_coefficients_verified':31,'source_sha256':hashlib.sha256((r/'runtime-source.rs').read_bytes()).hexdigest(),'model_sha256':hashlib.sha256((r/'model.py').read_bytes()).hexdigest(),'scope':'Each selected forward HMR/phase repair is omitted and that same physical value is kept outside the schedule, then reinserted at its exactly matching cleanup rebuild, omitting one AND and one HMR. All14-input value/phase functions match exactly. Lifecycle frontier minimizes peak then saved lifetime for each retained count. More held wires can increase complete ladder cost. Native exhaustive phase/ancilla controls and full raw resource grid still required; no circuit score or final gate.'};(r/'MODEL.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
