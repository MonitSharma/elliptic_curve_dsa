"""Exact finite-model search for direct retained-form cleanup using CCZ phases."""
import hashlib,itertools,json,time
from pathlib import Path
r=Path(__file__).resolve().parent;f={k:int(v,16)for k,v in json.loads((r/'FUNCTIONS.json').read_bytes()).items()};one=f['one'];low=[f['input0']^f['input6'],f['input1']^f['input7']^f['c1'],f['input2']^f['input8']^f['c2'],f['input3']^f['c3'],f['input4']^f['c4']^f['k0'],f['input5']^f['c5']^f['k0']^f['k1']];f.update({f'sum{i}':v for i,v in enumerate(low)});start=time.time();reports=[]
for frame in ['fin0-written-sums','fin1-original-inputs']:
 base=[('one',one)]+([(f'input{i}',f[f'input{i}'])for i in range(6,14)]+[(f'sum{i}',v)for i,v in enumerate(low)]if frame.startswith('fin0')else[(f'input{i}',f[f'input{i}'])for i in range(14)])
 m=json.loads((r/('QUADRATIC-LOAN-REVERSE-MODEL.json'if frame.startswith('fin0')else'FIN1-MODEL.json')).read_bytes());remaining=[(n,f[n])for n in m['selected_output_basis']];erased=[]
 while remaining:
  options=[]
  for name,g in reversed(remaining):
   features=base+[(n,v)for n,v in remaining if n!=name];basis={};terms=[]
   def add(v,mask):
    while v:
     h=v.bit_length()-1
     if h not in basis:basis[h]=(v,mask);return
     w,b=basis[h];v^=w;mask^=b
   def reduce(v):
    mask=0
    while v:
     h=v.bit_length()-1
     if h not in basis:break
     w,b=basis[h];v^=w;mask^=b
    return v,mask
   for degree in [1,2,3]:
    candidates=[(0,)]if degree==1 else[]
    candidates+=list(itertools.combinations(range(1,len(features)),degree))
    for ids in candidates:
     value=one
     for i in ids:value&=features[i][1]
     terms.append([features[i][0]for i in ids]);add(value,1<<(len(terms)-1))
    residual,mask=reduce(g)
    if not residual:
     witness=[t for i,t in enumerate(terms)if mask>>i&1];check=0
     for t in witness:
      value=one
      for n in t:value&=f[n]
      check^=value
     assert check==g;options.append({'wire_function':name,'phase_terms':witness,'cubic_terms':sum(len(t)==3 for t in witness),'max_degree':degree});break
   if options and options[-1]['cubic_terms']==0:break
  if not options:break
  chosen=min(options,key=lambda x:(x['cubic_terms'],len(x['phase_terms'])));erased.append(chosen);remaining=[(n,v)for n,v in remaining if n!=chosen['wire_function']]
  print(frame,len(erased),chosen['wire_function'],'cubic',chosen['cubic_terms'],flush=True)
 reports.append({'frame':frame,'erased':len(erased),'unresolved':[n for n,v in remaining],'cubic_phase_terms':sum(x['cubic_terms']for x in erased),'witnesses':erased})
(r/'RETAINED-CUBIC-CLEANUP.json').write_bytes((json.dumps({'status':'EXACT_TRUTH_FUNCTION_MODEL_ONLY','functions_sha256':hashlib.sha256((r/'FUNCTIONS.json').read_bytes()).hexdigest(),'seconds':time.time()-start,'frames':reports,'scope':'All16384 truth assignments, deterministic greedy choice. Cubic phase count is not a native or full-circuit resource result. Phase repair may use classically conditioned CCZ; no native cleanup implementation or allocation proof yet. Failed residuals are finite search outcomes, not lower bounds.'},indent=2)+'\n').encode())
