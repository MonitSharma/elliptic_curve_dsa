"""Run only the already declared complete census after the shared CPU release."""
import hashlib,json,math,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'repair67-native-20261016';tree=d/'candidate';native=tree/'ops.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();freeze=json.loads((r/'REPAIR67_FREEZE.json').read_text());plan=json.loads((r/'REPAIR67_FRESH_CENSUS_PLAN.json').read_text());receipt=json.loads((d/'NATIVE_RECEIPT.json').read_text())
assert (d/'launcher.exit').read_text().strip()=='0' and receipt['status']=='NATIVE_REPAIRED67_SOURCE_AND_BYTE_IDENTITY_PASS'
assert sha(native)==receipt['native_stream_sha256']==freeze['external_stream_sha256']
for rel,h in receipt['source_files_sha256'].items():assert sha(tree/'src/point_add'/rel)==h
for rel,h in receipt['protected_files_sha256'].items():assert sha(tree/rel)==h
assert sha(d/'point-add-source.tar.gz')==(d/'source-archive-sha256.txt').read_text().split()[0]
runner=Path(plan['runner']);assert sha(runner)==plan['runner_sha256'];assert sha(r/plan['original_reference_stream'])==plan['original_reference_sha256']
assert plan['batches_per_source']==32768 and plan['first_batch']==0 and plan['last_batch']==32767
for role,ops in [('parent',r/plan['original_reference_stream']),('candidate',native)]:
    out=d/f'{role}-census.jsonl';assert not out.exists()
    with (d/f'{role}-census-preflight.json').open('w') as f:subprocess.run(['python3','/home/hclau/ecdsa_research/server-preflight.py'],stdout=f,check=True)
    with (d/f'{role}-census.log').open('w') as log:
        p=subprocess.Popen([str(runner),str(ops),plan['label'],'0','32768','8',str(out),'0'],stdout=log,stderr=subprocess.STDOUT);(d/f'{role}-census.pid').write_text(str(p.pid)+'\n');rc=p.wait()
    (d/f'{role}-census.exit').write_text(str(rc)+'\n');assert rc==0
rows=[]
for role in ['parent','candidate']:
    data=[json.loads(line) for line in (d/f'{role}-census.jsonl').read_text().splitlines()];assert len(data)==32768 and sorted(row['batch'] for row in data)==list(range(32768)) and all(row['shots']==64 for row in data);rows.append({row['batch']:row for row in data})
a,b=rows;delta=[(a[i]['toffoli']-b[i]['toffoli'])/64 for i in range(32768)];mean=sum(delta)/len(delta);fail=[sum(bool(row['failures']) for row in data.values()) for data in rows];dirty=[sum(row['dirty_shots'] for row in data.values()) for data in rows]
summary={'status':'COMPLETE_FIXED_CENSUS_NOT_A_RESOURCE_RECORD','label':plan['label'],'batches_each':32768,'shots_each':2097152,'parent_sha256':plan['original_reference_sha256'],'candidate_sha256':freeze['external_stream_sha256'],'failed_batches':dict(zip(['parent','candidate'],fail)),'failures_per_packet':dict(zip(['parent','candidate'],[141*f/32768 for f in fail])),'dirty_shots':dirty,'paired_mean_T_saving':mean,'saving_standard_error':math.sqrt(sum((x-mean)**2 for x in delta)/(len(delta)*(len(delta)-1))),'failure_gate_pass':fail[1]<=fail[0] and 141*fail[1]/32768<=18 and dirty[1]==0,'workers_each':8,'source_jobs_sequential_for_global_thread_cap':True,'runner_sha256':sha(runner),'all_declared_rows_retained':True,'nonce_search_performed':False,'score':None}
(d/'census-summary.json').write_text(json.dumps(summary,indent=2)+'\n');(r/'repair67-census-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
