"""Can the retained20 forms be measured away without restoring garbage?"""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;f={k:int(v,16)for k,v in json.loads((r/'FUNCTIONS.json').read_bytes()).items()};one=f['one'];low=[f['input0']^f['input6'],f['input1']^f['input7']^f['c1'],f['input2']^f['input8']^f['c2'],f['input3']^f['c3'],f['input4']^f['c4']^f['k0'],f['input5']^f['c5']^f['k0']^f['k1']];f.update({f'sum{i}':v for i,v in enumerate(low)})
m=json.loads((r/'QUADRATIC-LOAN-REVERSE-MODEL.json').read_bytes());base=[('one',one)]+[(f'input{i}',f[f'input{i}'])for i in range(6,14)]+[(f'sum{i}',v)for i,v in enumerate(low)];remaining=[(n,f[n])for n in m['selected_output_basis']];eliminated=[]
while remaining:
 progress=False
 for name,g in reversed(remaining):
  features=base+[(n,v)for n,v in remaining if n!=name];basis={};terms=[]
  def add(v,mask):
   while v:
    h=v.bit_length()-1
    if h not in basis:basis[h]=(v,mask);return
    w,b=basis[h];v^=w;mask^=b
  for i,(n,v)in enumerate(features):
   terms.append([n]);add(v,1<<(len(terms)-1))
   for j in range(1,i):terms.append([features[j][0],n]);add(v&features[j][1],1<<(len(terms)-1))
  residual=g;mask=0
  while residual:
   h=residual.bit_length()-1
   if h not in basis:break
   w,b=basis[h];residual^=w;mask^=b
  if not residual:
   witness=[t for i,t in enumerate(terms)if mask>>i&1];value=0
   for term in witness:
    v=one
    for n in term:v&=f[n]
    value^=v
   assert value==g
   eliminated.append({'wire_function':name,'phase_terms':witness});remaining=[(n,v)for n,v in remaining if n!=name];progress=True;break
 if not progress:break
report={'status':'EXACT_TRUTH_FUNCTION_MODEL_ONLY','functions_sha256':hashlib.sha256((r/'FUNCTIONS.json').read_bytes()).hexdigest(),'erased_retained_helpers':len(eliminated),'unresolved':[n for n,v in remaining],'phase_witnesses':eliminated,'scope':'All16384 source assignments; fixed written low-sum frame. No new arithmetic, phase repair Clifford only. Native and complete-fold validity pending.'};(r/'RETAINED-CLEANUP-MODEL.json').write_text(json.dumps(report,indent=2)+'\n');print('erased',len(eliminated),'unresolved',report['unresolved'])
