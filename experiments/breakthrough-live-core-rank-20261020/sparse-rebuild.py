"""Source-derived one-product regeneration for each of eleven loaned helpers."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;f={k:int(v,16)for k,v in json.loads((r/'FUNCTIONS.json').read_bytes()).items()};one=f['one'];a=[f[f'input{i}']for i in range(6)];e=[f[f'input{i}']for i in range(6,9)];nm=[f[f'input{i}']for i in range(9,12)]
low=[a[0]^e[0],a[1]^e[1]^f['c1'],a[2]^e[2]^f['c2'],a[3]^f['c3'],a[4]^f['c4']^f['k0'],a[5]^f['c5']^f['k0']^f['k1']];f.update({f'sum{i}':v for i,v in enumerate(low)})
phase=json.loads((r/'QUADRATIC-LOAN-REVERSE-MODEL.json').read_bytes());features=[('one',one)]+[(f'input{i}',f[f'input{i}'])for i in range(6,14)]+[(f'sum{i}',v)for i,v in enumerate(low)]+[(n,f[n])for n in phase['selected_output_basis']]
forms={
 'c1':(e[0],one^low[0],0),
 'c2':(low[1]^e[1],e[1]^f['c1'],f['c1']),
 'c3':(low[2]^e[2],e[2]^f['c2'],f['c2']),
 'c4':(f['c3'],one^low[3],0),
 'tt':(f['input12'],f['input13'],0),
 'r2':(nm[1]^f['r1'],a[1]^f['r1'],f['r1']),
 'r3':(nm[2]^f['r2'],a[2]^f['r2'],f['r2']),
 'y3':(f['input12']^f['input13']^f['tt'],low[3],0),
 'y4':(f['input13'],low[4],0),
 'c5':(low[4]^f['k0'],f['k0']^f['c4'],f['c4']),
 'y5':(f['tt'],low[5],0),
}
witnesses=[]
for item in reversed(phase['quadratic_phase_eliminations']):
 name=item['wire_function'];left,right,linear=forms[name];assert(left&right)^linear==f[name]
 basis={}
 for i,(n,v)in enumerate(features):
  mask=1<<i
  while v:
   h=v.bit_length()-1
   if h not in basis:basis[h]=(v,mask);break
   w,m=basis[h];v^=w;mask^=m
 def expression(v):
  mask=0
  while v:
   h=v.bit_length()-1;assert h in basis,(name,'missing available linear fanin');w,m=basis[h];v^=w;mask^=m
  return [n for i,(n,v)in enumerate(features)if mask>>i&1]
 witnesses.append({'wire_function':name,'products':[[expression(left),expression(right)]],'linear':expression(linear),'and_count':1})
 features.append((name,f[name]))
report={'status':'EXACT_ALL_16384_TRUTH_FUNCTION_FACTORIZATIONS','functions_sha256':hashlib.sha256((r/'FUNCTIONS.json').read_bytes()).hexdigest(),'phase_model_sha256':hashlib.sha256((r/'QUADRATIC-LOAN-REVERSE-MODEL.json').read_bytes()).hexdigest(),'reconstruction_order':'reverse of erasure order','total_reconstruction_AND_products':11,'witnesses':list(reversed(witnesses)),'scope':'One AND per helper using affine fanins of currently available transformed wires and written low sums. All16384 truth assignments checked; pending native controls. No whole point-add score.'}
(r/'SPARSE-REBUILD.json').write_text(json.dumps(report,indent=2)+'\n');print([(v['wire_function'],v['products'])for v in witnesses]);print('total AND products',11)
