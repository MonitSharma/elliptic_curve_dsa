import hashlib,json,math,statistics
from pathlib import Path
root=Path(__file__).resolve().parent;folder=root/'compact11-frozen-census-20261016';data={};rows={}
for name in ['parent','candidate']:
    path=folder/f'{name}-census.jsonl';values=[json.loads(line) for line in path.open()]
    assert len(values)==32768 and [r['batch'] for r in values]==list(range(32768))
    bad=sum(bool(r['value_shots'] or r['phase_shots'] or r['dirty_shots']) for r in values);rows[name]=values
    data[name]={'batches':32768,'shots':2097152,'failed_batches':bad,'failures_per_packet':141*bad/32768,'mean_t':sum(r['toffoli'] for r in values)/2097152,'census_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'failure_per_packet_se':141*math.sqrt(bad/32768*(1-bad/32768)/32768)}
delta=[(p['toffoli']-c['toffoli'])/64 for p,c in zip(rows['parent'],rows['candidate'])]
data['paired_saving_t']=statistics.mean(delta);data['paired_se_t']=statistics.stdev(delta)/math.sqrt(len(delta))
data['label']='product-compact11-frozen-20261016';data['nonce_search_performed']=False;data['score']=None
data['measured_failure_gate_pass']=data['candidate']['failures_per_packet']<=data['parent']['failures_per_packet'] and data['candidate']['failures_per_packet']<=18
data['declaration']=json.loads((folder/'DECLARATION.json').read_text())
(root/'compact11-census-summary.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data,indent=2))
