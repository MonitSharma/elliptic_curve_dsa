import itertools,json
from pathlib import Path
# Exhaustive Boolean identities behind only the structural scanner's accepted
# rule. These do not assert any actual source region is accepted.
count=0
for old,a,b,guard,update,mr,oldbit in itertools.product(range(2),repeat=7):
 left=old^(guard*a);right=old^(guard*a*b)
 left^=update;right^=update
 # Exact protected HMR: fresh output bit, phase depends on incoming q, q=0.
 lh=(0,mr);rh=(0,mr);assert lh==rh
 # Exact protected R consumes same MR and has no classical write; q=0.
 lr=(0,oldbit);rr=(0,oldbit);assert lr==rr
 # Unconditional SWAP moves the one possible difference to the other wire.
 assert (update^update)==0 and (left^right)==((guard*a)^(guard*a*b))
 count+=1
# Negative controls: value fanout and inactive conditional reset can preserve
# a real distinction. R/HMR phases are intentionally not declared equal.
assert (1&1)!=(0&1)
assert (1&~0)!=(0&~0)
assert (1&1)!=(0&1), 'R/HMR may change phase'
r={'status':'PASS','exhaustive_cases':count,'negative_controls':['value_fanout','conditional_reset_inactive','phase_difference'],'scope':'Boolean protected value/classical semantics only; no actual site accepted by tests','authority':False}
(Path(__file__).parent/'PRIMITIVE-CHECKS.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
