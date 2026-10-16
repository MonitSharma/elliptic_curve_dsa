from pathlib import Path
import hashlib,json,os,re,resource,signal,statistics,subprocess,tarfile,time
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=json.loads((R/'DECLARATION.json').read_text());pins=json.loads((R/'LAUNCH_BINDINGS.json').read_text())
assert plan['trial_order']==['raw','fused','fused','raw'] and plan['max_total_threads']==8
assert pins['executable_sha256']==plan['executable_sha256']=='ab8cf13ceca99f8418ba490e7e02be7b0611a55de975a3451c5943d55c25e28b'
old=R.parent/'repair67-cost-20261016';assert sha(old/'evidence.tar.gz')==plan['prior_archive_sha256']
with tarfile.open(old/'evidence.tar.gz')as tar:
 reference=[]
 for name,h in plan['prior_reference_files'].items():
  data=tar.extractfile(name).read();assert hashlib.sha256(data).hexdigest()==h
  reference.extend(map(json.loads,data.decode().splitlines()))
reference.sort(key=lambda row:row['nonce']);assert [row['nonce']for row in reference]==list(range(1,16385))
def check():
 assert sha(pins['executable'])==pins['executable_sha256']
 for artifact in pins['artifacts']:assert sha(artifact['path'])==artifact['sha256'],artifact['path']
def memory_limit():resource.setrlimit(resource.RLIMIT_AS,(12*1024**3,12*1024**3))
def memory_check():
 available=int(next(x.split()[1]for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))
 assert available>=148*1024**2, '48GiB reservation plus100GiB reserve required'
 return available
def stop_signal(signum,frame):raise TimeoutError(f'Owned supervisor received signal{signum}')
signal.signal(signal.SIGTERM,stop_signal);signal.signal(signal.SIGINT,stop_signal)
deadline=time.monotonic()+1800;results=[];workers=[]
sourcepins={p.name:sha(p)for p in [R/'run.py',R/'run.sh',R/'DECLARATION.json',R/'LAUNCH_BINDINGS.json']}
(R/'SOURCE-PINS-BEFORE.json').write_text(json.dumps(sourcepins,indent=2)+'\n')
try:
 for trial,mode in enumerate(plan['trial_order']):
  check();available=memory_check();workers=[]
  env=os.environ.copy()
  for key in ['SCALAR_FAST_LIB','FAST_ZERO_DISPATCH','FORCE_FULL_FALLBACK','PACKED_ZERO_SHADOW','EARLY_FULLSTATE_SHADOW','FIXED_TRANSFER_SHADOW','FUSED_GUARD','FUSED_GUARD_SHADOW','RAIL_SHADOW']:
   env.pop(key,None)
  env.update(RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',CANDIDATE_SEED_SHADOW='1',SCALAR_FAST_LIB='/home/hclau/ecdsa_research/scalar-fast-20261015/libscalar_fast_batch.so')
  if mode=='fused':env['FUSED_GUARD']='1'
  started=time.monotonic()
  for worker in range(4):
   name=f'trial{trial}-{mode}-worker{worker}'
   with(R/f'{name}.log').open('w')as out,(R/f'{name}.err').open('w')as err:
    argv=[pins['executable'],pins['candidate'],'1','16384','2',str(R/f'{name}.jsonl'),pins['model_source'],'4096']
    proc=subprocess.Popen(argv,env=env,stdout=out,stderr=err,stdin=subprocess.DEVNULL,preexec_fn=memory_limit)
   workers.append((name,proc))
  (R/f'trial{trial}-owned-pids.json').write_text(json.dumps([p.pid for _,p in workers])+'\n')
  for name,proc in workers:
   code=proc.wait(timeout=max(.1,deadline-time.monotonic()));(R/f'{name}.exit').write_text(str(code)+'\n');assert code==0,(name,code)
  elapsed=time.monotonic()-started;walls=[];outputs=[]
  for name,proc in workers:
   path=R/f'{name}.jsonl';rows=sorted(map(json.loads,path.read_text().splitlines()),key=lambda row:row['nonce'])
   assert rows==reference and len(rows)==16384,name
   assert all(row['proof_accepted']is False and row['authoritative_rejection']is False for row in rows)
   assert 'CANDIDATE_OWN_FIAT_PROTECTED_4096_BYTE_CONTROLS_PASS'in(R/f'{name}.err').read_text()
   if mode=='fused':assert 'FUSED_GUARD_LINEAGE_BOUND'in(R/f'{name}.err').read_text()
   walls.append(float(re.search(r'wall_seconds=([0-9.]+)',(R/f'{name}.log').read_text())[1]))
   outputs.append({'path':path.name,'sha256':sha(path),'rows':len(rows),'all_rows_equal_frozen_reference':True})
  rate=65536/elapsed;hours8=181165677.0769668/rate/3600
  item={'trial':trial,'mode':mode,'available_KiB_before':available,'group_elapsed_seconds_including_startup':elapsed,
   'rows_with_repetitions':65536,'unique_existing_nonces':16384,'observed_eight_thread_amortized_nonces_per_second':rate,
   'observed_eight_thread_amortized_mean_hours':hours8,'ideal_linear_64_thread_mean_hours_NOT_MEASURED':hours8/8,
   'individual_program_only_wall_seconds':walls,'program_only_common_steady_state_claimed':False,'outputs':outputs}
  results.append(item);(R/'PROGRESS.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(item),flush=True)
finally:
 for _,proc in workers:
  if proc.poll()is None:proc.terminate()
 for _,proc in workers:
  try:proc.wait(timeout=10)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
check();after={p.name:sha(p)for p in [R/'run.py',R/'run.sh',R/'DECLARATION.json',R/'LAUNCH_BINDINGS.json']}
assert sourcepins==after;(R/'SOURCE-PINS-AFTER.json').write_text(json.dumps(after,indent=2)+'\n')
medians={mode:statistics.median(x['group_elapsed_seconds_including_startup']for x in results if x['mode']==mode)for mode in ['raw','fused']}
result={'status':'DISABLED_PERSISTENT_FOUR_WINDOW_COST_AND_COMPLETE_ROWS_PASS','trials':results,'median_group_seconds':medians,
 'ideal_linear_64_thread_mean_hours_NOT_MEASURED':{mode:181165677.0769668/(65536/seconds)/3600/8 for mode,seconds in medians.items()},
 'user_criterion':'Approximately24hoursat64threads; previous8thread24hrestrictionwasours. Onlyanideallinearprojectionisavailablehere.',
 'source_and_binary_changed':False,'new_unique_inputs':False,'nonce_selected':None,'production_changed':False,'additional_search_authority':False}
(R/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
