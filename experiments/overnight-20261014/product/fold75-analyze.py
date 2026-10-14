"""Unlimited integer producer and independent modular fold/rotation value checks."""
from pathlib import Path
import collections,json,re,sys
p=2**256-2**32-977;mask=2**256-1
rows=[]
for line in Path(sys.argv[1]).read_text().splitlines():
 if line.startswith('PRODUCT_FOLD_FRAME '):rows.append(dict(re.findall(r'(\w+)=(\S+)',line)))
assert len(rows)==256
groups=collections.defaultdict(list)
for r in rows:groups[(r['source'],r['mode'],r['index'],r['t'])].append(r)
proofs=[]
for key,rs in groups.items():
 assert [r['label']for r in rs]==['entry','before-fold-producer','after-fold-producer','after-ripple-close']
 a,pre,fold,close=rs;T=int(a['p0'],16);B=int(a['p1'],16);letter=a['letter'];assert len(letter)==5
 signs=[int(i)for i in letter[:3]];nm=sum(s*2**i for i,s in enumerate(signs));coeff=sum((1-2*s)*2**i for i,s in enumerate(signs));shift=3+int(letter[3])+2*int(letter[4])
 unsigned=T+sum((B if not s else mask-B)*2**i for i,s in enumerate(signs))
 expected_y=(T+coeff*B)*pow(2**shift,-1,p)%p
 rolled=((expected_y<<shift)|(expected_y>>(256-shift)))&mask
 actual_unsigned=int(pre['open_x'],16)+(int(pre['overflow'],16)<<256)
 details=[]
 for r in rs:
  physB=int(r['p1'],16);decodedB=physB^(mask if r['b_complemented']=='true'and signs[2]else 0)
  details.append(dict(stage=r['label'],old_end=int(r['old_end']),final_end=int(r['final_end']),source_preserved=decodedB==B,logical_target=hex(int(r['open_x'],16)),physical_target=r['p0'],overflow=r['overflow'],pending_y33=int(r['pending_y33']),open_ripple=r['open_ripple']=='true'))
 proof=dict(source=key[0],mode=key[1],index=int(key[2]),tick=int(key[3]),letter=letter,rotation_shift=shift,source_sign_word=nm,
  expected_unsigned_add2=hex(unsigned),actual_unsigned_add2=hex(actual_unsigned),producer_exact=actual_unsigned==unsigned,
  expected_unrotated_word=hex(rolled),actual_postfold_word=fold['open_x'],postfold_exact=int(fold['open_x'],16)==rolled,
  actual_closed_word=close['open_x'],closed_exact=int(close['open_x'],16)==rolled,
  postfold_delta=(int(fold['open_x'],16)-rolled),close_delta=(int(close['open_x'],16)-rolled),
  source_preserved_all=all(s['source_preserved']for s in details),details=details)
 proofs.append(proof)
doc=dict(status='FINITE_SOURCE_BOUND_INTERNAL_FOLD_DIAGNOSTIC',qualified_score=None,producer_cases=len(proofs),
 rule='Unfolded unsigned X=T+sum(2^j*(B xor s_j*(2^256-1))). Exact field result=(T+sum(2^j*(-1)^s_j*B))*inverse(2^(3+k1+2*k2)) modp. Its256bit left rotation is the expected stored word before the source final rotations.',
 representation='Pre-fold open ripple reconstructed from actual TG XOR complemented source XOR live carry; overflow from three real E sums. Postfold reconstruction uses restored ripple. Source words decoded with the actual s2 complement; all physical/logical values retained.',
 proofs=proofs,important=[r for r in proofs if r['index']in[8033,94]],
 limitations='Finite values only, no phase cause claims. Full tick entry may already be wrong from earlier ticks; model uses actual entry, so this isolates each local transformation. No width/fold/source changes or score.')
Path(sys.argv[2]).write_text(json.dumps(doc,indent=2)+'\n',newline='\n')
print(json.dumps(dict(cases=len(proofs),bad_producers=[r for r in proofs if not r['producer_exact']],important=doc['important']),indent=2))
