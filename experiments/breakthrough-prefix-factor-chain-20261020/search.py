"""Search the rank-minimal AND language by exact truth-function subspaces."""
import collections,hashlib,itertools,json,time
from pathlib import Path
r=Path(__file__).resolve().parent;dag=json.loads((r/'PREFIX-DAG.json').read_bytes());f={k:int(v,16)for k,v in json.loads((r/'FUNCTIONS.json').read_bytes()).items()};one=f['one'];values=[one]+[f['input'+str(i)]for i in range(14)]
def comb(mask,cols):
 out=0
 while mask:
  b=mask&-mask;out^=cols[b.bit_length()-1];mask^=b
 return out
for _,a,b in dag['gates']:values.append(comb(a,values)&comb(b,values))
case=json.loads((r/'WINDOWS.json').read_text())['cases'][0];assert case['original_ANDs']==5 and case['new_gate_budget']==case['required_nonlinear_rank']==4
boundary_masks=[1]+[1<<i for i in case['boundary_columns']];boundary=[comb(x,values)for x in boundary_masks];target_forms=case['output_forms'];targets=[comb(x,values)for x in target_forms];m=len(targets);started=time.time();seen=set();queue=collections.deque([((),[])]);history=[];success=None;timed_out=False
def canonical(rows):
 basis={}
 for x in rows:
  for p in sorted(basis,reverse=True):
   if x>>p&1:x^=basis[p]
  if x:
   p=x.bit_length()-1
   for k,v in list(basis.items()):
    if v>>p&1:basis[k]=v^x
   basis[p]=x
 return tuple(basis[p]for p in sorted(basis,reverse=True))
def rem(x,state):
 for row in state:
  if x>>(row.bit_length()-1)&1:x^=row
 return x
def add(basis,value,coef):
 while value:
  p=value.bit_length()-1
  if p not in basis:basis[p]=(value,coef);return
  v,c=basis[p];value^=v;coef^=c
def solve(basis,value):
 coef=0
 while value:
  p=value.bit_length()-1
  if p not in basis:return None
  v,c=basis[p];value^=v;coef^=c
 return coef
while queue and time.time()-started<900:
 state,path=queue.popleft()
 if state in seen:continue
 seen.add(state);cols=boundary+[comb(x,targets)for x in state];masks=boundary_masks+[comb(x,target_forms)for x in state];n=len(cols);base={}
 for i,x in enumerate(cols):add(base,x,1<<i)
 classes=sorted({rem(y,state)for y in range(1,1<<m)}-{0});found={};candidates=[];used=set()
 for _,a,b in dag['gates'][case['start']:case['end']]:
  for form in[a,b]:
   witness=solve(base,comb(form,values))
   if witness is not None and witness&~1:candidates.append(witness&~1)
 for weight in[1,2,3]:
  candidates.extend(sum(1<<i for i in ids)for ids in itertools.combinations(range(1,n),weight))
 count=0
 for aa in candidates:
  if aa in used:continue
  used.add(aa);av=comb(aa,cols);basis=base.copy();count+=1
  for j,bv in enumerate(cols[1:],1):add(basis,av&bv,1<<(n+j))
  for y in classes:
   if y in found:continue
   coef=solve(basis,comb(y,targets))
   if coef is None:continue
   linear=coef&((1<<n)-1);bb=coef>>n;assert bb and comb(linear,cols)^(av&comb(bb,cols))==comb(y,targets)
   step={'available_form_masks':masks,'target_combination':y,'target_form_mask':comb(y,target_forms),'linear':linear,'and_a':aa,'and_b':bb,'all16384_assignments_verified':True};found[y]=step;new=canonical(state+(y,));newpath=path+[step]
   if len(new)==m:success=newpath;break
   if new not in seen:queue.append((new,newpath))
  if success:break
  if time.time()-started>=900:timed_out=True;break
  if len(found)==len(classes):break
 history.append({'state':state,'depth':len(state),'factor_candidates_tried':count,'found_target_classes':list(found),'seconds_total':time.time()-started});(r/'PROGRESS.json').write_text(json.dumps({'states':len(seen),'queued':len(queue),'history':history},indent=2)+'\n');print(json.dumps(history[-1]),flush=True)
 if success or timed_out:break
status='EXACT_FOUR_AND_CHAIN_ALL16384_VERIFIED_NOT_NATIVE'if success else'BOUNDED_FACTOR_LANGUAGE_EXHAUSTED_NOT_LOWER_BOUND'if not queue and not timed_out else'TIME_LIMIT_INCOMPLETE'
result={'status':status,'case':case,'solution':success,'states_examined':len(seen),'history':history,'seconds':time.time()-started,'source_hashes':{n:hashlib.sha256((r/n).read_bytes()).hexdigest()for n in['PREFIX-DAG.json','FUNCTIONS.json','WINDOWS.json','search.py']},'scope':'At4 target-function rank and4 AND budget, every new AND must lie in the target-plus-boundary span. Enumerates these subspaces; searches one factor of sparse weight<=3 or existing available gate-control forms, the other factor and linear correction solved exactly. Any hit verified on full14-input truth domain. Finite restricted-language failure is not a full multiplicative-complexity lower bound. Native phase/workspace and complete point-add tests still required.'};(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(status,flush=True)
