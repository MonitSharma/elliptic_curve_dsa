"""Read-only, complete terminal JSONL audit. Never audit an active log as final."""
from pathlib import Path
import collections, hashlib, json, sys

# Bound before the search launched: plain95-final-20261017/BINDING.json, written by chain.sh after acceptance.
_B=json.loads((Path(__file__).resolve().parent/'BINDING.json').read_text())
ACCEPTANCE=_B['acceptance_sha256']
BINARY=_B['executable_sha256']

def require(condition,message):
    if not condition:raise ValueError(message)

def integer(value,lo,hi,name):
    require(type(value) is int and lo<=value<=hi,name)
    return value

def audit_lane(path,lane,rows,look=4096,workers=4):
    require(rows>=0 and rows%look==0,'incomplete window count')
    seen=bytearray((rows+7)//8);digest=hashlib.sha256();kinds=collections.Counter();passes=[];count=0
    before=path.stat()
    with path.open('rb') as stream:
        for raw in stream:
            require(raw.endswith(b'\n'),'truncated final JSONL row');digest.update(raw)
            r=json.loads(raw);nonce=integer(r.get('nonce'),1,2**63-1,'nonce')
            group,offset=divmod(nonce-1,look)
            require(group%workers==lane,'nonce in wrong lane')
            local=(group//workers)*look+offset
            require(local<rows,'row outside completed lane prefix')
            byte,bit=divmod(local,8)
            require(not seen[byte]&(1<<bit),'duplicate nonce')
            seen[byte]|=1<<bit;count+=1
            require(r.get('proof_accepted') is True,'unaccepted proof gate')
            integer(r.get('witnesses_tried'),0,9024,'witness count')
            if r.get('certified_wrong_value') is True:
                require(r.get('authoritative_rejection') is True,'wrong-bit row not authoritative')
                integer(r.get('witness_batch'),0,140,'witness batch')
                integer(r.get('witness_shot'),0,63,'witness shot')
                require(r['witnesses_tried']>0,'missing witness attempt')
                require('candidate_full_fallback_pass' not in r,'conflicting row dispositions')
                kinds['certified_wrong_value']+=1
            else:
                require(r.get('certified_wrong_value') is False,'missing exact disposition')
                passed=r.get('candidate_full_fallback_pass')
                require(type(passed) is bool,'missing full-fallback boolean')
                shots=integer(r.get('exact_early_shots'),1,9024,'early shots')
                # The final batch can be partial if a raw Fiat scalar pair is
                # excluded by the protected input rule. Exact rejects remain
                # sound; protected passes still require all9024shots below.
                kind=r.get('exact_early_kind')
                if passed:
                    require(r.get('authoritative_rejection') is False,'pass marked rejection')
                    require(kind=='pass' and shots==9024 and r.get('protected_shots')==9024,'incomplete protected pass')
                    passes.append(nonce);kinds['full_protected_pass']+=1
                else:
                    require(r.get('authoritative_rejection') is True,'fallback reject not authoritative')
                    if kind=='pass':
                        require(shots==9024 and r.get('protected_shots')==9024,'missing full protected reject')
                        kinds['early_pass_protected_reject']+=1
                    else:
                        require(kind in ['classical','phase','ancilla'] and r.get('protected_shots')==0,'invalid early rejection')
                        kinds['exact_early_'+kind]+=1
    after=path.stat()
    require((before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'log changed during audit')
    require(count==rows,'missing nonce rows')
    # Every row is in-range and unique; equal cardinality proves exact coverage.
    return {'lane':lane,'rows':count,'sha256':digest.hexdigest(),'bytes':after.st_size,'dispositions':dict(kinds),'passes':sorted(passes),'complete_local_prefix':True}

def hash_file(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def audit(root):
    require((root/'search.exit').read_text().strip()=='0','coordinator not cleanly terminal')
    require(hash_file(root/'ACCEPTANCE.json')==ACCEPTANCE,'changed acceptance')
    receipt=json.loads((root/'ACCEPTANCE.json').read_text());run=json.loads((root/'run-record.json').read_text())
    require(run['acceptance_sha256']==ACCEPTANCE and run['executable_sha256']==BINARY,'changed launch binding')
    require(run['workers']==4 and run['lookahead']==4096 and run['count_cap_each']==134217728,'changed partition')
    require(run['threads_each']==14 and run['search_from']==1 and run['submission_mode']=='queue','changed launch policy')
    require(hash_file(root/'tool/target/release/value_prefilter')==BINARY,'changed executable')
    artifacts={path:hash_file(Path(path)) for path in receipt['runtime_artifacts']}
    require(artifacts==receipt['runtime_artifacts'],'changed runtime artifacts')
    extra={
      '/home/hclau/ecdsa_research/zero-mr-slice-20261016/tip.compact16.bin':'812f706d2edd7e821ff6c5f72db5e7e65b3f9756f562d99c1d0e1fceb007daf0',
      '/home/hclau/ecdsa_research/zero-mr-slice-20261016/libzero8_slice.so':'84b73bcdee01bb537d0320f9985a682758d1076860455ad382a2ae175690ea82',
      '/home/hclau/ecdsa_research/rail-masks-20261016/librail8_masks.so':'046dd5f1d11386550ec5234b955f6bc1974431e79a6b80499bda97da0ade3e90',
      '/home/hclau/ecdsa_research/shake8-20261015/libshake8.so':'41296c5587a62a131f89a84b242e15dd9200d5bd43d2c52a9ab86088b4b9fac6'}
    for path,sha in extra.items():require(hash_file(Path(path))==sha,'changed auxiliary runtime artifact')
    artifacts.update(extra)
    terminal=json.loads((root/'RESULT.json').read_text())
    require(terminal['worker_exit_codes']==[0]*4,'worker failed')
    lanes=[]
    for lane in range(4):
        require((root/f'worker{lane}.exit').read_text().strip()=='0','unclean worker exit')
        progress=root/f'worker{lane}-progress.json'
        p=json.loads(progress.read_text()) if progress.exists() else None
        rows=p['cumulative_worker_rows'] if p else 0
        integer(rows,0,134217728,'completed rows')
        if p:
            require(rows>0 and rows%4096==0 and p['lane']==lane and p['count']==4096,'invalid progress')
            first=1+((rows//4096-1)*4+lane)*4096
            require(p['first']==first and p['last']==first+4095 and p['status']=='COMPLETE_WINDOW_ALL_ROWS_RECORDED','progress range mismatch')
        require(p==terminal['progress'][lane],'terminal progress mismatch')
        lanes.append(audit_lane(root/f'worker{lane}.jsonl',lane,rows))
    passes=sorted(nonce for lane in lanes for nonce in lane['passes'])
    saved=[]
    for path in (root/'passes').glob('pass-*.json'):
        row=json.loads(path.read_text());require(row['full_protected9024_pass'] is True,'invalid pass file')
        require(path.name==f"pass-{row['nonce']}.json",'misnamed pass file');saved.append(row['nonce'])
    require(sorted(saved)==passes,'pass file/log mismatch')
    best=min(passes) if passes else None
    require(terminal['best_full_protected_pass']==best,'terminal pass mismatch')
    prefix=min((lane['rows']//4096)*4+lane['lane'] for lane in lanes)*4096
    complete=best is not None and prefix>=best
    require(terminal['lowest_prefix_window_completion']==complete,'terminal coverage mismatch')
    total=sum(lane['rows'] for lane in lanes)
    require(terminal['screened_unique_completed_rows']==total,'terminal count mismatch')
    require(not passes or complete,'lower nonce prefix incomplete')
    result={'status':'LOWEST_PASS_COMPLETE_JSONL_AUDIT_PASS' if complete else 'NO_PASS_COMPLETE_JSONL_AUDIT_PASS','lowest_full_protected_pass':best,'complete_global_prefix':prefix,'operational_unique_nonces':total,'operational_overrun_above_lowest':total-best if best is not None else None,'lanes':lanes,'runtime_artifacts_rehashed':artifacts,'audit_source_sha256':hash_file(Path(__file__)),'final_benchmark_and_predeclared_census_still_required':True,'preliminary_control':run['preliminary_control'],'preliminary_repeated_attempt_accounting':'Lane-0 control screened nonces 1..4096 once before launch (CONTROL.json); disclose separately, never add to the operational unique count','submission_mode':'queue','score':None}
    return result

if __name__=='__main__':
    root=Path(sys.argv[1]).resolve()
    result=audit(root)
    # Caller chooses a new receipt path; the search source/logs are read-only.
    if len(sys.argv)>2:
        out=Path(sys.argv[2]);require(not out.exists(),'refuse overwrite of audit receipt');out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
