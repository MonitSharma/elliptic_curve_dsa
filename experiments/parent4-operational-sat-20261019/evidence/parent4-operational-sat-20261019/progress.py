import json
from pathlib import Path
r=Path(__file__).resolve().parent;proof=r.parent/'product-parent-sat-20261019';q=proof/'parent4-filter'
out={'transfer_certificate':(proof/'PUBLIC-PARENT-TRANSFER.json').exists(),'filter_exit':None,'prepare_exit':None}
for name,p in [('filter_exit',q/'filter.exit'),('prepare_exit',r/'prepare-v2.exit'),('earlier_prepare_exit',r/'prepare.exit')]:
    if p.exists():out[name]=p.read_text().strip()
out['qualification_rows']={p.name:sum(1 for _ in p.open()) for p in sorted(q.glob('*.jsonl'))}
for name in ('RESULT.json','CONTROL.json','ACCEPTANCE.json','run-record.json'):
    p=(q if name=='RESULT.json' and not (r/'run-record.json').exists() else r)/name
    if p.exists():
        d=json.loads(p.read_text());out[name]={k:d[k] for k in ('status','expected_nonces','expected_hours_at_56_threads_ideal_linear','started_utc','workers','threads_each','best_full_protected_pass','screened_unique_completed_rows') if k in d}
out['search_windows']=[json.loads(p.read_text()) for p in sorted(r.glob('worker*-progress.json'))]
out['passes']=[json.loads(p.read_text()) for p in sorted((r/'passes').glob('pass-*.json'))] if (r/'passes').exists() else []
print(json.dumps(out,indent=2))
