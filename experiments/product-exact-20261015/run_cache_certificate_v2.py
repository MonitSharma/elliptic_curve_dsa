"""Complete deterministic25-stage audit with separate universal proof passes."""
import concurrent.futures,copy,hashlib,json,os,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'cache-certificate-v2-20261016';d.mkdir(exist_ok=True)
available=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024;assert available>=200*1024**3
plan=copy.deepcopy(json.loads((r/'cache-certificate-20261016/PLAN.json').read_text()))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
exe=r/'target-cache-certificate-v2/release/product_paired_diagnostic'
plan.update(workers=3,per_worker_address_limit_GiB=16,available_at_launch_bytes=available,verifier_executable_sha256=sha(exe),scope='Complete fresh deterministic audit of all25 frozen stages; separate step-only zero proof and query-aware product proof; no simulated inputs or sampled packets.',status='incomplete')
plan['kernel_sha256']={n:sha(r/'cache-certificate-v2-tool/src'/n) for n in plan['kernel_sha256']}
for row in plan['stages']:
    row.update(status='not launched',returncode=None,audit_log=None,audit_log_sha256=None)
    for key,h in [('input_stream','input_sha256'),('output_stream','output_sha256'),('lease_log','lease_log_sha256')]:assert sha(r/row[key])==row[h]
(d/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
def run(row):
    env=os.environ.copy();env.update(CACHE_ATOM_CAP=str(row['atom_cap']),CACHE_PRODUCT_CAP='1000000',ANF_PAIR_CAP='64',RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1')
    out=d/f"stage-{row['stage']:02d}.log"
    with out.open('wb') as f:p=subprocess.run(['prlimit','--as='+str(16*1024**3),'--',str(exe),str(r/row['input_stream']),str(r/row['output_stream']),str(r/row['lease_log']),row['family']],stdout=f,stderr=subprocess.STDOUT,env=env)
    row.update(status='PASS' if p.returncode==0 else 'FAIL',returncode=p.returncode,audit_log=str(out.relative_to(r)),audit_log_sha256=sha(out));return row
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    for future in concurrent.futures.as_completed([pool.submit(run,row) for row in plan['stages']]):
        row=future.result();print('STAGE',row['stage'],row['status'],flush=True);(d/'RECEIPT.json').write_text(json.dumps(plan,indent=2)+'\n')
assert all(x['status']=='PASS' for x in plan['stages'])
plan['status']='UNIVERSAL_CACHE_CHAIN_PASS';(d/'RECEIPT.json').write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps({'status':plan['status'],'stages':25,'baseline_stream_sha256':plan['baseline_stream_sha256'],'candidate_stream_sha256':plan['candidate_stream_sha256']}),flush=True)
