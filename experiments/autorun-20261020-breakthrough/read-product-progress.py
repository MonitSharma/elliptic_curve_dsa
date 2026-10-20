import collections,json,statistics
from datetime import datetime,timezone
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research');out={'at_utc':datetime.now(timezone.utc).isoformat(),'audits':{}}
for name in ['breakthrough-value-ir-audit-v2-20261020','breakthrough-value-ir-audit-v3-20261020','breakthrough-value-ir-audit-v4-20261020','breakthrough-value-abstract-audit-20261020']:
 r=ws/name;d={'terminal':(r/'run.exit').read_text().strip()if(r/'run.exit').exists()else'RUNNING','cases':{}}
 for p in r.glob('*.json'):
  if p.name not in['product_candidate.json','toffoli747226.json']:continue
  v=json.loads(p.read_text());d['cases'][p.stem]={k:v[k]for k in['final_value_nodes','live_random_measurement_definitions','original_rng_words','certified_global_zero_resets']};d['cases'][p.stem]['rounds']=len(v['rounds'])
  if'abstract_audit'in v:d['cases'][p.stem]['abstract_audit']=v['abstract_audit']
 out['audits'][name]=d
r=ws/'breakthrough-public-best-drop-nonce-v2-20261020';rows=[]
with(r/'production.jsonl').open()as inp:
 for line in inp:
  if line.endswith('\n'):rows.append(json.loads(line))
out['initial_exact_search']={'completed_screens':len(rows),'passes':[x['nonce']for x in rows if x['pass']],'failure_kinds':dict(collections.Counter(x['kind']for x in rows)),'mean_batches_run':statistics.mean(x['batches_run']for x in rows),'mean_selected_rng_group_seconds':statistics.mean(x['selected_rng_group_secs']for x in rows),'mean_selected_exact_group_seconds':statistics.mean(x['selected_exact_group_secs']for x in rows),'terminal':(r/'run.exit').read_text().strip()if(r/'run.exit').exists()else'RUNNING'}
for name,marker in [('breakthrough-public-best-drop-nonce-continuation-20261020','run.exit'),('breakthrough-public-best-drop-final-20261020','review.exit')]:
 r=ws/name;out[name]=(r/marker).read_text().strip()if(r/marker).exists()else'WAITING_OR_RUNNING'
print(json.dumps(out,indent=2))
