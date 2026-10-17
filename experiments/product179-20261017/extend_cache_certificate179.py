"""Append universal source-bound audits for stages 96..179 to the complete universal95 certificate."""
import concurrent.futures,copy,filecmp,hashlib,json,os,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'cache-certificate179-20261017';d.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original=r/'cache-certificate95-20261017/CACHE_EQUIVALENCE_CERTIFICATE.json'
assert sha(original)=='f3af2e4d3275f9b39fa34ad61d8a000f166935eb4f7236ac28a5cd2032dc27ad'
exe=r/'target-cache-certificate-v2/release/product_paired_diagnostic';assert sha(exe)=='2e9f5ee6ed4ea1fa5b625f38298a71e05ce885778db7aed1064b23d2ee657091'
if sys.argv[1]=='prepare':
    assert not (d/'PLAN.json').exists()
    freeze=json.loads((r/'PRODUCT179_FREEZE.json').read_text());old=json.loads((r/'cache-certificate95-20261017/RECEIPT.json').read_text())
    lines=[line.split() for line in (r/freeze['chain_manifest']).read_text().splitlines()];assert len(lines)==179
    previous='tip/ops.bin';stages=[]
    for i,((output,log),config) in enumerate(zip(lines,freeze['stages']),1):
        if i<=95:
            prior=None if i<=67 else old['stages'][i-68]
            if prior is not None:assert previous==prior['input_stream'] and output==prior['output_stream'];assert sha(r/previous)==prior['input_sha256'] and sha(r/output)==prior['output_sha256']
        else:
            stages.append({'stage':i,'family':config['family'],'atom_cap':config['atom_cap'],'config':config,'input_stream':previous,'input_sha256':sha(r/previous),'output_stream':output,'output_sha256':sha(r/output),'lease_log':log,'lease_log_sha256':sha(r/log) if log!='=' else None,'status':'not launched'})
        previous=output
    assert stages[0]['input_sha256']==old['candidate_stream_sha256']
    assert stages[-1]['output_sha256']==freeze['external_stream_sha256']
    plan={'status':'PREPARED_NOT_LAUNCHED','prior_certificate_sha256':sha(original),'prior_receipt_sha256':sha(r/'cache-certificate95-20261017/RECEIPT.json'),'source_freeze_sha256':sha(r/'PRODUCT179_FREEZE.json'),'baseline_stream_sha256':old['baseline_stream_sha256'],'candidate_stream_sha256':freeze['external_stream_sha256'],'verifier_executable_sha256':sha(exe),'kernel_sha256':old['kernel_sha256'],'workers':4,'per_worker_address_limit_GiB':12,'no_simulated_inputs':True,'scope':'Universal audit of fixed179 via completed universal95 certificate plus every freshly verified stage96..179; preserve all failures. Same trusted conservative immutable Boolean kernels and HMR/CZ gadget theorem; not a proof assistant. No assertion of global MR independence.','stages':stages}
    (d/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('PREPARED84_APPENDED_STAGES',flush=True)
elif sys.argv[1]=='run':
    assert not (d/'RECEIPT.json').exists();plan=copy.deepcopy(json.loads((d/'PLAN.json').read_text()))
    available=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024;assert available>=200*1024**3
    plan.update(status='INCOMPLETE',available_at_launch_bytes=available)
    def run(row):
        assert sha(r/row['input_stream'])==row['input_sha256'] and sha(r/row['output_stream'])==row['output_sha256']
        out=d/f"stage-{row['stage']:02d}.log"
        if row['lease_log']=='=':
            assert filecmp.cmp(r/row['input_stream'],r/row['output_stream'],shallow=False);out.write_text('UNIVERSAL_BYTE_IDENTITY_PASS\n');rc=0
        else:
            assert sha(r/row['lease_log'])==row['lease_log_sha256']
            env=os.environ.copy();env.update(CACHE_ATOM_CAP=str(row['atom_cap']),CACHE_PRODUCT_CAP='1000000',ANF_PAIR_CAP='64',RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1')
            with out.open('wb') as f:rc=subprocess.run(['prlimit','--as='+str(12*1024**3),'--',str(exe),str(r/row['input_stream']),str(r/row['output_stream']),str(r/row['lease_log']),row['family']],stdout=f,stderr=subprocess.STDOUT,env=env).returncode
        row.update(status='PASS' if rc==0 else 'FAIL',returncode=rc,audit_log=str(out.relative_to(r)),audit_log_sha256=sha(out));return row
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for future in concurrent.futures.as_completed([pool.submit(run,row) for row in plan['stages']]):
            row=future.result();print('STAGE',row['stage'],row['status'],flush=True);(d/'RECEIPT.json').write_text(json.dumps(plan,indent=2)+'\n')
    assert all(x['status']=='PASS' for x in plan['stages']);plan['status']='UNIVERSAL179_CHAIN_PASS';(d/'RECEIPT.json').write_text(json.dumps(plan,indent=2)+'\n');print(plan['status'],flush=True)
else:raise ValueError(sys.argv[1])
