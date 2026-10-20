"""Exact 14-input Boolean model; storage schedules are not native resource results."""
import hashlib,itertools,json,time,os
from pathlib import Path
r=Path(__file__).resolve().parent;d=json.loads((r/'PREFIX-DAG.json').read_bytes());old=r.parent/'breakthrough-live-core-rank-20261020';f={k:int(v,16)for k,v in json.loads((old/'FUNCTIONS.json').read_bytes()).items()};start=time.time();values=[f['one']]+[f['input'+str(i)]for i in range(14)]
def truth(mask):
 v=0
 while mask:
  bit=mask&-mask;v^=values[bit.bit_length()-1];mask^=bit
 return v
for i,(_,a,b)in enumerate(d['gates']):
 assert a<1<<(15+i)and b<1<<(15+i);values.append(truth(a)&truth(b))
names=list(f)[15:46];assert len(names)==31
assert all(truth(mask)==f[n]for n,mask in zip(names,d['helper_masks']))
assert all(truth(mask)==f['field'+str(i)]for i,mask in enumerate(d['field_masks']))
low=[f['input0']^f['input6'],f['input1']^f['input7']^f['c1'],f['input2']^f['input8']^f['c2'],f['input3']^f['c3'],f['input4']^f['c4']^f['k0'],f['input5']^f['c5']^f['k0']^f['k1']]
assert[truth(m)for m in d['low_sum_masks']]==low and truth(d['c6_mask'])==f['c6']
def reduce(v,basis):
 while v:
  h=v.bit_length()-1
  if h not in basis:break
  v^=basis[h]
 return v
def independent(seq):
 basis={};chosen=[]
 for v in seq:
  w=reduce(v,basis)
  if w:basis[w.bit_length()-1]=w;chosen.append(v)
 return chosen,basis
desired=[1]+[1<<(i+1)for i in range(6,14)]+d['low_sum_masks']+d['field_masks']+[d['c6_mask']]
requirements=[]
for born in range(32):
 mask=(1<<(15+born))-1;req=[v&mask for v in desired]
 for _,a,b in d['gates'][born:]:req.extend([a&mask,b&mask])
 chosen,basis=independent(req);assert chosen[0]==1;requirements.append(chosen)
assert len(requirements[-1])==35
def quadratic_witness(target,features,max_degree=2):
 basis={};terms=[]
 def add(v,coef):
  while v:
   h=v.bit_length()-1
   if h not in basis:basis[h]=(v,coef);return
   w,c=basis[h];v^=w;coef^=c
 fun=[truth(m)for m in features]
 for i in range(len(features)):
  terms.append([features[i]]);add(fun[i],1<<(len(terms)-1))
 for i,j in itertools.combinations(range(1,len(features)),2):
  terms.append([features[i],features[j]]);add(fun[i]&fun[j],1<<(len(terms)-1))
 if max_degree>=3:
  for i,j,k in itertools.combinations(range(1,len(features)),3):
   terms.append([features[i],features[j],features[k]]);add(fun[i]&fun[j]&fun[k],1<<(len(terms)-1))
 v=truth(target);coef=0
 while v:
  h=v.bit_length()-1
  if h not in basis:return None
  w,c=basis[h];v^=w;coef^=c
 witness=[term for i,term in enumerate(terms)if coef>>i&1];check=0
 for term in witness:
  value=f['one']
  for m in term:value&=truth(m)
  check^=value
 assert check==truth(target);return witness
basis_strategy=os.environ.get('PREFIX_BASIS_STRATEGY','previous');erase_strategy=os.environ.get('PREFIX_ERASE_STRATEGY','minimum');assert basis_strategy in ['previous','original-forward','original-reverse'];assert erase_strategy in ['minimum','forward','reverse']
held=[1]+[1<<(i+1)for i in range(14)];reports=[];peak=14
for born in range(1,32):
 req=requirements[born];_,span=independent(held+[1<<(14+born)]);assert all(not reduce(v,span)for v in req)
 preferred=[m for m in d['helper_masks']if m<1<<(15+born)and not reduce(m,span)]if basis_strategy!='previous'else[]
 if basis_strategy=='original-reverse':preferred.reverse()
 full,_=independent(req+preferred+held+[1<<(14+born)]);garbage=full[len(req):];peak=max(peak,len(held));erasures=[]
 while garbage:
  choices=[]
  for g in garbage:
   features=req+[v for v in garbage if v!=g];w=quadratic_witness(g,features)
   if w is not None:choices.append((len(w),g,w))
  if not choices:break
  _,g,w=min(choices)if erase_strategy=='minimum'else choices[0]if erase_strategy=='forward'else choices[-1];garbage.remove(g);erasures.append({'function_mask':g,'phase_terms':w})
 held=req+garbage;reports.append({'born':born,'ideal_retained_physical_wires':len(req)-1,'before_erasure_physical_wires':len(full)-1,'retained_physical_wires':len(held)-1,'delayed_garbage':garbage.copy(),'erasures':erasures})
finishing=[];quad_final_helpers=len(held)-15
while garbage:
 choices=[]
 for g in garbage:
  features=req+[v for v in garbage if v!=g];w=quadratic_witness(g,features,3)
  if w is not None:choices.append((sum(len(t)==3 for t in w),len(w),g,w))
 if not choices:break
 _,_,g,w=min(choices);garbage.remove(g);finishing.append({'function_mask':g,'phase_terms':w,'cubic_terms':sum(len(t)==3 for t in w)})
held=req+garbage
result={'status':'EXACT_BOOLEAN_STORAGE_MODEL_ONLY','basis_strategy':basis_strategy,'erase_strategy':erase_strategy,'native_dag_sha256':hashlib.sha256((r/'PREFIX-DAG.json').read_bytes()).hexdigest(),'functions_sha256':hashlib.sha256((old/'FUNCTIONS.json').read_bytes()).hexdigest(),'all16384_assignments_verified':True,'original_prefix_helper_peak':31,'ideal_linear_projection_helper_peak':max(len(v)for v in requirements[:-1])-14,'greedy_quadratic_erasure_helper_peak':peak-14,'quadratic_only_final_helpers':quad_final_helpers,'final_helpers_after_cubic_attempt':len(held)-15,'finishing_cubic_terms':sum(x['cubic_terms']for x in finishing),'finishing':finishing,'stages':reports,'seconds':time.time()-start,'scope':'Native31-AND DAG and all fields/low sums match exact14-input truth functions. Linear projections and greedy phase-erasure model only; cubic finishing attempted explicitly. No native basis-change allocation, integrated arithmetic, complete benchmark, finalgate, nonce or scored gain.'};output='SCHEDULE-v2-'+basis_strategy+'-'+erase_strategy+'.json';assert not(r/output).exists();(r/output).write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps({k:v for k,v in result.items()if k not in ['stages','finishing']}))
