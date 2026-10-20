"""Can C6 leave the held field basis between its value uses? Exact14-input model."""
import itertools,json,hashlib,time
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-prefix-dag-20261020';froot=r.parent/'breakthrough-live-core-rank-20261020';d=json.loads((old/'PREFIX-DAG.json').read_bytes());f={k:int(v,16)for k,v in json.loads((froot/'FUNCTIONS.json').read_bytes()).items()};values=[f['one']]+[f['input'+str(i)]for i in range(14)]
def truth(mask):
 v=0
 while mask:
  b=mask&-mask;v^=values[b.bit_length()-1];mask^=b
 return v
for _,a,b in d['gates']:values.append(truth(a)&truth(b))
selected=json.loads((froot/'QUADRATIC-LOAN-REVERSE-MODEL.json').read_bytes())['selected_output_basis'];held=[d['c6_mask']if n=='c6'else d['field_masks'][int(n[5:])]for n in selected];assert held[-1]==d['c6_mask'];state=[1]+d['low_sum_masks']+[1<<(i+1)for i in range(6,14)]+held[:-1];fun=[truth(m)for m in state];basis={};terms=[];start=time.time()
def add(v,coef):
 while v:
  h=v.bit_length()-1
  if h not in basis:basis[h]=(v,coef);return
  w,c=basis[h];v^=w;coef^=c
for i,v in enumerate(fun):terms.append([i]);add(v,1<<(len(terms)-1))
for i,j in itertools.combinations(range(1,len(fun)),2):terms.append([i,j]);add(fun[i]&fun[j],1<<(len(terms)-1))
for i,j,k in itertools.combinations(range(1,len(fun)),3):terms.append([i,j,k]);add(fun[i]&fun[j]&fun[k],1<<(len(terms)-1))
v=truth(d['c6_mask']);coef=0
while v:
 h=v.bit_length()-1
 if h not in basis:break
 w,c=basis[h];v^=w;coef^=c
witness=None
if not v:
 witness=[term for i,term in enumerate(terms)if coef>>i&1];check=0
 for term in witness:
  x=f['one']
  for i in term:x&=fun[i]
  check^=x
 assert check==truth(d['c6_mask'])
result={'status':'C6_CUBIC_LOAN_MODEL_ONLY','all16384_assignments_verified':witness is not None,'cubic_terms':sum(len(t)==3 for t in witness)if witness else None,'phase_terms':witness,'remaining_held_helpers':19,'state_masks':state,'c6_mask':d['c6_mask'],'feature_rank':len(basis),'seconds':time.time()-start,'scope':'Separate degree3 query for exact C6 erasure using the14 low-sum/immutable input functions and19 other held output basis values. Model only; no ladder schedule, native phase test, point-add gate, nonce or record.'};(r/'CUBIC-RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
