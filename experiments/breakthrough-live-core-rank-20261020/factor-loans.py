"""Factor verified quadratic phase witnesses; component model only."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;f={k:int(v,16)for k,v in json.loads((r/'FUNCTIONS.json').read_bytes()).items()};one=f['one']
f.update({f'sum{i}':v for i,v in enumerate([f['input0']^f['input6'],f['input1']^f['input7']^f['c1'],f['input2']^f['input8']^f['c2'],f['input3']^f['c3'],f['input4']^f['c4']^f['k0'],f['input5']^f['c5']^f['k0']^f['k1']])})
p=r/'QUADRATIC-LOAN-REVERSE-MODEL.json';report=json.loads(p.read_bytes());results=[]
for item in report['quadratic_phase_eliminations']:
 pairs=set();lin=set()
 def toggle(dst,key):
  if key in dst:dst.remove(key)
  else:dst.add(key)
 for term in item['phase_terms']:
  if len(term)==1:toggle(lin,term[0])
  else:toggle(pairs,tuple(sorted(term)))
 products=[]
 while pairs:
  vertices=set(x for pair in pairs for x in pair)
  row={v:{b if a==v else a for a,b in pairs if v in (a,b)}for v in vertices}
  x,y=min(pairs,key=lambda p:(len(row[p[0]])*len(row[p[1]]),p))
  left=row[y];right=row[x];products.append([sorted(left),sorted(right)])
  for a in left:
   for b in right:
    if a==b:toggle(lin,a)
    else:toggle(pairs,tuple(sorted((a,b))))
 def value(names):
  v=0
  for n in names:v^=f[n]
  return v
 actual=value(lin)
 for left,right in products:actual^=value(left)&value(right)
 assert actual==f[item['wire_function']]
 results.append({'wire_function':item['wire_function'],'products':products,'linear':sorted(lin),'and_count':len(products)})
out={'status':'EXACT_ALL_16384_TRUTH_FUNCTION_FACTORIZATIONS','functions_sha256':hashlib.sha256((r/'FUNCTIONS.json').read_bytes()).hexdigest(),'phase_model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'reconstruction_order':'reverse of erasure order','total_reconstruction_AND_products':sum(x['and_count']for x in results),'witnesses':results,'scope':'Polynomial model only. Each product can use one scratch output plus an existing parity pivot; alias and in-place basis-transform legality remain to be checked in a native circuit. No complete resource result.'}
(r/'FACTORED-LOANS.json').write_text(json.dumps(out,indent=2)+'\n');print([(x['wire_function'],x['and_count'])for x in results]);print('total',out['total_reconstruction_AND_products'])
