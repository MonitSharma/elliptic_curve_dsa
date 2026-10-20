"""Independent full augmented-column intersection and rank certificate."""
import hashlib,json,time
from pathlib import Path
r=Path(__file__).resolve().parent
def xor_columns(mask,cols):
 out=0
 for i,v in enumerate(cols):
  if mask>>i&1:out^=v
 return out
def eliminate(columns,tagged=False):
 basis={};kernel=[]
 for i,value in enumerate(columns):
  tag=1<<i
  while value:
   pivot=value.bit_length()-1
   if pivot not in basis:basis[pivot]=(value,tag);break
   other,coef=basis[pivot];value^=other;tag^=coef
  if not value:kernel.append(tag)
 return basis,kernel
def independent(columns):return[v for v,t in eliminate(columns)[0].values()]
def rank(columns):return len(eliminate(columns)[0])
d=json.loads((r/'PREFIX-DAG.json').read_text());f={k:int(v,16)for k,v in json.loads((r/'FUNCTIONS.json').read_text()).items()};original=[f['one']]+[f['input'+str(i)]for i in range(14)]
for _,a,b in d['gates']:original.append(xor_columns(a,original)&xor_columns(b,original))
required=[xor_columns(x,original)for x in d['field_masks']+d['low_sum_masks']+[d['c6_mask']]];result=json.loads((r/'RESULT.json').read_text());cases=json.loads((r/'INTERFACES.json').read_text())['cases'];receipts=[];start=time.time()
assert len(cases)==len(result['cases'])==63
required_helper_forms=[x>>15 for x in d['field_masks']+d['low_sum_masks']+[d['c6_mask']]]
assert rank(required_helper_forms)==25
parities={case['parity']for case in cases};assert len(parities)==63 and 0 not in parities and rank(list(parities))==6
assert all((p&x).bit_count()%2==0 for p in parities for x in required_helper_forms)
assert all(a^b in parities or a==b for a in parities for b in parities)
for index,case in enumerate(cases):
 universe=original[:15]+[xor_columns(x,original)for x in case['retained_helper_forms']];assert rank(universe)==45
 available=original[:15].copy();history=[]
 while True:
  products=[available[i]&available[j]for i in range(len(available))for j in range(i+1,len(available))];quadratics=available+products
  _,kernel=eliminate(universe+quadratics);lowmask=(1<<len(universe))-1
  intersections=[xor_columns(row&lowmask,universe)for row in kernel];new=independent(available+intersections);history.append(len(new))
  if len(new)==len(available):break
  available=new
 # Independent dimension formula certifies the fixed point, rather than
 # inferring it from a zero count in the original quotient implementation.
 intersection_rank=rank(quadratics)+rank(universe)-rank(quadratics+universe);assert intersection_rank==len(available)
 missing=[i for i,t in enumerate(required)if rank(available+[t])>len(available)];expected=result['cases'][index];assert len(available)==expected['rank']and missing==expected['unreachable_target_indices']and missing
 receipts.append({'case':index,'closure_rank':len(available),'intersection_rank_from_dimension_formula':intersection_rank,'missing_target_indices':missing,'rank_history':history})
verification={'status':'ALL63_EXACT_OBSTRUCTIONS_INDEPENDENTLY_REPRODUCED','cases':receipts,'seconds':time.time()-start,'source_hashes':{p:hashlib.sha256((r/p).read_bytes()).hexdigest()for p in['search.py','verify.py','RESULT.json','FUNCTIONS.json','PREFIX-DAG.json','INTERFACES.json']},'scope':'Only XOR/AND programs with every intermediate product function confined to the original46-dimensional truth-function span are excluded at<=30 ANDs. No unrestricted circuit lower bound, native circuit, or point-add score.'};(r/'INDEPENDENT-VERIFICATION.json').write_text(json.dumps(verification,indent=2)+'\n');print(verification['status'],verification['seconds'])
