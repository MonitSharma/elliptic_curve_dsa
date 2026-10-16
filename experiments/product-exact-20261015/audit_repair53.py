"""Audit every fresh53 cache stage relative to corrected A29, not original4b."""
import concurrent.futures,copy,filecmp,hashlib,json,os,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'repair53-universal-20261016';d.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
exe=r/'target-cache-certificate-v2/release/product_paired_diagnostic';assert sha(exe)=='2e9f5ee6ed4ea1fa5b625f38298a71e05ce885778db7aed1064b23d2ee657091'
trusted=r/'cache-certificate-v2-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json';assert sha(trusted)=='4857f8255c6aa85f0c6cb84720c6d5690aaca060f2758a8c517bd43fc5e2f04e';old=json.loads(trusted.read_text())
sources={str(p.relative_to(r/'cache-certificate-v2-tool')):sha(p) for p in (r/'cache-certificate-v2-tool').rglob('*') if p.is_file() and 'target' not in p.relative_to(r/'cache-certificate-v2-tool').parts};assert sources==old['source_files_sha256']
if sys.argv[1]=='prepare':
    assert not (d/'PLAN.json').exists();freeze=json.loads((r/'REPAIR53_FREEZE.json').read_text());assert len(freeze['stages'])==53
    assert sha(r/'wide-largecaps-20261016/launcher.exit')==hashlib.sha256(b'0\n').hexdigest()
    lines=[x.split() for x in (r/freeze['chain_manifest']).read_text().splitlines()];assert len(lines)==53
    previous=freeze['repair_parent_stream'];assert sha(r/previous)==freeze['repair_parent_sha256'];stages=[]
    for i,((output,log),config) in enumerate(zip(lines,freeze['stages']),1):
        stages.append({'stage':i,'family':config['family'],'atom_cap':config['atom_cap'],'config':config,'input_stream':previous,'input_sha256':sha(r/previous),'output_stream':output,'output_sha256':sha(r/output),'lease_log':log,'lease_log_sha256':sha(r/log) if log!='=' else None,'status':'not launched'});previous=output
    assert stages[-1]['output_sha256']==freeze['external_stream_sha256']
    plan={'status':'PREPARED_NOT_LAUNCHED','baseline_stream_sha256':freeze['repair_parent_sha256'],'candidate_stream_sha256':freeze['external_stream_sha256'],'source_freeze_sha256':sha(r/'REPAIR53_FREEZE.json'),'native_receipt_sha256':sha(r/'repair53-native-20261016/NATIVE_RECEIPT.json'),'source_files_sha256':sources,'verifier_executable_sha256':sha(exe),'trusted_kernel_reference_certificate_sha256':sha(trusted),'trusted_base':old['trusted_base'],'protected_dependency_revision':old['protected_dependency_revision'],'protected_dependency_files_sha256':old['protected_dependency_files_sha256'],'workers':2,'per_worker_address_limit_GiB':12,'no_simulated_inputs':True,'scope':'All53 independently verified cache stages relative to corrected A29 source1cd3457b, with every original A29 ABI input and MR assignment. Reuses only immutable verifier/kernel provenance from original4b audit, not its equivalence or value-mask theorem. No original4b coordinate-function transfer and no global MR-independence claim. Conditional per-input masks need a separate sound A29 source-bound model. Preserve resource/proof failures; native full-byte and fixed fresh gate are independent completed evidence.','stages':stages}
    (d/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('PREDECLARED_ALL53_A29_RELATIVE_UNIVERSAL_AUDITS',flush=True)
elif sys.argv[1]=='run':
    assert not (d/'RECEIPT.json').exists();plan=copy.deepcopy(json.loads((d/'PLAN.json').read_text()));assert sources==plan['source_files_sha256']
    available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024;assert available>=200*1024**3
    plan.update(status='INCOMPLETE',available_at_launch_bytes=available)
    def run(row):
        assert sha(r/row['input_stream'])==row['input_sha256'] and sha(r/row['output_stream'])==row['output_sha256'];out=d/f"stage-{row['stage']:02d}.log"
        if row['lease_log']=='=':
            assert filecmp.cmp(r/row['input_stream'],r/row['output_stream'],shallow=False);out.write_text('UNIVERSAL_BYTE_IDENTITY_PASS\n');rc=0
        else:
            assert sha(r/row['lease_log'])==row['lease_log_sha256'];config=row['config'];env=os.environ.copy();env.update(CACHE_ATOM_CAP=str(row['atom_cap']),CACHE_PRODUCT_CAP=str(config.get('product_cap',1000000)),ANF_PAIR_CAP=str(config.get('pair_cap',64)),RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1')
            with out.open('wb') as f:rc=subprocess.run(['prlimit','--as='+str(12*1024**3),'--',str(exe),str(r/row['input_stream']),str(r/row['output_stream']),str(r/row['lease_log']),row['family']],stdout=f,stderr=subprocess.STDOUT,env=env).returncode
        row.update(status='PASS' if rc==0 else 'FAIL',returncode=rc,audit_log=str(out.relative_to(r)),audit_log_sha256=sha(out));return row
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for future in concurrent.futures.as_completed([pool.submit(run,row) for row in plan['stages']]):
            row=future.result();print('STAGE',row['stage'],row['status'],flush=True);(d/'RECEIPT.json').write_text(json.dumps(plan,indent=2)+'\n')
    assert all(x['status']=='PASS' for x in plan['stages']);plan['status']='UNIVERSAL_REPAIRED53_CHAIN_PASS';(d/'RECEIPT.json').write_text(json.dumps(plan,indent=2)+'\n');print(plan['status'],flush=True)
else:raise ValueError(sys.argv[1])
