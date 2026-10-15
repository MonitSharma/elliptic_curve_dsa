from pathlib import Path
import hashlib,json,math,subprocess,sys
root=Path(__file__).resolve().parent;name=sys.argv[1];dest=root/name;tree=dest/'candidate'
freeze=json.loads((dest/'DECLARATION.json').read_text())
assert hashlib.sha256((tree/'ops.bin').read_bytes()).hexdigest()==freeze['expected_normal_generated_stream_sha256']
assert '4 passed; 0 failed' in (dest/'native-tests.log').read_text()
if name=='product53':
 # This file has not yet run. Another agent already launched the identical
 # predeclared label/range on the frozen external stream. Reuse all its rows
 # after native byte identity; do not launch a second sample or select rates.
 record={'status':'NATIVE_BYTE_IDENTITY_PASS_CENSUS_ALREADY_RUNNING_ELSEWHERE','expected_stream_sha256':freeze['expected_normal_generated_stream_sha256'],'reuse_entire_fixed_sample':'product-exact-20261015/product53-frozen-census-20261016','batches_each':32768,'label':'product53-frozen-20261016','workers_each_actual':8,'original_duplicate_workers_each':6,'nonce_search_performed':False}
 (dest/'census-reuse.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2));sys.exit(0)
runner=root.parent/'simd-census-v2-20261016/bin/simd_census_v2'
assert hashlib.sha256(runner.read_bytes()).hexdigest()=='790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66'
parent=root.parent/('product-exact-20261015/tip/ops.bin' if name=='product53' else 'nonce-screen-20261015/final-census/ops.bin')
jobs=[];logs=[]
for role,ops in [('parent',parent),('candidate',tree/'ops.bin')]:
 log=(dest/f'{role}-census.log').open('w');logs.append(log)
 job=subprocess.Popen([str(runner),str(ops),name+'-frozen-20261016','0','32768','6',str(dest/f'{role}-census.jsonl'),'0'],stdout=log,stderr=subprocess.STDOUT);jobs.append(job)
 (dest/f'{role}-census.pid').write_text(str(job.pid)+'\n')
codes=[job.wait() for job in jobs]
for log in logs:log.close()
assert codes==[0,0],codes
rows=[]
for role in ['parent','candidate']:
 data=[json.loads(line) for line in (dest/f'{role}-census.jsonl').read_text().splitlines()]
 assert len(data)==32768 and sorted(r['batch'] for r in data)==list(range(32768)) and all(r['shots']==64 for r in data)
 rows.append({r['batch']:r for r in data})
a,b=rows;delta=[(a[i]['toffoli']-b[i]['toffoli'])/64 for i in range(32768)];mean=sum(delta)/len(delta)
fail=[sum(bool(r['failures']) for r in data.values()) for data in rows]
dirty=[sum(r['dirty_shots'] for r in data.values()) for data in rows]
summary={'status':'FRESH_CENSUS_COMPLETE_NOT_A_RESOURCE_RECORD','name':name,'batches_each':32768,'shots_each':2097152,'label':name+'-frozen-20261016','failed_batches':dict(zip(['parent','candidate'],fail)),'failures_per_packet':dict(zip(['parent','candidate'],[141*f/32768 for f in fail])),'dirty_shots':dirty,'paired_mean_T_saving':mean,'saving_standard_error':math.sqrt(sum((x-mean)**2 for x in delta)/(len(delta)*(len(delta)-1))),'failure_gate_pass':fail[1]<=fail[0] and 141*fail[1]/32768<=18 and dirty[1]==0,'nonce_search_performed':False}
(dest/'census-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
