"""Fresh diagnostic paired pilot. This is not the final failure-rate gate."""
import concurrent.futures, hashlib, json, statistics, subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
binary=Path('/home/hclau/ecdsa_research/simd-census-v2-20261016/bin/simd_census_v2')
assert hashlib.sha256(binary.read_bytes()).hexdigest()=='790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66'
label='pareto-exact-diagnostic-20261019-v1'
cases={'parent':root/'parent/ops.bin','unwrapped':root/'parent-unwrapped.ops.bin','retained':root/'parent-unwrapped-retained.ops.bin'}
folder=root/'pilot-parent';folder.mkdir(exist_ok=False)
decl={'status':'DIAGNOSTIC_ONLY_NOT_FAILURE_GATE','label':label,'batches':512,'shots_per_batch':64,'workers_per_stream':8,
      'streams':{k:{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for k,p in cases.items()}}
(folder/'DECLARATION.json').write_text(json.dumps(decl,indent=2)+'\n')
def run(case):
    key,path=case
    with (folder/(key+'.log')).open('w') as log:
        subprocess.run([str(binary),str(path),label,'0','512','8',str(folder/(key+'.jsonl')),'0'],stdout=log,stderr=subprocess.STDOUT,check=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    list(pool.map(run,cases.items()))
rows={}
for k in cases:
    a=[json.loads(line) for line in (folder/(k+'.jsonl')).open()]
    assert len(a)==512
    rows[k]={r['batch']:r for r in a};assert sorted(rows[k])==list(range(512))
summary={'status':'DIAGNOSTIC_ONLY_NOT_FAILURE_GATE','label':label,'batches':512,'shots_each':32768,'streams':{}}
for k,a in rows.items():
    delta=[(rows['parent'][i]['toffoli']-a[i]['toffoli'])/64 for i in range(512)]
    summary['streams'][k]={'mean_toffoli':sum(r['toffoli'] for r in a.values())/(64*512),
        'value_shots':sum(r['value_shots'] for r in a.values()),'dirty_shots':sum(r['dirty_shots'] for r in a.values()),
        'failed_batches':sum(bool(r['failures']) for r in a.values()),'paired_mean_toffoli_saving':statistics.mean(delta),
        'saving_standard_error':statistics.stdev(delta)/512**0.5}
(folder/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
assert all(s['dirty_shots']==0 for s in summary['streams'].values())
assert all(s['value_shots']==summary['streams']['parent']['value_shots'] for s in summary['streams'].values())
