"""Exact small reversible synthesis for the first peak-carry block.

All 32 data inputs and both measurement outcomes are checked. This is a
component search, not a full point-addition score. Search uses complete linear
spaces around two Toffoli gates and exact 32-bit truth tables.
"""
import json
from pathlib import Path
from itertools import combinations
import time

N=5
MASK=(1<<(1<<N))-1
xs=[sum(((s>>q)&1)<<s for s in range(1<<N)) for q in range(N)]

def source(m):
    # a=803,b=253,c=1232,d=254,e=255. Ancilla z=1233 starts zero.
    a,b,c,d,e=xs
    z=a&b
    a^=c;z^=c;b^=c;d^=z;a^=z;e^=a&d;a^=z;e^=z;d^=z
    e^=a;d^=a;d^=z;z^=c;b^=c;a^=c
    phase=z if m else 0
    z=0
    if m:phase^=a&b
    assert phase==0 and z==0
    return [a,b,c,d,e]

def rank(vs):
    rows={}
    for v in vs:
        while v:
            p=v.bit_length()-1
            if p in rows:v^=rows[p]
            else:rows[p]=v;break
    return len(rows)

def span(vs):
    out=[0]
    for v in vs:out += [x^v for x in out]
    return out

def linear_coefficients(vs,target):
    rows={}
    for i,v in enumerate(vs):
        w=1<<i
        while v:
            p=v.bit_length()-1
            if p in rows:v^=rows[p][0];w^=rows[p][1]
            else:rows[p]=(v,w);break
    w=0;v=target
    while v:
        p=v.bit_length()-1
        if p not in rows:return None
        v^=rows[p][0];w^=rows[p][1]
    return w

def search():
    began=time.monotonic();ys=source(0);assert ys==source(1)
    assert rank(xs)==rank(ys)==N
    assert len({sum(((y>>s)&1)<<i for i,y in enumerate(ys)) for s in range(1<<N)})==1<<N
    forms=span(xs);W=set(span(ys));checked=0;near=0
    gates=[]
    for a,b in combinations(range(1,1<<N),2):
        h=forms[a]&forms[b]
        for t in range(1,1<<N):
            if (a&t).bit_count()%2 or (b&t).bit_count()%2:continue
            gates.append((a,b,t,h))
    for a,b,t,h in gates:
        fs=[x^(h if t>>i&1 else 0) for i,x in enumerate(xs)]
        if rank(fs+ys)>N+1:continue
        near+=1;S=span(fs);union=set(span(fs+ys)) if False else None
        # One more shear changes the function space by at most one dimension.
        for c,d in combinations(range(1,1<<N),2):
            hh=S[c]&S[d]
            if rank(fs+ys+[hh])>N+1:continue
            for u in range(1,1<<N):
                if (c&u).bit_count()%2 or (d&u).bit_count()%2:continue
                checked+=1
                gs=[x^(hh if u>>i&1 else 0) for i,x in enumerate(fs)]
                if all(g in W for g in gs):
                    out=[linear_coefficients(gs,y) for y in ys]
                    assert all(v is not None for v in out)
                    return dict(status='EXACT_COMPONENT_TWO_TOFFOLI_WITNESS',inputs=N,
                        data_cases=32,measurement_outcomes=2,first=[a,b,t],second=[c,d,u],
                        output_linear=out,source_truth=ys,checked=checked,near=near,
                        elapsed_seconds=time.monotonic()-began)
    return dict(status='NO_TWO_TOFFOLI_WITNESS_IN_LINEAR_SHEAR_FAMILY',inputs=N,
        checked=checked,near=near,elapsed_seconds=time.monotonic()-began,
        scope='Exact zero-preserving two-Toffoli linear-conjugation family; no larger-circuit optimality claim')

if __name__=='__main__':
    result=search();print(json.dumps(result,indent=2))
    Path(__file__).with_name('peak-synthesis.json').write_text(json.dumps(result,indent=2)+'\n')
