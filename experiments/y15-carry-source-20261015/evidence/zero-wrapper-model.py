"""Exact arithmetic design: keep both physical zero encodings outside nonzero oracles."""
from pathlib import Path
import json
rows=[]
for p in [5,7,11,17,31,61,127]:
 for operation in ['divide','multiply']:
  count=0
  for x in range(1,p):
   image=[]
   for original in range(p+1):
    y=original;z0=int(y==0);zp=int(y==p);z=z0^zp
    if zp:y^=p
    if z:y^=x if operation=='divide' else 1
    assert 0<y<p
    y=(y*pow(x,-1,p) if operation=='divide' else y*x)%p
    assert 0<y<p
    if z:y^=1 if operation=='divide' else x
    if zp:y^=p
    z0^=int(y==0);zp^=int(y==p)
    expected=original if original in (0,p) else ((original*pow(x,-1,p) if operation=='divide' else original*x)%p)
    assert (y,z0,zp)==(expected,0,0)
    image.append(y);count+=1
   assert sorted(image)==list(range(p+1))
  rows.append({'prime':p,'operation':operation,'cases':count,'permutations':p-1})
result={'status':'finite algebraic design only','score':None,'cases':sum(r['cases'] for r in rows),'rows':rows,'division_rule':'Map zero payload to denominator x, apply nonzero division, XOR 1 on flagged branch, restore physical p if needed, uncompute zero flags.','multiplication_rule':'Map zero payload to 1, apply nonzero multiplication, XOR x on flagged branch, restore physical p if needed, uncompute zero flags.','limitations':['Assumes nonzero x and a phase-correct oracle with canonical nonzero output.','No quantum implementation, resource count or production phase proof.','Actual seam and seed-fusion contracts require verification; disabling them has a cost.','Does not solve zero x in multiplication; that case requires point-level handling or another reversible contract.']}
(Path(__file__).resolve().parent/'zero-wrapper-model.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'cases':result['cases'],'status':result['status']}))
