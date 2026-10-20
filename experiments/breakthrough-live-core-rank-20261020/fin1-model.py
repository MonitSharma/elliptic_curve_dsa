"""Prefix30 model: original fin1 omits c2 before the active field program."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;f={k:int(v,16)for k,v in json.loads((r/'FUNCTIONS.json').read_bytes()).items()};one=f['one'];base=[('one',one)]+[(f'input{i}',f[f'input{i}'])for i in range(14)];held=[(n,f[n])for n in list(f)[15:46]if n!='c2'];assert len(held)==30
class Basis:
 def __init__(self):self.b={}
 def add(self,v,c=0):
  while v:
   h=v.bit_length()-1
   if h not in self.b:self.b[h]=(v,c);return True
   w,d=self.b[h];v^=w;c^=d
  return False
 def reduce(self,v):
  c=0
  while v:
   h=v.bit_length()-1
   if h not in self.b:break
   w,d=self.b[h];v^=w;c^=d
  return v,c
b=Basis()
for n,v in base:b.add(v)
keep=[]
for n in [f'field{i}'for i in range(21)]+['c6']:
 if b.add(f[n]):keep.append((n,f[n]))
garbage=[]
for n,v in held:
 if b.add(v):garbage.append((n,v))
assert len(b.b)==45 and len(keep)==20 and len(garbage)==10
remaining=garbage.copy();witnesses=[]
while remaining:
 progress=False
 for name,g in reversed(remaining):
  features=base+keep+[(n,v)for n,v in remaining if n!=name];q=Basis();terms=[]
  for i,(n,v)in enumerate(features):
   terms.append([n]);q.add(v,1<<(len(terms)-1))
   for j in range(1,i):terms.append([features[j][0],n]);q.add(v&features[j][1],1<<(len(terms)-1))
  residual,mask=q.reduce(g)
  if not residual:
   terms=[t for i,t in enumerate(terms)if mask>>i&1];check=0
   for t in terms:
    v=one
    for n in t:v&=f[n]
    check^=v
   assert check==g
   witnesses.append({'function':name,'phase_terms':terms});remaining=[(n,v)for n,v in remaining if n!=name];progress=True;break
 if not progress:break
report={'status':'EXACT_TRUTH_FUNCTION_MODEL_ONLY','functions_sha256':hashlib.sha256((r/'FUNCTIONS.json').read_bytes()).hexdigest(),'prefix_live_helpers':30,'retained_helpers':20,'selected_output_basis':[n for n,v in keep],'garbage_basis':[n for n,v in garbage],'clifford_erasure_witnesses':witnesses,'unresolved':[n for n,v in remaining],'scope':'Original fin1 frame, c2 omitted; no native implementation or prefix30 width claim. All16384 truth assignments. Native peak and missing-carry phase repairs remain required.'};(r/'FIN1-MODEL.json').write_text(json.dumps(report,indent=2)+'\n');print('keep',[n for n,v in keep]);print('garbage',[n for n,v in garbage]);print('erased',[v['function']for v in witnesses],'unresolved',report['unresolved'])
