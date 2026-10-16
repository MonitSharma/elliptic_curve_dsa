"""Bind every universal stage audit to complete immutable source and log hashes."""
import hashlib,json,os,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'cache-certificate-20261016';d.mkdir(exist_ok=True)
freeze=json.loads((r/'PRODUCT25_FREEZE.json').read_text());rows=(r/'product-continuation-20261016/stage-25.manifest').read_text().splitlines();assert len(rows)==25
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
exe=r/'target-cache-certificate/release/product_paired_diagnostic';previous=r/'tip/ops.bin'
assert sha(previous)=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
plan={'base_revision':freeze['base_revision'],'baseline_stream_sha256':sha(previous),'candidate_stream_sha256':freeze['external_stream_sha256'],'stage_count':25,'nonce':1046072871510,'score':None,'no_simulated_inputs':True,'trusted_base':'Conservative immutable Boolean Support kernels plus HMR/CZ lazy-cache gadget theorem; no external formal proof assistant','obligations':['all ABI quantum/classical inputs symbolic; every MR fresh independent symbol','product equality at every proposed use','donor identically zero at lease start','no input quantum read/phase/write on donor except zero reset inside lease','last controls unchanged through cleanup','top-level fresh/private flag resets and disjoint reuse intervals','exact every output row including guards, HMR/CZ phase twin, suffix and original ABI'],'source_freeze_sha256':sha(r/'PRODUCT25_FREEZE.json'),'verifier_executable_sha256':sha(exe),'kernel_sha256':{n:sha(r/'cache-certificate-tool/src'/n) for n in ['interned_witness.rs','interned_anf.rs','interned_anf_retained.rs','cache_certificate.rs']},'stages':[]}
for i,(line,spec) in enumerate(zip(rows,freeze['stages']),1):
    candidate,log=line.split();assert log!='=';candidate=r/candidate;log=r/log
    row={'stage':i,'family':spec['family'],'atom_cap':spec['atom_cap'],'input_stream':str(previous.relative_to(r)),'input_sha256':sha(previous),'output_stream':str(candidate.relative_to(r)),'output_sha256':sha(candidate),'lease_log':str(log.relative_to(r)),'lease_log_sha256':sha(log),'config':spec,'status':'not launched'}
    plan['stages'].append(row);(d/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');previous=candidate
assert plan['stages'][-1]['output_sha256']==freeze['external_stream_sha256']=='180af069679ffa33b099b200d3337d6fc6c20a451a72508a40dea6617150dc64'
for row in plan['stages']:
    env=os.environ.copy();env.update(CACHE_ATOM_CAP=str(row['atom_cap']),CACHE_PRODUCT_CAP='1000000',ANF_PAIR_CAP='64',RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1')
    out=d/f"stage-{row['stage']:02d}.log"
    with out.open('wb') as stream:
        proc=subprocess.run([str(exe),str(r/row['input_stream']),str(r/row['output_stream']),str(r/row['lease_log']),row['family']],stdout=stream,stderr=subprocess.STDOUT,env=env)
    row.update(status='PASS' if proc.returncode==0 else 'FAIL',returncode=proc.returncode,audit_log=str(out.relative_to(r)),audit_log_sha256=sha(out))
    (d/'RECEIPT.json').write_text(json.dumps(plan,indent=2)+'\n');assert proc.returncode==0,f"stage{row['stage']} universal audit failed"
assert all(x['status']=='PASS' for x in plan['stages']);plan['status']='UNIVERSAL_CACHE_CHAIN_PASS'
(d/'RECEIPT.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps({'status':plan['status'],'stages':25,'baseline_stream_sha256':plan['baseline_stream_sha256'],'candidate_stream_sha256':plan['candidate_stream_sha256']}))
