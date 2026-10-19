"""Exact allocation simulation for a new nonadjacent early-drop schedule."""
import json
from pathlib import Path
r=Path(__file__).resolve().parent
plan=[7,6,6,5,5,4,4,3,3,2,2,3];drops=[0,2,4,6,8]
held=set();peak=0;rows=[]
for j,w in enumerate(plan):
    owned=w-2 if j==len(plan)-1 else w
    peak=max(peak,len(held)+owned)
    rows.append({'stage':'forward','chunk':j,'held_before':len(held),'ladder_owned':owned,'live_peak':len(held)+owned})
    if j<len(plan)-1:held.add(j)
    if j>0 and j-1 in drops:
        assert j<len(plan)-1 and(j<2 or j-2 in held);held.remove(j-1)
for j in range(len(plan)-2,-1,-1):
    if j not in held:continue
    held.remove(j)
    # Erase a kept carry. If its predecessor was dropped, regenerate that
    # whole predecessor, erase its lower carries, compare this chunk, then
    # erase the regenerated boundary by its own exact compare.
    ordinary_compare=plan[j]-1
    if j==0 or j-1 in held:
        needed=ordinary_compare
    else:
        needed=max(plan[j-1],1+ordinary_compare,plan[j-1]-1)
    peak=max(peak,len(held)+needed)
    rows.append({'stage':'erase','chunk':j,'other_held':len(held),'maximum_extra':needed,'live_peak':len(held)+needed})
assert not held and sum(plan)==50 and peak==7
(r/'PLAN-ALLOCATION.json').write_text(json.dumps({'status':'SEVEN_CARRY_SCHEDULE_MODEL','plan':plan,'early_drop_chunks':drops,'bits':sum(plan),'modeled_owned_carry_peak':peak,
    'scope':'Allocation model for the existing exact ladder_drop, excluding fixed core and linear-form helper allocation. Native test required; no full point-add score.',
    'rows':rows},indent=2)+'\n')
print('50 bits, modeled carry peak7; native verification required.')
