import hashlib,itertools,json
from pathlib import Path
r=Path(__file__).resolve().parent;d=json.loads((r/'PREFIX-DAG.json').read_bytes());f={k:int(v,16)for k,v in json.loads((r.parent/'breakthrough-live-core-rank-20261020/FUNCTIONS.json').read_bytes()).items()};values=[f['one']]+[f['input'+str(i)]for i in range(14)]
def truth(mask):
 v=0
 while mask:
  bit=mask&-mask;v^=values[bit.bit_length()-1];mask^=bit
 return v
for _,a,b in d['gates']:values.append(truth(a)&truth(b))
basis={}
for i,v in enumerate(values):
 coef=1<<i
 while v:
  h=v.bit_length()-1
  if h not in basis:basis[h]=(v,coef);break
  w,c=basis[h];v^=w;coef^=c
 assert v,'Full source function basis must be independent'
x=json.loads((r/'PROTECTED-v2-c1+c2+c3+c4.json').read_bytes());triples=[term for z in x['finishing']for term in z['phase_terms']if len(term)==3];assert len(triples)==1;rows=[]
for a,b in itertools.combinations(triples[0],2):
 target=truth(a)&truth(b);v=target;coef=0
 while v:
  h=v.bit_length()-1
  if h not in basis:break
  w,c=basis[h];v^=w;coef^=c
 if not v:assert truth(coef)==target
 rows.append({'phase_factor_masks':[a,b],'linear_in_full_original_function_space':not bool(v),'native_coordinate_mask':coef if not v else None,'residual_weight':v.bit_count()})
(r/'AUXILIARY-MODEL.json').write_bytes((json.dumps({'status':'FINITE_EXACT_AUXILIARY_MODEL_ONLY','model_sha256':hashlib.sha256((r/'PROTECTED-v2-c1+c2+c3+c4.json').read_bytes()).hexdigest(),'triple':triples[0],'pairs':rows,'scope':'A matching auxiliary could be retained from the original function span without an extra AND, then erased by a quadratic phase. Scheduling, native synthesis and full circuit evidence remain pending.'},indent=2)+'\n').encode());print(rows)
