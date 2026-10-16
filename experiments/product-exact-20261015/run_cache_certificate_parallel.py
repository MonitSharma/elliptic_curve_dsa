"""Independent complete deterministic rerun of the25 stage audits, four workers."""
import concurrent.futures,copy,hashlib,json,os,resource,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'cache-certificate-parallel-20261016';d.mkdir(exist_ok=True)
plan=copy.deepcopy(json.loads((r/'cache-certificate-20261016/PLAN.json').read_text()))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
exe=r/'target-cache-certificate/release/product_paired_diagnostic';assert sha(exe)==plan['verifier_executable_sha256']
plan.update(workers=4,per_worker_address_limit_GiB=6,scope='Independent deterministic verification rerun; every original25 stage/config/input/output/log retained, no random inputs or samples.')
for row in plan['stages']:
    row['status']='not launched'
    for key,hashkey in [('input_stream','input_sha256'),('output_stream','output_sha256'),('lease_log','lease_log_sha256')]:assert sha(r/row[key])==row[hashkey]
(d/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
def limit():resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
def audit(row):
    env=os.environ.copy();env.update(CACHE_ATOM_CAP=str(row['atom_cap']),CACHE_PRODUCT_CAP='1000000',ANF_PAIR_CAP='64',RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1')
    out=d/f"stage-{row['stage']:02d}.log"
    with out.open('wb') as f:p=subprocess.run([str(exe),str(r/row['input_stream']),str(r/row['output_stream']),str(r/row['lease_log']),row['family']],stdout=f,stderr=subprocess.STDOUT,env=env,preexec_fn=limit)
    row.update(status='PASS' if p.returncode==0 else 'FAIL',returncode=p.returncode,audit_log=str(out.relative_to(r)),audit_log_sha256=sha(out))
    return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    futures=[pool.submit(audit,row) for row in plan['stages']]
    for future in concurrent.futures.as_completed(futures):
        row=future.result();print('STAGE',row['stage'],row['status'],flush=True)
        (d/'RECEIPT.json').write_text(json.dumps(plan,indent=2)+'\n')
assert all(x['status']=='PASS' for x in plan['stages'])
plan['status']='UNIVERSAL_CACHE_CHAIN_PASS';(d/'RECEIPT.json').write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps({'status':plan['status'],'stages':25,'baseline_stream_sha256':plan['baseline_stream_sha256'],'candidate_stream_sha256':plan['candidate_stream_sha256']}),flush=True)
