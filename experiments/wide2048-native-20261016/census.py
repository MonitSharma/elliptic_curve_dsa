from pathlib import Path
import hashlib,json,math,subprocess
root=Path(__file__).resolve().parent;dest=root/'wide2048';tree=dest/'candidate'
freeze=json.loads((dest/'DECLARATION.json').read_text())
assert hashlib.sha256((tree/'ops.bin').read_bytes()).hexdigest()==freeze['expected_normal_generated_stream_sha256']
assert '4 passed; 0 failed' in (dest/'native-tests.log').read_text()
runner=root.parent/'simd-census-v2-20261016/bin/simd_census_v2'
assert hashlib.sha256(runner.read_bytes()).hexdigest()=='790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66'
parent=root.parent/'nonce-screen-20261015/final-census/ops.bin'
assert hashlib.sha256(parent.read_bytes()).hexdigest()=='01aad987cfe03e7ca97df6f3dcd26085a21a5836aa6e661ec8fbd9c9c1b63740'
label='wide95-plus-retained2048-scratch64-frozen-20261016'
new_reference=root/'reference753721.ops.bin'
assert hashlib.sha256(new_reference.read_bytes()).hexdigest()=='1d8c05eeee7b43dd694506b5efe963c771461b7e690bc62f409947b2306b7d77'
original=json.loads((root/'ORIGINAL-GATE-DECLARATION.json').read_text())
assert original['cases'][0]['fresh_census_label']==label and original['fresh_gate']['batches_per_source']==32768
jobs=[];logs=[]
for role,ops in [('parent',parent),('candidate',tree/'ops.bin'),('reference753721',new_reference)]:
 path=dest/f'{role}-census.jsonl';assert not path.exists(),'never resample or overwrite the sole gate'
 log=(dest/f'{role}-census.log').open('w');logs.append(log)
 job=subprocess.Popen([str(runner),str(ops),label,'0','32768','1',str(path),'0'],stdout=log,stderr=subprocess.STDOUT);jobs.append(job)
 (dest/f'{role}-census.pid').write_text(str(job.pid)+'\n')
codes=[job.wait() for job in jobs]
for log in logs:log.close()
assert codes==[0,0,0],codes
rows=[]
for role in ['parent','candidate']:
 data=[json.loads(line) for line in (dest/f'{role}-census.jsonl').read_text().splitlines()]
 assert len(data)==32768 and sorted(r['batch'] for r in data)==list(range(32768)) and all(r['shots']==64 and r['skipped']==0 for r in data)
 rows.append({r['batch']:r for r in data})
a,b=rows;delta=[(a[i]['toffoli']-b[i]['toffoli'])/64 for i in range(32768)];mean=sum(delta)/len(delta)
fail=[sum(bool(r['failures']) for r in data.values()) for data in rows];dirty=[sum(r['dirty_shots'] for r in data.values()) for data in rows]
summary={'status':'FRESH_CENSUS_COMPLETE_NOT_A_RESOURCE_RECORD','name':'wide2048','label':label,'batches_each':32768,'shots_each':2097152,'failed_batches':dict(zip(['parent','candidate'],fail)),'failures_per_packet':dict(zip(['parent','candidate'],[141*f/32768 for f in fail])),'dirty_shots':dirty,'paired_mean_T_saving':mean,'saving_standard_error':math.sqrt(sum((x-mean)**2 for x in delta)/(len(delta)*(len(delta)-1))),'failure_gate_pass':fail[1]<=fail[0] and 141*fail[1]/32768<=18 and dirty[1]==0,'nonce_search_performed':False}
(dest/'census-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
reference=[json.loads(line) for line in (dest/'reference753721-census.jsonl').read_text().splitlines()]
assert len(reference)==32768 and sorted(r['batch'] for r in reference)==list(range(32768)) and all(r['shots']==64 and r['skipped']==0 for r in reference)
ref_fail=sum(bool(r['failures']) for r in reference);ref_dirty=sum(r['dirty_shots'] for r in reference)
check={'status':'SAME_FIXED_SAMPLE_COMPARISON_AGAINST_COMPLETE753721_REFERENCE','label':label,'reference_sha256':'1d8c05eeee7b43dd694506b5efe963c771461b7e690bc62f409947b2306b7d77','reference_failed_batches':ref_fail,'reference_dirty_shots':ref_dirty,'candidate_failed_batches':fail[1],'failure_gate_pass':summary['failure_gate_pass'] and fail[1]<=ref_fail,'candidate_rows_reused_without_resampling':True,'not_an_official_validation_claim':True}
(dest/'reference753721-comparison.json').write_text(json.dumps(check,indent=2)+'\n');print(json.dumps(check,indent=2))
