"""Source-bound retry of only deterministic memory-exhausted proof stages."""
import concurrent.futures,copy,hashlib,json,os,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;old=r/'cache-certificate-parallel-20261016';d=r/'cache-certificate-retry-20261016';d.mkdir(exist_ok=True)
assert (old/'launcher.exit').exists() and (r/'wide43-scratch-20261016/launcher.exit').exists()
available=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024
assert available>=200*1024**3,'Require at least200GiB available before audit retries'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=copy.deepcopy(json.loads((old/'RECEIPT.json').read_text()));exe=r/'target-cache-certificate/release/product_paired_diagnostic';assert sha(exe)==plan['verifier_executable_sha256']
retry=[]
for row in plan['stages']:
    for k,h in [('input_stream','input_sha256'),('output_stream','output_sha256'),('lease_log','lease_log_sha256')]:assert sha(r/row[k])==row[h]
    audit=r/row['audit_log'];assert sha(audit)==row['audit_log_sha256']
    if row['status']=='PASS':assert 'UNIVERSAL_CACHE_CERTIFICATE_PASS' in audit.read_text();row['proof_origin']='verified complete deterministic prior audit'
    else:
        assert row['returncode'] in [-6,-9,101] and 'memory allocation' in audit.read_text(),'Only explicit memory failures are retried; semantic failures require investigation'
        row['prior_resource_failure']=copy.deepcopy({k:row[k] for k in ['returncode','audit_log','audit_log_sha256']});row['status']='not launched';retry.append(row)
plan.update(workers=4,per_worker_address_limit_GiB=12,available_at_launch_bytes=available,prior_receipt_sha256=sha(old/'RECEIPT.json'),status='incomplete resource retries',scope='Every original25 stage retained. Passing deterministic certificates reused with all source/log/executable hashes checked; only explicit memory-exhausted checks rerun at a larger resource cap. No simulated inputs or samples.')
(d/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
def run(row):
    env=os.environ.copy();env.update(CACHE_ATOM_CAP=str(row['atom_cap']),CACHE_PRODUCT_CAP='1000000',ANF_PAIR_CAP='64',RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1')
    out=d/f"stage-{row['stage']:02d}.log"
    with out.open('wb') as f:proc=subprocess.run(['prlimit','--as='+str(12*1024**3),'--',str(exe),str(r/row['input_stream']),str(r/row['output_stream']),str(r/row['lease_log']),row['family']],stdout=f,stderr=subprocess.STDOUT,env=env)
    row.update(status='PASS' if proc.returncode==0 else 'FAIL',returncode=proc.returncode,audit_log=str(out.relative_to(r)),audit_log_sha256=sha(out),proof_origin='larger-cap deterministic memory retry')
    return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for future in concurrent.futures.as_completed([pool.submit(run,row) for row in retry]):
        row=future.result();print('STAGE',row['stage'],row['status'],flush=True);(d/'RECEIPT.json').write_text(json.dumps(plan,indent=2)+'\n')
assert all(x['status']=='PASS' for x in plan['stages'])
plan['status']='UNIVERSAL_CACHE_CHAIN_PASS';(d/'RECEIPT.json').write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps({'status':plan['status'],'stages':25,'retried_stages':len(retry),'baseline_stream_sha256':plan['baseline_stream_sha256'],'candidate_stream_sha256':plan['candidate_stream_sha256']}),flush=True)
