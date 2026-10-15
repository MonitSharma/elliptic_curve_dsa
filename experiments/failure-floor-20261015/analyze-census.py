from pathlib import Path
import json,statistics,collections
root=Path(__file__).resolve().parent;ev=root/'evidence'
parents=[json.loads(l)for l in(ev/'parent-window4-census.jsonl').read_text().splitlines()]
child=[json.loads(l)for l in(ev/'window4-census.jsonl').read_text().splitlines()]
assert len(parents)==len(child)==4096
assert all(a['batch']==b['batch']==i for i,(a,b)in enumerate(zip(parents,child)))
keys=['value_shots','phase_shots','dirty_shots']
def summarize(rows):
 bad=sum(any(r[k]for k in keys)for r in rows)
 return {'shots':sum(r['shots']for r in rows),'batches':len(rows),'failed_batches':bad,'expected_failed_batches_per_9024':141*bad/len(rows),'mean_executed_t':sum(r['toffoli']for r in rows)/sum(r['shots']for r in rows),'value_shots':sum(r['value_shots']for r in rows),'phase_batches':sum(bool(r['phase_shots'])for r in rows),'dirty_batches':sum(bool(r['dirty_shots'])for r in rows)}
d=[(b['toffoli']-a['toffoli'])/64 for a,b in zip(parents,child)]
pv={(r['batch'],f['lane'])for r in parents for f in r['failures']if f['value']};cv={(r['batch'],f['lane'])for r in child for f in r['failures']if f['value']}
out={'qualified_score':None,'parent_source':'unsmoothed wide 95e771ba, NOT official smooth nonce375','window_source':'40abbe69; Y15 windows60/61 instead of56/57','peak_q_both':1464,'parent':summarize(parents),'window4':summarize(child),'paired_t_delta':statistics.mean(d),'paired_t_delta_standard_error':statistics.stdev(d)/len(d)**0.5,'value_failures_cured':len(pv-cv),'new_value_failures':len(cv-pv),'caveat':'Capacity experiment; not exact correctness. Phase event changes are not monotone because measurement consumption changes.'}
(root/'window4-census-analysis.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
