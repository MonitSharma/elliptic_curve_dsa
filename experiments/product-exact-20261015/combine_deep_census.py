import hashlib,json,math,statistics
from pathlib import Path
root=Path(__file__).resolve().parent;data={}
for name in ['parent','candidate']:
    paths=[root/f'frozen-{name}-census.jsonl',root/f'frozen-{name}-continuation.jsonl']
    rows=[json.loads(line) for path in paths for line in path.open()]
    assert len(rows)==32768 and [r['batch'] for r in rows]==list(range(32768))
    out=root/f'frozen-deep-{name}.jsonl'
    out.write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in rows))
    bad=sum(bool(r['value_shots'] or r['phase_shots'] or r['dirty_shots']) for r in rows)
    data[name]={'batches':len(rows),'shots':len(rows)*64,'failed_batches':bad,'failures_per_packet':141*bad/len(rows),'mean_t':sum(r['toffoli'] for r in rows)/64/len(rows),'source_files_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    data[name]['batch_fail_standard_error_per_packet']=141*math.sqrt(bad/len(rows)*(1-bad/len(rows))/len(rows))
    data[name]['rows']=rows
d=[(p['toffoli']-c['toffoli'])/64 for p,c in zip(data['parent']['rows'],data['candidate']['rows'])]
for r in data.values():del r['rows']
data['paired_saving_t']=statistics.mean(d);data['paired_se_t']=statistics.stdev(d)/math.sqrt(len(d))
data['label']='product-frozen-four-stage-20261015';data['nonce_search_performed']=False
(root/'frozen-deep-summary.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data,indent=2))
