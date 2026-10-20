"""Exhaust all Boolean inputs of the local phase/channel identities."""
import itertools,json,hashlib
from pathlib import Path
r=Path(__file__).resolve().parent;cases=0;counter=[]
for a,b,c,top,atop,desired,m in itertools.product(range(2),repeat=7):
 maj=(a&b)^(a&c)^(b&c)
 old_phase=m&(top^desired^atop^c^((a^c)&(b^c)))
 new_phase=m&(top^desired^atop^maj)
 assert old_phase==new_phase
 if old_phase!=(new_phase^m)and not counter:counter=[a,b,c,top,atop,desired,m]
 cases+=1
padding=0
for b,c,top,desired,m in itertools.product(range(2),repeat=5):
 assert(m&(top^desired^(b&c)))==(m&(top^desired^((0&b)^(0&c)^(b&c))))
 padding+=1
for a,b in itertools.product(range(2),repeat=2):assert(a&b)==(a&(1^(a^b)))
assert counter
(r/'BOOLEAN-PROOF.json').write_text(json.dumps({'status':'ALL_LOCAL_BOOLEAN_ASSIGNMENTS_PASS','full_terminal_channel_cases':cases,'zero_extended_terminal_channel_cases':padding,'zero_carry_completed_sum_cases':4,'wrong_sign_counterexample':counter,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Exact local Boolean phase identities only; no full-circuit, universal point-add or novelty claim.'},indent=2)+'\n')
