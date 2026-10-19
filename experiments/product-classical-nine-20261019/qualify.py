"""One final paired gate. Never restart a partially declared census."""
import hashlib,json,math,statistics,subprocess
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'candidate';out=r/'qualification'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
def save(name,data): (out/name).write_text(json.dumps(data,indent=2)+'\n')
assert (r/'run.exit').read_text().strip()=='0'
native=json.loads((r/'NATIVE-RECEIPT.json').read_text())
assert native['status']=='NATIVE_COMPLETE_STREAM_IDENTICAL_TO_CONTROLLED_RESEARCH_CANDIDATE'
freeze=json.loads((r/'SOURCE_FREEZE.json').read_text())
def check_source():
    assert all(sha(t/p)==h for p,h in {**freeze['source_files'],**freeze['protected_files']}.items())
    assert {p.relative_to(t).as_posix() for p in (t/'src/point_add').rglob('*') if p.is_file()}==set(freeze['source_files'])
check_source()
assert len(freeze['protected_files'])==17
subprocess.run(['python3',str(r/'refresh_record.py')],check=True)
public=json.loads((r/'PUBLIC-RECORD.json').read_text());leader=public['leader']
assert leader['id']=='9dc3798c-93e0-4da4-a6a9-37586737c4af','Public parent changed; no gate declared'
assert leader['submissionCommitSha']=='0c3a0751ab66bd9144358d67563bcb79201cf636'
binary=ws/'simd-census-v2-20261016/bin/simd_census_v2'
assert sha(binary)=='790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66'
paths={'parent':ws/'product-pareto-20261019/parent/ops.bin','candidate':t/'ops.bin'}
assert sha(paths['parent'])=='99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683'
assert sha(paths['candidate'])==native['compressed_sha256']
out.mkdir(exist_ok=False)
label='pareto-parent4-classical9-gate-20261019-v1';batches=262144;threads=2
decl={'declared_at_utc':datetime.now(timezone.utc).isoformat(),'label':label,'batch_count':batches,'shots_per_batch':64,
      'workers_per_stream':threads,'streams_run_sequentially':True,'public_parent':leader,'public_refresh_sha256':sha(r/'PUBLIC-RECORD.json'),
      'streams':{k:{'path':str(p),'sha256':sha(p)}for k,p in paths.items()},'native_receipt':native,
      'frozen_source_manifest_sha256':sha(r/'SOURCE_FREEZE.json'),'driver_sha256':sha(__file__),
      'verdict_is_final':True,'identity_tail_inherited_unchanged':'1048009047001','nonces_screened_on_this_source':0,
      'scope':'Fresh failure-rate qualification only; no benchmark, score or nonce search.',
      'required_rules':['candidate value shots <= parent','one-sided exact McNemar p >= 0.05','141 * candidate failed batches / total <= 18','zero dirty shots']}
save('DECLARATION.json',decl);print(json.dumps(decl,indent=2),flush=True)
for key,path in paths.items():
    with (out/(key+'.log')).open('xb') as log:
        subprocess.run([str(binary),str(path),label,'0',str(batches),str(threads),str(out/(key+'.jsonl')),'0'],stdout=log,stderr=subprocess.STDOUT,check=True)
rows={}
for key in paths:
    a=[json.loads(line) for line in (out/(key+'.jsonl')).open()]
    assert len(a)==batches
    rows[key]={x['batch']:x for x in a}
    assert sorted(rows[key])==list(range(batches))
    assert all(x['shots']==64 and x.get('skipped',0)==0 for x in a)
p,c=rows['parent'],rows['candidate']
failed={k:sum(bool(x['failures']) for x in a.values()) for k,a in rows.items()}
value={k:sum(x['value_shots'] for x in a.values()) for k,a in rows.items()}
dirty={k:sum(x['dirty_shots'] for x in a.values()) for k,a in rows.items()}
b=sum(bool(c[i]['failures']) and not p[i]['failures'] for i in p)
nc=sum(bool(p[i]['failures']) and not c[i]['failures'] for i in p)
prob=sum(math.comb(b+nc,x) for x in range(b,b+nc+1))/2**(b+nc)
rules={'value_not_above_parent':value['candidate']<=value['parent'],'paired_mcnemar_p_at_least_005':prob>=.05,
       'failed_batches_per_packet_at_most_18':141*failed['candidate']/batches<=18,'zero_dirty_shots':dirty['candidate']==0}
delta=[(p[i]['toffoli']-c[i]['toffoli'])/64 for i in p]
check_source();assert all(sha(path)==decl['streams'][key]['sha256'] for key,path in paths.items())
result={'status':'FAILURE_GATE_PASS' if all(rules.values()) else 'FAILURE_GATE_FAIL','label':label,'batches':batches,'shots_each':64*batches,
        'rules':rules,'failed_batches':failed,'value_shots':value,'dirty_shots':dirty,'newly_failing_b':b,'newly_passing_c':nc,
        'mcnemar_one_sided_p':prob,'failed_batches_per_packet':{k:141*v/batches for k,v in failed.items()},
        'paired_mean_toffoli_saving':statistics.mean(delta),'saving_standard_error':statistics.stdev(delta)/batches**.5,
        'mean_toffoli':{k:sum(x['toffoli'] for x in a.values())/(64*batches) for k,a in rows.items()},
        'census_sha256':{k:sha(out/(k+'.jsonl')) for k in paths},'stream_sha256':{k:sha(path) for k,path in paths.items()},
        'no_official_benchmark_or_nonce_search':True}
save('RESULT.json',result);print(json.dumps(result,indent=2),flush=True)
assert all(rules.values()),'Final gate failed; never rerun to reverse its verdict'
