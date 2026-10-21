"""Declare and run exactly one fresh final statistical gate; never resample."""
import concurrent.futures,hashlib,json,math,statistics,subprocess,urllib.request
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parent;run=root/'continuation84';d=run/'gate';d.mkdir(exist_ok=False)
native=json.loads((run/'NATIVE.json').read_text());assert native['status']=='NATIVE_IDENTITY_AND_PROTECTED_FILES_PASS'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_hashes=json.loads((run/'point-add-source.json').read_text())
assert all(sha(Path(native['candidate'])/p)==h for p,h in source_hashes.items())
api='https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74/submissions'
data=urllib.request.urlopen(api,timeout=60).read();(d/'public-submissions.json').write_bytes(data)
records=json.loads(data)['submissions'];eligible=[r for r in records if (r.get('status')=='accepted' or (r.get('status')=='rejected' and r.get('rejectionReason')=='score did not improve current best')) and isinstance(r.get('officialScore'),int) and (r.get('officialMetrics') or {}).get('qubits',0)*(r.get('officialMetrics') or {}).get('toffoli',0)==r['officialScore'] and r['officialScore']>0]
leader=min(eligible,key=lambda r:r['officialScore'])
if leader['id']!='9dc3798c-93e0-4da4-a6a9-37586737c4af':
    (d/'PUBLIC_PARENT_CHANGED.json').write_text(json.dumps(leader,indent=2)+'\n');raise RuntimeError('Public product parent changed; gate not started')
binary=Path('/home/hclau/ecdsa_research/simd-census-v2-20261016/bin/simd_census_v2');assert sha(binary)=='790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66'
paths={'parent':root/'parent/ops.bin','candidate':Path(native['candidate'])/'ops.bin'}
assert sha(paths['parent'])=='99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683'
assert sha(paths['candidate'])==native['stream_sha256']
label='pareto-parent84-gate-20261019-v1';n=32768
decl={'declared_at_utc':datetime.now(timezone.utc).isoformat(),'label':label,'batch_count':n,'shots_per_batch':64,'public_parent':leader['id'],'streams':{k:{'path':str(p),'sha256':sha(p)} for k,p in paths.items()},'workers_per_stream':16,'verdict_is_final':True,'nonce_search_authorized_by_this_script':False}
decl['gate_driver_sha256']=sha(Path(__file__).resolve())
(d/'DECLARATION.json').write_text(json.dumps(decl,indent=2)+'\n')
available=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024;assert available>130*1024**3
def census(item):
    key,path=item
    with (d/(key+'.log')).open('wb') as out:subprocess.run([str(binary),str(path),label,'0',str(n),'16',str(d/(key+'.jsonl')),'0'],stdout=out,stderr=subprocess.STDOUT,check=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(census,paths.items()))
rows={}
for key in paths:
    a=[json.loads(s) for s in (d/(key+'.jsonl')).open()];assert len(a)==n
    rows[key]={r['batch']:r for r in a};assert sorted(rows[key])==list(range(n)) and all(r['shots']==64 and r.get('skipped',0)==0 for r in a)
p,c=rows['parent'],rows['candidate'];failed={k:sum(bool(r['failures']) for r in a.values()) for k,a in rows.items()};value={k:sum(r['value_shots'] for r in a.values()) for k,a in rows.items()};dirty={k:sum(r['dirty_shots'] for r in a.values()) for k,a in rows.items()}
b=sum(bool(c[i]['failures']) and not p[i]['failures'] for i in p);new_pass=sum(bool(p[i]['failures']) and not c[i]['failures'] for i in p)
prob=sum(math.comb(b+new_pass,x) for x in range(b,b+new_pass+1))/2**(b+new_pass)
rules={'value_not_above_parent':value['candidate']<=value['parent'],'paired_mcnemar_p_at_least_005':prob>=.05,'failed_batches_per_packet_at_most_18':141*failed['candidate']/n<=18,'zero_dirty_shots':dirty['candidate']==0}
delta=[(p[i]['toffoli']-c[i]['toffoli'])/64 for i in p]
result={'status':'FAILURE_GATE_PASS' if all(rules.values()) else 'FAILURE_GATE_FAIL','label':label,'batches':n,'shots_each':64*n,'rules':rules,'failed_batches':failed,'value_shots':value,'dirty_shots':dirty,'newly_failing_b':b,'newly_passing_c':new_pass,'mcnemar_one_sided_p':prob,'failed_batches_per_packet':{k:141*v/n for k,v in failed.items()},'paired_mean_toffoli_saving':statistics.mean(delta),'saving_standard_error':statistics.stdev(delta)/n**.5,'mean_toffoli':{k:sum(r['toffoli'] for r in a.values())/(64*n) for k,a in rows.items()},'census_sha256':{k:sha(d/(k+'.jsonl')) for k in paths},'stream_sha256':{k:sha(p) for k,p in paths.items()},'no_official_benchmark_or_nonce_search':True}
(d/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
assert result['status']=='FAILURE_GATE_PASS','Final gate failed; do not rerun'
assert all(sha(Path(native['candidate'])/p)==h for p,h in source_hashes.items())
if result['paired_mean_toffoli_saving']-2*result['saving_standard_error']<12:
    (run/'MARGIN_TOO_SMALL.json').write_text(json.dumps({'status':'FAILURE_GATE_PASS_RESOURCE_MARGIN_TOO_SMALL','criterion':'paired saving minus two standard errors must be at least 12 T before pursuing a long search','gate':result},indent=2)+'\n')
    raise RuntimeError('Failure gate passed but product margin is too small; no nonce search')
(run/'READY_FOR_NONCE_RESEARCH.json').write_text(json.dumps({'status':'GATE_PASS_NOT_A_SCORED_RESULT','gate':result,'remaining':['Qualify a sound candidate-bound prefilter or affordable exact search','Ascending nonce search on frozen source','Unchanged official benchmark','Refresh public record and prepare reviewable submission']},indent=2)+'\n')
