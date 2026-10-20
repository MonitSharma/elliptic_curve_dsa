"""Exact finite phase model for the remaining helper; no native resource claim."""
import collections,hashlib,itertools,json,time
from pathlib import Path
r=Path(__file__).resolve().parent;start=time.time();d=json.loads((r/'PREFIX-DAG.json').read_bytes());old=r.parent/'breakthrough-live-core-rank-20261020';f={k:int(v,16)for k,v in json.loads((old/'FUNCTIONS.json').read_bytes()).items()};values=[f['one']]+[f['input'+str(i)]for i in range(14)]
def truth(mask):
 v=0
 while mask:
  bit=mask&-mask;v^=values[bit.bit_length()-1];mask^=bit
 return v
for _,a,b in d['gates']:values.append(truth(a)&truth(b))
def basisof(seq):
 basis={};chosen=[]
 for mask in seq:
  v=mask
  while v:
   h=v.bit_length()-1
   if h not in basis:basis[h]=v;chosen.append(mask);break
   v^=basis[h]
 return chosen
features=basisof([1]+[1<<(i+1)for i in range(6,14)]+d['low_sum_masks']+d['field_masks']+[d['c6_mask']]);assert len(features)==35
model=json.loads((r/'SCHEDULE-v2-original-forward-minimum.json').read_bytes());garbage=model['stages'][-1]['delayed_garbage'].copy()
for item in model['finishing']:garbage.remove(item['function_mask'])
assert len(garbage)==1;target=truth(garbage[0]);basis={};terms=[];fun=[truth(mask)for mask in features]
def add(v,coef):
 while v:
  h=v.bit_length()-1
  if h not in basis:basis[h]=(v,coef);return
  w,c=basis[h];v^=w;coef^=c
def reduce(v):
 coef=0
 while v:
  h=v.bit_length()-1
  if h not in basis:break
  w,c=basis[h];v^=w;coef^=c
 return v,coef
reports=[];witness=None
for degree in range(1,5):
 for ids in ([(0,)]if degree==1 else[])+list(itertools.combinations(range(1,len(features)),degree)):
  value=f['one']
  for i in ids:value&=fun[i]
  terms.append([features[i]for i in ids]);add(value,1<<(len(terms)-1))
 residual,coef=reduce(target);reports.append({'max_degree':degree,'features':len(terms),'rank':len(basis),'remaining_residual_weight':residual.bit_count()});print(reports[-1],flush=True)
 if not residual:
  witness=[t for i,t in enumerate(terms)if coef>>i&1];check=0
  for term in witness:
   value=f['one']
   for mask in term:value&=truth(mask)
   check^=value
  assert check==target;break
result={'status':'EXACT_FINITE_QUARTIC_PHASE_MODEL_ONLY','model_sha256':hashlib.sha256((r/'SCHEDULE-v2-original-forward-minimum.json').read_bytes()).hexdigest(),'target_mask':garbage[0],'reports':reports,'witness':witness,'witness_term_degrees':dict(collections.Counter(map(len,witness)))if witness else None,'seconds':time.time()-start,'scope':'All16384 assignments. Degree4 phase terms could use one temporary AND, a classically conditioned CCZ and exact HMR repair; native synthesis, allocation, component tests and full circuit evidence pending.'};(r/'QUARTIC-FINISH.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print({k:result[k]for k in ['status','witness_term_degrees','seconds']})
