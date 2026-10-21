"""Fixed, input-independent 84-stage product research with per-stage audits."""
import concurrent.futures, hashlib, json, os, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
root=Path(__file__).resolve().parent
run=root/'continuation84';run.mkdir(exist_ok=False)
old=Path('/home/hclau/ecdsa_research/product-exact-20261015')
generator=old/'target-flags/release/product_paired_diagnostic'
verifier=old/'target-cache-certificate-v2/release/product_paired_diagnostic'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(generator)=='3a556985ea1521e950e8f57326e349687fbbb7af3536f668e5fb366137b3f434'
assert sha(verifier)=='2e9f5ee6ed4ea1fa5b625f38298a71e05ce885778db7aed1064b23d2ee657091'
assert (root/'pilot.exit').read_text().strip()=='0'
previous=root/'parent-unwrapped-retained.ops.bin'
pilot=json.loads((root/'pilot-parent/DECLARATION.json').read_text());assert sha(previous)==pilot['streams']['retained']['sha256']
cycle=[('retained',128,'start'),('retained',512,'proxy'),('retained',1024,'start'),('anf',512,'proxy'),('retained',128,'proxy'),('retained',512,'start'),('retained',1024,'proxy')]
plan={'declared_at_utc':datetime.now(timezone.utc).isoformat(),'status':'DECLARED_BEFORE_GENERATION',
 'objective':'Lower complete Q*T at Q1234; exact changes only. Fixed endpoint, no packet-dependent selection.',
 'base_public_commit':'0c3a0751ab66bd9144358d67563bcb79201cf636','public_parent_sha256':'99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683',
 'input_path':str(previous),'input_sha256':sha(previous),'stage_count':84,
 'stages':[{'stage':i+1,'family':family,'atom_cap':cap,'rank':rank} for i,(family,cap,rank) in enumerate(cycle*12)],
 'generator_sha256':sha(generator),'verifier_sha256':sha(verifier),
 'resources':{'generator_threads':1,'concurrent_audits':2,'audit_threads_each':1,'minimum_available_memory_GiB':100},
 'nonce_search':False,'submission':False}
(run/'DECLARATION.json').write_text(json.dumps(plan,indent=2)+'\n')
records=[];pending=[]
def memory_guard():
    while True:
        available=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024
        if available>=180*1024**3:return available
        print('WAIT_MEMORY',available,flush=True);time.sleep(30)
def audit(row):
    memory_guard();env=os.environ.copy();env.update(CACHE_ATOM_CAP=str(row['atom_cap']),CACHE_PRODUCT_CAP='1000000',ANF_PAIR_CAP='64',RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1')
    log=run/f"stage-{row['stage']:03d}-audit.log"
    if row['input_sha256']==row['output_sha256']:
        assert Path(row['input']).read_bytes()==Path(row['output']).read_bytes()
        log.write_text('UNIVERSAL_BYTE_IDENTITY_PASS\n')
        row.update(audit_returncode=0,audit_log=str(log),audit_log_sha256=sha(log),audit_status='PASS',audit_scope='byte identity')
        (run/f"stage-{row['stage']:03d}-receipt.json").write_text(json.dumps(row,indent=2)+'\n');print('AUDIT',row['stage'],'BYTE_IDENTITY_PASS',flush=True);return row
    with log.open('wb') as out:
        rc=subprocess.run(['prlimit','--as='+str(16*1024**3),'--',str(verifier),row['input'],row['output'],row['generation_log'],row['family']],stdout=out,stderr=subprocess.STDOUT,env=env).returncode
    text=log.read_text(errors='replace')
    row.update(audit_returncode=rc,audit_log=str(log),audit_log_sha256=sha(log))
    row['audit_status']='PASS' if rc==0 and 'UNIVERSAL_CACHE_CERTIFICATE_PASS' in text and 'independent_zero_and_product_passes=true' in text else 'FAIL'
    (run/f"stage-{row['stage']:03d}-receipt.json").write_text(json.dumps(row,indent=2)+'\n')
    print('AUDIT',row['stage'],row['audit_status'],flush=True)
    assert row['audit_status']=='PASS',row
    return row
try:
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for spec in plan['stages']:
            for task in pending:
                if task.done():task.result()
            memory_guard();i=spec['stage'];output=run/f'stage-{i:03d}.ops.bin';log=run/f'stage-{i:03d}-generate.log'
            env=os.environ.copy();env.update(EXACT_MODE='cache-'+spec['family'],CACHE_ATOM_CAP=str(spec['atom_cap']),ANF_PAIR_CAP='64',CACHE_PRODUCT_CAP='1000000',CACHE_SPLIT='1',CACHE_RANK=spec['rank'],RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
            row=dict(spec,input=str(previous),input_sha256=sha(previous),output=str(output),generation_log=str(log))
            print('GENERATING',i,flush=True)
            with log.open('wb') as out:
                subprocess.run(['prlimit','--as='+str(32*1024**3),'--','/usr/bin/time','-v',str(generator),str(previous),str(output)],stdout=out,stderr=subprocess.STDOUT,env=env,check=True)
            row.update(output_sha256=sha(output),generation_log_sha256=sha(log));records.append(row)
            (run/'PROGRESS.json').write_text(json.dumps({'generated_stages':i,'fixed_endpoint':84,'latest_stream':str(output),'latest_sha256':row['output_sha256']},indent=2)+'\n')
            pending.append(pool.submit(audit,row));previous=output
        verified=[task.result() for task in pending]
    result={'status':'ALL_84_EXACT_CACHE_AUDITS_PASS','input_sha256':plan['input_sha256'],'output':str(previous),'output_sha256':sha(previous),'stages':verified,'no_nonce_search':True,'no_scored_result':True}
    (run/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],flush=True)
except BaseException as exc:
    (run/'FAILED.json').write_text(json.dumps({'status':'STOPPED_ON_FAILURE','error':repr(exc),'generated_stages':len(records)},indent=2)+'\n');raise
