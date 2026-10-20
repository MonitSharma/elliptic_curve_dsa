"""Codimension-one interfaces containing every required active-prefix output."""
import itertools,json,hashlib
from pathlib import Path
r=Path(__file__).resolve().parent;dpath=r.parent/'breakthrough-prefix-dag-20261020/PREFIX-DAG.json';d=json.loads(dpath.read_bytes());rows=[x>>15 for x in d['low_sum_masks']+d['field_masks']+[d['c6_mask']]];basis={}
for x in rows:
 while x:
  p=x.bit_length()-1
  if p not in basis:basis[p]=x;break
  x^=basis[p]
pivots=set(basis);free=[i for i in range(31)if i not in pivots];null=[]
for q in free:
 x=1<<q
 for p in sorted(pivots):
  if(basis[p]&x).bit_count()%2:x|=1<<p
 assert all((x&row).bit_count()%2==0 for row in rows);null.append(x)
assert len(null)==11;all_vectors=[]
for mask in range(1,1<<len(null)):
 x=0
 for i,v in enumerate(null):
  if mask>>i&1:x^=v
 all_vectors.append(x)
all_vectors.sort(key=lambda x:(x.bit_count(),x));cases=[]
for parity in all_vectors[:12]:
 missing=[i for i in range(31)if parity>>i&1];pivot=missing[0];forms=[1<<i for i in range(31)if i!=pivot and not(parity>>i&1)]+[(1<<pivot)^(1<<i)for i in missing[1:]];assert len(forms)==30 and all((x&parity).bit_count()%2==0 for x in forms)
 cases.append({'parity':parity,'support':missing,'weight':len(missing),'retained_helper_forms':[x<<15 for x in forms],'new_gate_budget':30,'original_ANDs':31})
report={'status':'DECLARED_GLOBAL_FUSION_INTERFACES_NOT_CIRCUITS','dag_sha256':hashlib.sha256(dpath.read_bytes()).hexdigest(),'required_helper_rank':len(basis),'dual_dimension':len(null),'all_hyperplanes':len(all_vectors),'weight_histogram':{str(w):sum(x.bit_count()==w for x in all_vectors)for w in range(1,32)if any(x.bit_count()==w for x in all_vectors)},'cases':cases,'scope':'First12 codimension-one hyperplanes ordered by sparse algebraic support, all containing every required low-sum/field/C6 function modulo inputs. Seek30 ANDs within each retained span; no packet/census information.'};(r/'INTERFACES.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'weights':report['weight_histogram'],'cases':[{k:v for k,v in x.items()if k!='retained_helper_forms'}for x in cases]},indent=2))
