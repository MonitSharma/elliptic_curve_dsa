"""Turn every retained policy failure into a valid independent curve-point pair."""
from pathlib import Path
import hashlib,json,sys
root=Path(sys.argv[1]);audit=json.loads((root/'independent-policy-v9.json').read_text(encoding='utf8'))
p=2**256-2**32-977;packets=[]
for flagged in audit['flagged']:
 dx=int(flagged['diagnosis']['reflected_dx'],16)
 for ox in range(10000):
  tx=(ox+dx)%p;orr=(ox**3+7)%p;trr=(tx**3+7)%p
  oy=pow(orr,(p+1)//4,p);ty=pow(trr,(p+1)//4,p)
  if oy*oy%p==orr and ty*ty%p==trr and ty and oy:
   oy=min(oy,p-oy);ty=min(ty,p-ty);break
 else:raise RuntimeError('No point pair found within the fixed bounded construction')
 assert (tx-ox)%p==dx and dx!=0
 slope=(ty-oy)*pow(dx,-1,p)%p;rx=(slope*slope-tx-ox)%p;ry=(slope*(tx-rx)-ty)%p
 assert ry*ry%p==(rx**3+7)%p
 packets.append(dict(shot=len(packets),independent_index=flagged['fixed_independent_index'],arithmetic_dx=f'{dx:064x}',target=[f'{tx:064x}',f'{ty:064x}'],offset=[f'{ox:064x}',f'{oy:064x}'],expected=[f'{rx:064x}',f'{ry:064x}'],scope='valid curve pair constructed from an already retained independent arithmetic failure; not an official validation packet'))
assert len(packets)==3
report=dict(scope='All three independent policy failures converted to valid secp256k1 curve pairs; no nonce or official packet alteration',audit_sha256=hashlib.sha256((root/'independent-policy-v9.json').read_bytes()).hexdigest(),packets=packets)
(root/'independent-curve-packet-v9.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print('INDEPENDENT_CURVE_CONSTRUCTION_PASS pairs=3 on_curve=True distinct_x=True expected_addition=True')
