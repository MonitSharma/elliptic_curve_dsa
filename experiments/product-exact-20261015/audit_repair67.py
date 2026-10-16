"""Prepare/run only the fourteen new A29-relative stages after native/fresh gates.

The completed53 certificate is a theorem premise. No theorem or value mask from
the arithmetic-different original4b source transfers across A29.
"""
import concurrent.futures,copy,filecmp,hashlib,json,os,re,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'repair67-universal-20261016'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
exe=r/'target-cache-certificate-v2/release/product_paired_diagnostic'
assert sha(exe)=='2e9f5ee6ed4ea1fa5b625f38298a71e05ce885778db7aed1064b23d2ee657091'
basepath=r/'repair53-universal-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json'
def source_hashes():
    s=r/'cache-certificate-v2-tool'
    return {str(p.relative_to(s)):sha(p) for p in s.rglob('*') if p.is_file() and 'target' not in p.relative_to(s).parts}
def write(p,obj):p.write_text(json.dumps(obj,indent=2)+'\n')
mode=sys.argv[1]
if mode=='prepare':
    assert not (d/'PLAN.json').exists();base=json.loads(basepath.read_text())
    assert base['status']=='UNIVERSAL_A29_RELATIVE_CACHE_EQUIVALENCE_PASS' and base['stage_count']==53
    assert source_hashes()==base['source_files_sha256'] and sha(exe)==base['verifier_executable_sha256']
    freeze=json.loads((r/'REPAIR67_FREEZE.json').read_text());old=json.loads((r/'REPAIR53_FREEZE.json').read_text())
    gate=json.loads((r/'repair67-native-20261016/census-summary.json').read_text())
    native=json.loads((r/'repair67-native-20261016/NATIVE_RECEIPT.json').read_text())
    assert gate['failure_gate_pass'] and gate['all_declared_rows_retained'] and gate['batches_each']==32768
    assert gate['candidate_sha256']==freeze['external_stream_sha256']==native['native_stream_sha256']
    assert native['status']=='NATIVE_REPAIRED67_SOURCE_AND_BYTE_IDENTITY_PASS'
    assert (r/'repair67-native-20261016/launcher.exit').read_text().strip()=='0'
    assert base['baseline_stream_sha256']==freeze['repair_parent_sha256']==old['repair_parent_sha256']
    assert base['candidate_stream_sha256']==old['external_stream_sha256']
    lines=[x.split() for x in (r/freeze['chain_manifest']).read_text().splitlines()]
    oldlines=[x.split() for x in (r/old['chain_manifest']).read_text().splitlines()]
    assert len(lines)==67 and len(oldlines)==53 and lines[:53]==oldlines
    assert len(freeze['stages'])==67 and freeze['stages'][:53]==old['stages']
    previous=old['external_stream'];stages=[]
    for i,((output,log),config) in enumerate(zip(lines[53:],freeze['stages'][53:]),54):
        stages.append(dict(stage=i,family=config['family'],atom_cap=config['atom_cap'],config=config,input_stream=previous,input_sha256=sha(r/previous),output_stream=output,output_sha256=sha(r/output),lease_log=log,lease_log_sha256=sha(r/log) if log!='=' else None,status='not launched'));previous=output
    assert stages[0]['input_sha256']==base['candidate_stream_sha256'] and stages[-1]['output_sha256']==freeze['external_stream_sha256']
    d.mkdir(exist_ok=True)
    write(d/'PLAN.json',dict(status='PREPARED_NOT_LAUNCHED',baseline_stream_sha256=base['baseline_stream_sha256'],intermediate53_stream_sha256=base['candidate_stream_sha256'],candidate_stream_sha256=freeze['external_stream_sha256'],preceding53_certificate_sha256=sha(basepath),source_freeze_sha256=sha(r/'REPAIR67_FREEZE.json'),native_receipt_sha256=sha(r/'repair67-native-20261016/NATIVE_RECEIPT.json'),fresh_gate_sha256=sha(r/'repair67-native-20261016/census-summary.json'),source_files_sha256=source_hashes(),verifier_executable_sha256=sha(exe),workers=2,per_worker_address_limit_GiB=12,no_simulated_inputs=True,stages=stages))
    print('PREPARED_FIXED_FOURTEEN_STAGE_APPEND',flush=True)
