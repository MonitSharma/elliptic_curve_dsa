"""Compare exact sets and dimensions; order repair is forbidden on unequal sets."""
import json, sys
from pathlib import Path
base, candidate, out = map(Path, sys.argv[1:4])
old, new = (json.loads(p.read_text())['rows'] for p in [base,candidate])
assert len(new) <= len(old)
rows = []
for left,right in zip(old,new):
    assert left['payload'] == right['payload']
    item = {'payload': left['payload'], 'physical_inputs_equal': all(left[k] == right[k] for k in ['acc','e','nm','k']), 'old_plan': left['plan'], 'new_plan': right['plan']}
    for boundary in ['entry','exit']:
        a,b = left[boundary+'_state'], right[boundary+'_state']
        item[boundary] = {'ordered_state_equal': a == b, 'free_qubit_sets_equal': sorted(a[0]) == sorted(b[0]), 'free_bit_sets_equal': sorted(a[1]) == sorted(b[1]), 'next_bit_equal': a[2] == b[2], 'dims_equal': left[boundary+'_dims'] == right[boundary+'_dims']}
    rows.append(item)
doc = {'scope':'exact allocator sets and physical IDs; not semantic proof', 'baseline_calls':len(old), 'candidate_calls':len(new), 'rows':rows}
out.write_text(json.dumps(doc,indent=2)+'\n',newline='\n')
print(json.dumps(rows[:4],indent=2))
print('Unequal exit sets:',[r['payload'] for r in rows if not r['exit']['free_qubit_sets_equal']])
