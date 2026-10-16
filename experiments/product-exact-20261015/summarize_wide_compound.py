import hashlib,json,math,statistics
from pathlib import Path
root=Path(__file__).resolve().parent;folder=root/'wide-compound-frozen-20261016';data={};rows={}
assert (root/'wide-compound-native.exit').read_text().strip()=='0'
assert hashlib.sha256((root/'candidate-wide-compound/ops.bin').read_bytes()).hexdigest()=='9fe47b0a547b2aad68ddeb682be4f9fcab5dd184459a94f96afdc63e0e3fded8'
for name in ['parent','candidate']:
    assert (folder/f'{name}-census.exit').read_text().strip()=='0'
    path=folder/f'{name}-census.jsonl';values=[json.loads(line) for line in path.open()]
    assert len(values)==4096 and [r['batch'] for r in values]==list(range(4096))
    bad=sum(bool(r['value_shots'] or r['phase_shots'] or r['dirty_shots']) for r in values);rows[name]=values
    data[name]={'batches':4096,'shots':262144,'failed_batches':bad,'failures_per_packet':141*bad/4096,'mean_t':sum(r['toffoli'] for r in values)/262144,'census_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'failure_per_packet_se':141*math.sqrt(bad/4096*(1-bad/4096)/4096)}
delta=[(p['toffoli']-c['toffoli'])/64 for p,c in zip(rows['parent'],rows['candidate'])]
data['paired_saving_t']=statistics.mean(delta);data['paired_se_t']=statistics.stdev(delta)/math.sqrt(len(delta))
data['label']='wide-compound-frozen-20261016';data['nonce_search_performed']=False;data['score']=None
data['measured_failure_gate_pass']=data['candidate']['failures_per_packet']<=data['parent']['failures_per_packet'] and data['candidate']['failures_per_packet']<=18
data['declaration']=json.loads((root/'WIDE_COMPOUND_FREEZE.json').read_text())
(root/'wide-compound-census-summary.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data,indent=2))
