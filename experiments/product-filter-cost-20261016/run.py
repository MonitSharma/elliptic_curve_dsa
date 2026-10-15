from pathlib import Path
import hashlib,json,os,subprocess,time
root=Path(__file__).resolve().parent;freeze=json.loads((root.parent/'masked-witness-20261016/MASK_FREEZE.json').read_text())
env=os.environ.copy();env['MASK_DAG_PATH']=freeze['mask_path'];env['MASK_DAG_SHA256']=freeze['mask_sha256']
assert hashlib.sha256(Path(env['MASK_DAG_PATH']).read_bytes()).hexdigest()==env['MASK_DAG_SHA256']
ops='/home/hclau/ecdsa_research/product-exact-20261015/candidate-product-final25/ops.bin';model='/home/hclau/ecdsa_research/prefilter-20261015/model-source'
jobs=[];start=time.perf_counter()
for worker in range(4):
 name=f'worker{worker}';out=(root/(name+'.log')).open('w');err=(root/(name+'.err')).open('w');first=1+worker*65536
 job=subprocess.Popen([str(root/'tool/target/release/value_prefilter'),ops,str(first),'65536','12',str(root/(name+'.jsonl')),model,'4096'],env=env,stdout=out,stderr=err);jobs.append((worker,job,out,err))
 (root/(name+'.pid')).write_text(str(job.pid)+'\n')
for worker,job,out,err in jobs:
 code=job.wait();out.close();err.close();(root/f'worker{worker}.exit').write_text(str(code)+'\n');assert code==0
summary=[]
for worker in range(4):
 rows=[json.loads(s) for s in (root/f'worker{worker}.jsonl').read_text().splitlines()]
 first=1+worker*65536;assert len(rows)==65536 and sorted(r['nonce'] for r in rows)==list(range(first,first+65536))
 assert all(not r['authoritative_rejection'] and not r['proof_accepted'] for r in rows)
 summary.append({'worker':worker,'first':first,'count':len(rows),'observed_full_pass_controls':[r['nonce'] for r in rows if r.get('candidate_full_fallback_pass')]})
report={'status':'BOUNDED_FOUR_PROCESS_COST_MEASUREMENT_PASS','processes':4,'threads_each':12,'nonce_count':262144,'wall_including_four_startups_seconds':time.perf_counter()-start,'workers':summary,'authoritative_rejection':False,'nonce_selected':False}
(root/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