elif mode=='run':
    assert not (d/'RECEIPT.json').exists();plan=copy.deepcopy(json.loads((d/'PLAN.json').read_text()))
    assert sha(basepath)==plan['preceding53_certificate_sha256'] and source_hashes()==plan['source_files_sha256']
    available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
    assert available>=200*1024**3;plan.update(status='INCOMPLETE',available_at_launch_bytes=available)
    def audit(row):
        assert sha(r/row['input_stream'])==row['input_sha256'] and sha(r/row['output_stream'])==row['output_sha256'];out=d/f"stage-{row['stage']:02d}.log"
        if row['lease_log']=='=':
            assert filecmp.cmp(r/row['input_stream'],r/row['output_stream'],shallow=False);out.write_text('UNIVERSAL_BYTE_IDENTITY_PASS\n');rc=0
        else:
            assert sha(r/row['lease_log'])==row['lease_log_sha256'];c=row['config'];env=os.environ.copy();env.update(CACHE_ATOM_CAP=str(row['atom_cap']),CACHE_PRODUCT_CAP=str(c.get('product_cap',1000000)),ANF_PAIR_CAP=str(c.get('pair_cap',64)),RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1')
            with out.open('wb') as f:rc=subprocess.run(['prlimit','--as='+str(12*1024**3),'--',str(exe),str(r/row['input_stream']),str(r/row['output_stream']),str(r/row['lease_log']),row['family']],stdout=f,stderr=subprocess.STDOUT,env=env).returncode
        row.update(status='PASS' if rc==0 else 'FAIL',returncode=rc,audit_log=str(out.relative_to(r)),audit_log_sha256=sha(out));return row
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for future in concurrent.futures.as_completed([pool.submit(audit,row) for row in plan['stages']]):
            row=future.result();print('STAGE',row['stage'],row['status'],flush=True);write(d/'RECEIPT.json',plan)
    assert all(x['status']=='PASS' for x in plan['stages']);plan['status']='UNIVERSAL_REPAIRED67_APPEND_PASS';write(d/'RECEIPT.json',plan);print(plan['status'],flush=True)
elif mode=='consolidate':
    assert not (d/'CACHE_EQUIVALENCE_CERTIFICATE.json').exists() and (d/'launcher.exit').read_text().strip()=='0'
    receipt=json.loads((d/'RECEIPT.json').read_text());base=json.loads(basepath.read_text())
    assert receipt['status']=='UNIVERSAL_REPAIRED67_APPEND_PASS' and len(receipt['stages'])==14
    assert sha(basepath)==receipt['preceding53_certificate_sha256'] and source_hashes()==receipt['source_files_sha256']
    assert sha(exe)==receipt['verifier_executable_sha256']
    assert sha(r/'REPAIR67_FREEZE.json')==receipt['source_freeze_sha256']
    assert sha(r/'repair67-native-20261016/NATIVE_RECEIPT.json')==receipt['native_receipt_sha256']
    assert sha(r/'repair67-native-20261016/census-summary.json')==receipt['fresh_gate_sha256']
    last=receipt['intermediate53_stream_sha256'];leases=uses=0
    for number,row in enumerate(receipt['stages'],54):
        assert row['stage']==number and row['status']=='PASS' and row['returncode']==0 and row['input_sha256']==last
        for path,h in [('input_stream','input_sha256'),('output_stream','output_sha256'),('audit_log','audit_log_sha256')]:assert sha(r/row[path])==row[h]
        log=(r/row['audit_log']).read_text()
        if row['lease_log']=='=':assert 'UNIVERSAL_BYTE_IDENTITY_PASS' in log and row['input_sha256']==row['output_sha256']
        else:
            assert sha(r/row['lease_log'])==row['lease_log_sha256'] and 'UNIVERSAL_CACHE_CERTIFICATE_PASS' in log and 'independent_zero_and_product_passes=true' in log
            leases+=int(re.search(r'leases=(\d+)',log).group(1));uses+=int(re.search(r'uses=(\d+)',log).group(1))
        last=row['output_sha256']
    assert last==receipt['candidate_stream_sha256']
    cert={k:v for k,v in base.items() if k not in ['receipt_sha256','native_source_binding','native_receipt_sha256','source_freeze_sha256','candidate_stream_sha256','stage_count','leases_verified','replaced_uses_verified']}
    cert.update(status='UNIVERSAL_A29_RELATIVE_CACHE_EQUIVALENCE_PASS',stage_count=67,candidate_stream_sha256=last,preceding53_certificate_sha256=sha(basepath),append_receipt_sha256=sha(d/'RECEIPT.json'),source_freeze_sha256=receipt['source_freeze_sha256'],native_receipt_sha256=receipt['native_receipt_sha256'],leases_verified=base['leases_verified']+leases,replaced_uses_verified=base['replaced_uses_verified']+uses,append_leases_verified=leases,append_replaced_uses_verified=uses,composition='Completed source-bound universal53 theorem followed by every newly rederived universal stage54..67, with identical intermediate stream SHA. Arithmetic parent is corrected A29, not original4b.')
    write(d/'CACHE_EQUIVALENCE_CERTIFICATE.json',cert)
    freeze=json.loads((r/'REPAIR67_FREEZE.json').read_text())
    companion=dict(status='CONDITIONAL_PER_INPUT_MASK_TRANSFER_THEOREM_NOT_A_MASK_PROOF',certificate_sha256=sha(d/'CACHE_EQUIVALENCE_CERTIFICATE.json'),baseline_A29_stream_sha256=base['baseline_stream_sha256'],candidate_stream_sha256=last,candidate_prefix=freeze['prefix_manifest'],theorem='For each fixed ABI input x and scored output bit b, a separately sound A29-source-bound proof that F_A29,b(x,r) is constant for all original A29 MR r implies the audited67 cache output equals F_A29,b(x,0) for every candidate MR under the audited original-MR projection.',separate_premises=['A29-specific model/mask, never original4b across this arithmetic change.','Evaluate candidate final-source own Fiat inputs.','New nonce retains the identical audited prefix and48 adjacent XX identity pairs.','Full phase/dirty checks and unchanged official benchmark remain required.'],score=None)
    write(d/'PER_INPUT_MASK_TRANSFER.json',companion)
    (d/'PER_INPUT_MASK_TRANSFER.md').write_text('# Corrected A29 per-input mask transfer through67 cache stages\n\nThe certificate composes the completed53-stage A29 theorem with fourteen independently audited stages. For a fixed input and scored bit, a separately sound A29-source-bound independence mask permits the A29 zero-MR evaluator to supply that bit for every candidate MR assignment. This does not transfer the original4b mask or prove global A29 MR independence. Final-source own Fiat inputs, identical audited prefix plus48 XX pairs for a new nonce, and full phase/dirty/official checks remain separate requirements.\n')
    print(json.dumps(dict(certificate_sha256=sha(d/'CACHE_EQUIVALENCE_CERTIFICATE.json'),mask_companion_sha256=sha(d/'PER_INPUT_MASK_TRANSFER.json'),leases=cert['leases_verified'],uses=cert['replaced_uses_verified'])),flush=True)
else:raise ValueError(mode)
