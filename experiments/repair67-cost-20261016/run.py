from pathlib import Path
import hashlib,json,os,re,resource,statistics,subprocess,time
root=Path(__file__).resolve().parent
plan=json.loads((root/'DECLARATION.json').read_text())
pins=json.loads((root/'LAUNCH_BINDINGS.json').read_text())
assert pins['terminal_disabled_qualification_pass'] and pins['independent_root_review_pass']
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def check():
    assert sha(pins['executable'])==pins['executable_sha256']
    for item in pins['artifacts']:assert sha(item['path'])==item['sha256'],item['path']
check()
mem=int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:')))
assert mem>=148*1024*1024
assert sha(pins['executable'])==pins['executable_sha256']
expected_nonces=181165677.0769668
all_results=[];reference=None;started=time.monotonic();deadline=started+1800
def memory_limit():resource.setrlimit(resource.RLIMIT_AS,(12*1024**3,12*1024**3))
for trial,mode in enumerate(plan['trial_order']):
    check()
    available_kib=int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:')))
    assert available_kib>=148*1024*1024
    env=os.environ.copy()
    for key in ['SCALAR_FAST_LIB','FAST_ZERO_DISPATCH','FORCE_FULL_FALLBACK','PACKED_ZERO_SHADOW','EARLY_FULLSTATE_SHADOW','FIXED_TRANSFER_SHADOW','FUSED_GUARD','FUSED_GUARD_SHADOW','RAIL_SHADOW']:
        env.pop(key,None)
    env.update(RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',CANDIDATE_SEED_SHADOW='1',SCALAR_FAST_LIB='/home/hclau/ecdsa_research/scalar-fast-20261015/libscalar_fast_batch.so')
    if mode=='fused':env['FUSED_GUARD']='1'
    workers=[];trial_start=time.monotonic()
    try:
        for worker,(first,end) in enumerate(plan['nonce_ranges_each_trial']):
            stem=f'trial{trial}-{mode}-worker{worker}'
            out=(root/(stem+'.log')).open('w');err=(root/(stem+'.err')).open('w')
            argv=[pins['executable'],pins['candidate'],str(first),str(end-first),'2',str(root/(stem+'.jsonl')),pins['model_source'],'4096']
            proc=subprocess.Popen(argv,env=env,stdout=out,stderr=err,stdin=subprocess.DEVNULL,preexec_fn=memory_limit)
            out.close();err.close();workers.append((stem,first,end,proc))
        (root/f'trial{trial}-owned-pids.json').write_text(json.dumps([p.pid for *_,p in workers])+'\n')
        for stem,first,end,proc in workers:
            code=proc.wait(timeout=max(.1,deadline-time.monotonic()));(root/(stem+'.exit')).write_text(str(code)+'\n');assert code==0,(stem,code)
    except BaseException:
        for *_,proc in workers:
            if proc.poll() is None:proc.terminate()
        for *_,proc in workers:
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
        raise
    elapsed=time.monotonic()-trial_start;rows=[];program_walls=[]
    for stem,first,end,proc in workers:
        part=sorted(map(json.loads,(root/(stem+'.jsonl')).read_text().splitlines()),key=lambda r:r['nonce'])
        assert len(part)==4096 and [r['nonce'] for r in part]==list(range(first,end))
        assert all(r['authoritative_rejection'] is False and r['proof_accepted'] is False for r in part)
        assert 'CANDIDATE_OWN_FIAT_PROTECTED_4096_BYTE_CONTROLS_PASS' in (root/(stem+'.err')).read_text()
        program_walls.append(float(re.search(r'wall_seconds=([0-9.]+)',(root/(stem+'.log')).read_text())[1]))
        rows.extend(part)
    rows.sort(key=lambda r:r['nonce']);assert [r['nonce'] for r in rows]==list(range(1,16385))
    if reference is None:reference=rows
    else:assert rows==reference
    item=dict(trial=trial,mode=mode,rows=16384,elapsed_seconds_including_startup=elapsed,aggregate_nonces_per_second=16384/elapsed,forecast_mean_hours=expected_nonces/(16384/elapsed)/3600,program_wall_seconds=program_walls)
    all_results.append(item);(root/'PROGRESS.json').write_text(json.dumps(all_results,indent=2)+'\n');print(json.dumps(item),flush=True)
check()
medians={mode:statistics.median(r['elapsed_seconds_including_startup'] for r in all_results if r['mode']==mode) for mode in ['raw','fused']}
forecasts={mode:expected_nonces/(16384/elapsed)/3600 for mode,elapsed in medians.items()}
result=dict(status='DISABLED_FOUR_PROCESS_TIMING_AND_COMPLETE_ROWS_PASS',trials=all_results,median_elapsed_seconds=medians,forecast_mean_hours=forecasts,cost_gate_pass=forecasts['fused']<=24,unique_timing_nonces=16384,total_rows_with_repetitions=65536,no_nonce_selected=True,no_new_census=True,no_production_changes=True,additional_search_authority=False)
(root/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
