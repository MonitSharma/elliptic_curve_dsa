import hashlib,json,math,statistics
from pathlib import Path
root=Path(__file__).resolve().parent;folder=root/'category-restore-census-v2-20261016';data={};rows={}
for name in ['parent','candidate']:
    assert (folder/f'{name}-census.exit').read_text().strip()=='0'
    path=folder/f'{name}-census.jsonl';values=[json.loads(line) for line in path.open()]
    assert len(values)==4096 and [r['batch'] for r in values]==list(range(4096))
    bad=[bool(r['value_shots'] or r['phase_shots'] or r['dirty_shots']) for r in values];rows[name]=(values,bad)
    data[name]={'batches':4096,'shots':262144,'failed_batches':sum(bad),'failures_per_packet':141*sum(bad)/4096,'mean_t':sum(r['toffoli'] for r in values)/262144,'census_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
delta=[(c['toffoli']-p['toffoli'])/64 for p,c in zip(rows['parent'][0],rows['candidate'][0])]
fail=[141*(int(p)-int(c)) for p,c in zip(rows['parent'][1],rows['candidate'][1])]
data.update(paired_added_t=statistics.mean(delta),paired_added_t_se=statistics.stdev(delta)/math.sqrt(4096),paired_failures_per_packet_reduced=statistics.mean(fail),paired_failure_reduction_se=statistics.stdev(fail)/math.sqrt(4096),parent_only_failures=sum(p and not c for p,c in zip(rows['parent'][1],rows['candidate'][1])),candidate_only_failures=sum(c and not p for p,c in zip(rows['parent'][1],rows['candidate'][1])),label='product-deletion-restoration-20261016',scope='Component cost/failure measurement; source restores the complete inherited deletion family. Not an exact rewrite or a scored candidate.',nonce_search_performed=False,score=None)
(root/'category-census-summary.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data,indent=2))
