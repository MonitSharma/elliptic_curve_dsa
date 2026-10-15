import json, math, statistics
from pathlib import Path
root = Path(__file__).resolve().parent
baseline_path = root / 'original-census.jsonl'
baseline = [json.loads(line) for line in baseline_path.open()] if baseline_path.exists() else []
original_baseline=baseline
wide_baseline_path=root/'wide-original-census.jsonl'
wide_baseline=[json.loads(line) for line in wide_baseline_path.open()] if wide_baseline_path.exists() else []
frozen_baseline_path=root/'frozen-parent-census.jsonl'
frozen_baseline=[json.loads(line) for line in frozen_baseline_path.open()] if frozen_baseline_path.exists() else []
wide_frozen_baseline_path=root/'wide-frozen-parent-census.jsonl'
wide_frozen_baseline=[json.loads(line) for line in wide_frozen_baseline_path.open()] if wide_frozen_baseline_path.exists() else []
summary=[]
for path in sorted(root.glob('*-census.jsonl')):
    if path.name.startswith('wide-frozen-'):
        baseline,reference_path=wide_frozen_baseline,wide_frozen_baseline_path
    elif path.name.startswith('wide-'):
        baseline,reference_path=wide_baseline,wide_baseline_path
    elif path.name.startswith('frozen-'):
        baseline,reference_path=frozen_baseline,frozen_baseline_path
    else:
        baseline,reference_path=original_baseline,baseline_path
    rows=[json.loads(line) for line in path.open()]
    if not rows:
        continue
    rec=dict(file=path.name,batches=len(rows),mean_t=sum(r['toffoli'] for r in rows)/64/len(rows),failed_batches=sum(bool(r['value_shots'] or r['phase_shots'] or r['dirty_shots']) for r in rows))
    rec['failures_per_packet']=141*rec['failed_batches']/len(rows)
    if len(baseline)==len(rows) and path != reference_path:
        d=[(b['toffoli']-r['toffoli'])/64 for b,r in zip(baseline,rows)]
        rec['paired_saving_t']=statistics.mean(d)
        rec['paired_se_t']=statistics.stdev(d)/math.sqrt(len(d))
        rec['same_outcome_batches']=sum(bool(b['value_shots'] or b['phase_shots'] or b['dirty_shots'])==bool(r['value_shots'] or r['phase_shots'] or r['dirty_shots']) for b,r in zip(baseline,rows))
    summary.append(rec)
print(json.dumps(summary,indent=2))
