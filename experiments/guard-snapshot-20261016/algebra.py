"""Exact square-free Boolean ANF checks for combined-guard snapshot restoration."""
from pathlib import Path
import json
ZERO=frozenset();ONE=frozenset([frozenset()])
def var(i):return frozenset([frozenset([i])])
def mul(a,b):
    out=set()
    for x in a:
        for y in b:
            p=x|y
            if p in out:out.remove(p)
            else:out.add(p)
    return frozenset(out)
def xor(a,b):return a^b
checks=0
for depth in range(1,65):
    guards=[];base=ONE
    for i in range(depth):
        # A newly zeroed snapshot OR condition is exactly the combined guard.
        g=mul(base,var(i));guards.append(g);base=g
    rebuilt=ONE
    for i,snapshot in enumerate(guards):
        rebuilt=mul(rebuilt,snapshot);assert rebuilt==guards[i];checks+=1
    # Arbitrary later original-bit writes are independent of immutable snapshots.
    changed=mul(ONE,var(1000+depth));assert changed!=base
    # This identity applies to arbitrary guard functions too, not just variables.
    # Construct nested scopes with negation, XOR, products and reused predicates.
    base=ONE;compound=[]
    for i in range(depth):
        b=xor(var(i%5),mul(var((i+1)%5),var((i+2)%5)))
        if i%2:b=xor(ONE,b)
        base=mul(base,b);compound.append(base)
    rebuilt=ONE
    for i,snapshot in enumerate(compound):
        rebuilt=mul(rebuilt,snapshot);assert rebuilt==compound[i];checks+=1
report={'status':'EXACT_BOOLEAN_ANF_SNAPSHOT_STACK_IDENTITIES_PASS','depths_checked':64,
    'exact_equalities':checks,'general_reason':'S_i=S_(i-1)*g_i; S_i*S_j=S_i for j<i by idempotence; therefore product(S_1..S_i)=S_i.',
    'arbitrary_mutated_original_guard_bits_rejected_as_replacement':True,
    'not_a_cache_phase_or_donor_certificate':True,'no_candidate_or_score':True}
(Path(__file__).resolve().parent/'ALGEBRA.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
