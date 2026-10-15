"""Summarize preserved independent replay evidence without scoring it."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent;ev=root/'evidence';summary=dict(scope='complete-circuit independent diagnostics only; no official score',replays={})
for label,name in [('original','fixed-input-original-vs-v6.json'),('v6','fixed-input-v6-replay.json'),('v9-old-failed-inputs','fixed-input-v9-replay.json'),('v9-independent-curves','independent-curves-v9-result.json')]:
 p=ev/name
 if not p.exists():continue
 r=json.loads(p.read_text(encoding='utf8'));by_case={}
 for row in r['outputs']:
  key=str(row['fixed_failed_shot']);entry=by_case.setdefault(key,dict(lanes=0,value_failures=0,distinct_actual=set()))
  entry['lanes']+=1;entry['value_failures']+=not row['value_ok'];entry['distinct_actual'].add(tuple(row['actual']))
 for entry in by_case.values():entry['distinct_actual']=sorted(entry['distinct_actual'])
 summary['replays'][label]=dict(receipt_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),ops_path=r['ops_path'],physical_ops=r['physical_ops'],lanes=r['lanes'],value_mismatch_lanes=r['value_mismatch_lanes'],phase_word=r['phase_word'],ancilla_garbage_wires=len(r['ancilla_garbage']),by_case=by_case)
(root/'fixed-replay-summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:{f:v[f] for f in ['lanes','value_mismatch_lanes','phase_word','ancilla_garbage_wires']}for k,v in summary['replays'].items()},indent=2))
