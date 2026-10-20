"""Exact finite one-AND resynthesis search for the two costly rebuilds."""
import hashlib,itertools,json,shutil,time
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-prefix-dag-20261020';start=time.time();reports=[]
source=(r/'original-generate-native-cleanup.py').read_text().replace("r.parent/'breakthrough-live-core-rank-20261020'",'r');assert source.count('products=item[\'products\'];')==1
helper='''
def oneand(function,state,prior):
 started=time.time();fun=[truth(m) for m in state];n=len(fun);base={}
 def add(basis,v,coef):
  while v:
   h=v.bit_length()-1
   if h not in basis:basis[h]=(v,coef);return None
   w,c=basis[h];v^=w;coef^=c
  return coef
 for i,v in enumerate(fun):assert add(base,v,1<<i) is None
 target=truth(function);tried=0;seen=set();hit=None
 # Include all factor forms in the existing exact two-product witness first.
 candidates=[x for pair in prior for x in pair]
 candidates+=list(range(1,1))
 for weight in [1,2,3]:
  for bits in itertools.combinations(range(1,n),weight):candidates.append(sum(1<<i for i in bits))
 for aa in candidates:
  if aa in seen or not aa:continue
  seen.add(aa);av=value_of(aa,state);basis=base.copy();tried+=1
  for j,bv in enumerate(fun):add(basis,av&bv,1<<(n+j))
  v=target;coef=0
  while v:
   h=v.bit_length()-1
   if h not in basis:break
   w,c=basis[h];v^=w;coef^=c
  if not v:
   li=coef&((1<<n)-1);bb=coef>>n;assert value_of(li,state)^(av&value_of(bb,state))==target
   hit={'linear':li,'products':[(aa,bb)]};break
 result={'function_mask':function,'state':state.copy(),'old_products':prior,'candidates_tried':tried,'seconds':time.time()-started,'hit':hit,'domain_assignments':16384,'scope':'Finite sparse-affine one-AND factor search; exact truth verification, not a minimum-AND lower bound or native result.'};reports.append(result);(r/'SEARCH-PROGRESS.json').write_text(json.dumps(reports,indent=2)+'\\n');print('oneand',function,tried,'hit',bool(hit),flush=True)
 return hit
'''
needle='for rec in reversed(records):';assert source.count(needle)==1;source=source.replace(needle,helper+'\n'+needle)
needle="products=item['products'];";source=source.replace(needle,"products=item['products'];\n  if len(products)>1:\n   best=oneand(item['function'],current,products)\n   if best:item=dict(item,linear=best['linear']);products=best['products']\n  ")
ns={'__file__':str(r/'instrumented-cleanup.py'),'time':time,'itertools':itertools,'reports':reports};(r/'instrumented-cleanup.py').write_text(source);exec(compile(source,str(r/'instrumented-cleanup.py'),'exec'),ns)
(r/'SEARCH-RESULT.json').write_text(json.dumps({'status':'FINITE_EXACT_FACTOR_SEARCH_NOT_NATIVE','seconds':time.time()-start,'rebuilds':reports,'cleanup':json.loads((r/'CLEANUP-GENERATION.json').read_text()),'original_generator_sha256':hashlib.sha256((r/'original-generate-native-cleanup.py').read_bytes()).hexdigest()},indent=2)+'\n')
(r/'run.exit').write_text('0\n')
