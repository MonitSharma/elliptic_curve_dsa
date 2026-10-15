import hashlib,json,math,statistics
from pathlib import Path
root=Path(__file__).resolve().parent
folder=root/'product-smoothing-20261016'
data={'label':'product-tail-smooth-20261016','nonce_search_performed':False,'score':None}
rows={}
for name in ['parent','candidate']:
    path=folder/f'{name}-census.jsonl'
    rows[name]=[json.loads(line) for line in path.open()]
    assert len(rows[name])==4096 and [r['batch'] for r in rows[name]]==list(range(4096))
    values=rows[name];bad=sum(bool(r['value_shots'] or r['phase_shots'] or r['dirty_shots']) for r in values)
    data[name]={'batches':4096,'shots':262144,'failed_batches':bad,'failures_per_packet':141*bad/4096,'mean_t':sum(r['toffoli'] for r in values)/262144,'census_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'value_shots':sum(r['value_shots'] for r in values),'phase_shots':sum(r['phase_shots'] for r in values),'dirty_shots':sum(r['dirty_shots'] for r in values)}
delta=[(c['toffoli']-p['toffoli'])/64 for p,c in zip(rows['parent'],rows['candidate'])]
data['paired_cost_t']=statistics.mean(delta);data['paired_se_t']=statistics.stdev(delta)/math.sqrt(len(delta))
bad=lambda r:bool(r['value_shots'] or r['phase_shots'] or r['dirty_shots'])
data['paired_recovered_batches']=sum(bad(p) and not bad(c) for p,c in zip(rows['parent'],rows['candidate']))
data['paired_new_failed_batches']=sum(not bad(p) and bad(c) for p,c in zip(rows['parent'],rows['candidate']))
data['failure_reduction_per_packet']=data['parent']['failures_per_packet']-data['candidate']['failures_per_packet']
data['resources']=json.loads((folder/'resources.jsonl').read_text())
(root/'product-smoothing-summary.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data,indent=2))
