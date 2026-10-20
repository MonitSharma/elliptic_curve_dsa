"""Source-function workspace model; never a scored circuit or input census."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent
f={k:int(v,16) for k,v in json.loads((r/'FUNCTIONS.json').read_bytes()).items()}
one=f['one'];a=[f[f'input{i}'] for i in range(6)];e=[f[f'input{i}'] for i in range(6,9)]
low=[a[0]^e[0],a[1]^e[1]^f['c1'],a[2]^e[2]^f['c2'],a[3]^f['c3'],a[4]^f['c4']^f['k0'],a[5]^f['c5']^f['k1']^f['k0']]
inputs=[one]+[f[f'input{i}'] for i in range(6,14)]+low
outputs=[f[f'field{i}'] for i in range(21)]+[f['c6']]
held=[(k,v) for k,v in f.items() if k not in ['one'] and not k.startswith(('input','field','k')) or k=='k7']
assert len(held)==31,len(held)
class Basis:
 def __init__(self):self.b={}
 def add(self,v,c=0):
  while v:
   h=v.bit_length()-1
   if h not in self.b:self.b[h]=(v,c);return True
   w,d=self.b[h];v^=w;c^=d
  return False
 def reduce(self,v,c=0):
  while v:
   h=v.bit_length()-1
   if h not in self.b:break
   w,d=self.b[h];v^=w;c^=d
  return v,c
b=Basis()
for v in inputs:b.add(v)
input_rank=len(b.b);keep=[]
for i,v in enumerate(outputs):
 if b.add(v):keep.append(('field'+str(i) if i<21 else 'c6',v))
desired_rank=len(b.b);garbage=[]
for name,v in held:
 if b.add(v):garbage.append((name,v))
assert len(b.b)==46
rows=[];remaining=garbage.copy();eliminated=[]
while remaining:
 progress=False
 for name,g in reversed(remaining):
  features=[('one',one)]+[(f'input{i+6}',f[f'input{i+6}'])for i in range(8)]+[(f'sum{i}',v)for i,v in enumerate(low)]+keep+[(n,v)for n,v in remaining if n!=name]
  q=Basis();terms=[]
  for i,(n,v)in enumerate(features):
   terms.append([n]);q.add(v,1<<(len(terms)-1))
   for j in range(1,i):
    terms.append([features[j][0],n]);q.add(v&features[j][1],1<<(len(terms)-1))
  residual,mask=q.reduce(g)
  if residual==0:
   witness=[t for i,t in enumerate(terms)if mask>>i&1];check=0
   lookup=dict(features)
   for term in witness:
    v=one
    for n in term:v&=lookup[n]
    check^=v
   assert check==g
   eliminated.append({'wire_function':name,'phase_terms':witness,'quadratic_terms':sum(len(t)==2 for t in witness),'features':len(features)})
   remaining=[(n,v)for n,v in remaining if n!=name];progress=True;break
 if not progress:break
report={'status':'EXACT_TRUTH_FUNCTION_MODEL_ONLY','functions_sha256':hashlib.sha256((r/'FUNCTIONS.json').read_bytes()).hexdigest(),'input_rank_after_low_sums':input_rank,'desired_rank':desired_rank,'selected_output_basis':[n for n,v in keep],'additional_live_helpers':len(keep),'garbage_basis':[n for n,v in garbage],'quadratic_phase_eliminations':eliminated,'unresolved':[n for n,v in remaining],'scope':'All16384 source assignments, linear basis changes and HMR repair polynomials only; no native implementation, lifecycle or full point-add resource result.'}
(r/'QUADRATIC-LOAN-REVERSE-MODEL.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['quadratic_phase_eliminations','scope']},indent=2));print('eliminated',[(v['wire_function'],v['quadratic_terms'])for v in eliminated])
