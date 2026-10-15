"""Source-independent paired census summary, diagnostic counts only."""
import json
import math
from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent/'evidence'
def read(name):
    rows = [json.loads(line) for line in (root/name).read_text().splitlines() if line.strip()]
    by_id = {r['batch']:r for r in rows}
    assert len(rows) == len(by_id) == 4096
    assert all(r['shots'] == 64 for r in rows)
    return by_id

parent = read('parent-census.jsonl')
candidate = read('candidate-census.jsonl')
assert parent.keys() == candidate.keys()
diffs = [(parent[k]['toffoli'] - candidate[k]['toffoli'])/64 for k in sorted(parent)]
mean = sum(diffs)/len(diffs)
se = math.sqrt(sum((d-mean)**2 for d in diffs)/(len(diffs)-1)/len(diffs))
result = {'status':'diagnostic_only','score':None,'paired_batches':len(diffs),'shots_each':64*len(diffs),
          'mean_T_saving':mean,'saving_standard_error':se,'streams':{}}
for name, rows in [('parent',parent),('candidate',candidate)]:
    result['streams'][name] = {'failed_batches':sum(bool(r['failures']) for r in rows.values()),
        'expected_failed_batches_per_packet':141*sum(bool(r['failures']) for r in rows.values())/len(rows),
        'value_shots':sum(r['value_shots'] for r in rows.values()),
        'phase_shots':sum(r['phase_shots'] for r in rows.values()),
        'dirty_shots':sum(r['dirty_shots'] for r in rows.values()),
        'mean_executed_T':sum(r['toffoli'] for r in rows.values())/(64*len(rows))}
result['same_batch_outcome'] = sum(bool(parent[k]['failures']) == bool(candidate[k]['failures']) for k in parent)
result['passes_failure_gate'] = result['streams']['candidate']['failed_batches'] <= result['streams']['parent']['failed_batches'] and result['streams']['candidate']['expected_failed_batches_per_packet'] <= 18 and result['streams']['candidate']['dirty_shots'] == 0
print(json.dumps(result,indent=2))
