"""Finite permutation contract for a future zero-input multiplication wrapper."""
from pathlib import Path
import json
cases=0;maps=[]
for p in [5,7,11,17,31,61,127]:
    for x in range(1,p):
        outputs=[]
        for original in range(p+1):
            y=original;z0=int(y==0);zp=int(y==p)
            if z0:y^=1
            if zp:y^=p^1
            assert 1<=y<p
            y=x*y%p # abstract phase-correct nonzero multiplication oracle
            if z0^zp:y^=x
            if zp:y^=p
            z0^=int(y==0);zp^=int(y==p)
            assert z0==zp==0
            expected=original if original in [0,p] else x*original%p
            assert y==expected
            outputs.append(y);cases+=1
        assert sorted(outputs)==list(range(p+1));maps.append({'prime':p,'multiplier':x,'permutation_verified':True})
result={'score':None,'cases':cases,'permutations':len(maps),'status':'abstract finite-domain model only; no candidate circuit','contract':['x is canonical and nonzero modulo p.','y is in 0..p, with 0 and p as separate physical zero encodings.','The underlying multiplication maps nonzero canonical inputs to canonical nonzero output with clean phase and scratch.','Compute separate zero-encoding flags, map either zero to1, multiply, XOR x on the flagged branch, restore the original zero encoding, and uncompute both flags.'],'limitations':['This does not repair zero multiplicand x.','Actual leapfrog output encoding and phase contract must be established before integration.','Seamed multiplication changes x and seed fusion changes its input frame; use an explicitly proved interface before applying this wrapper.','No gate count, quantum implementation or phase proof is claimed.']}
Path(__file__).with_name('zero-guard-model.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
