from pathlib import Path
import hashlib,json,os,re,resource,signal,subprocess,tarfile,time
R=Path(__file__).resolve().parent;B=R.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
d=json.loads((R/'DECLARATION.json').read_text());pins=json.loads((R/'RUNTIME-BINDINGS.json').read_text())
assert d['trial_modes']==['generic','direct'] and pins['executable_sha256']=='12fb482e919ba69459d54904ff4370807b61512a280af0a10599c0a242293065'
assert sha(R/'QUALIFICATION-REVIEW.json')==d['qualification_review_sha256']
archive=B/'product67-filter-20261016/evidence.tar.gz';assert sha(archive)==d['qualification_archive_sha256']
with tarfile.open(archive)as tar:
 data=tar.extractfile(d['reference_prefix_path']).read();assert hashlib.sha256(data).hexdigest()==d['reference_prefix_sha256'];prefix=sorted(map(json.loads,data.decode().splitlines()),key=lambda row:row['nonce'])
assert len(prefix)==4096
def check():
 assert sha(pins['executable'])==pins['executable_sha256']
 for path,h in pins['artifacts'].items():assert sha(path)==h,path
def limit():resource.setrlimit(resource.RLIMIT_AS,(12*1024**3,12*1024**3))
def stop(signum,frame):raise TimeoutError(f'Owned pilot supervisor signal{signum}')
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
deadline=time.monotonic()+900;owned=[];reports=[]
scalar=Path('/home/hclau/ecdsa_research/scalar-fast-20261015/libscalar_fast_batch.so').resolve(strict=True)
assert sha(scalar)=='3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f'
def run_group(name,mode,first,count,look,workers,shadow=False,full=False):
 global owned
 check();available=int(next(x.split()[1]for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')));assert available>=124*1024**2
 env=os.environ.copy()
 for key in ['SCALAR_FAST_LIB','FAST_ZERO_DISPATCH','PACKED_ZERO_SHADOW','EARLY_FULLSTATE_SHADOW','FORCE_FULL_FALLBACK','FIXED_TRANSFER_SHADOW','FUSED_GUARD','FUSED_GUARD_SHADOW','RAIL_SHADOW']:
  env.pop(key,None)
 env.update(SCALAR_FAST_LIB=str(scalar),CANDIDATE_SEED_SHADOW='1',RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
 if mode=='direct':env['FAST_ZERO_DISPATCH']='1'
 if shadow:env['PACKED_ZERO_SHADOW']='1'
 if full:env['EARLY_FULLSTATE_SHADOW']='1'
 owned=[];started=time.monotonic();captured={}
 for worker in range(workers):
  stem=f'{name}-worker{worker}'
  with(R/f'{stem}.log').open('w')as out,(R/f'{stem}.err').open('w')as err:
   proc=subprocess.Popen([pins['executable'],pins['candidate'],str(first),str(count),'2',str(R/f'{stem}.jsonl'),pins['model_source'],str(look)],env=env,stdout=out,stderr=err,stdin=subprocess.DEVNULL,preexec_fn=limit)
  owned.append((stem,proc))
 (R/f'{name}-owned-pids.json').write_text(json.dumps([proc.pid for _,proc in owned])+'\n')
 while any(proc.poll()is None for _,proc in owned):
  assert time.monotonic()<deadline,'pilot deadline'
  for stem,proc in owned:
   if stem in captured:continue
   try:paths={line.split()[-1]for line in Path(f'/proc/{proc.pid}/maps').read_text().splitlines()if '/'in line}
   except FileNotFoundError:continue
   if str(scalar)in paths:
    assert sha(scalar)==env_hash
    captured[stem]={'pid':proc.pid,'resolved_scalar_path':str(scalar),'actual_mapped_scalar_sha256':sha(scalar)}
  time.sleep(.25)
 elapsed=time.monotonic()-started;groups=[];times=[]
 for stem,proc in owned:
  code=proc.wait();(R/f'{stem}.exit').write_text(str(code)+'\n');assert code==0,(stem,code);assert stem in captured,stem
  rows=sorted(map(json.loads,(R/f'{stem}.jsonl').read_text().splitlines()),key=lambda row:row['nonce']);assert len(rows)==count and [row['nonce']for row in rows]==list(range(first,first+count))
  assert all(row['proof_accepted']is False and row['authoritative_rejection']is False for row in rows)
  assert all(not row.get('candidate_full_fallback_pass',False)or row['protected_shots']==9024 for row in rows)
  err=(R/f'{stem}.err').read_text();assert 'CANDIDATE_OWN_FIAT_PROTECTED_4096_BYTE_CONTROLS_PASS'in err
  if full:assert 'EARLY_FULLSTATE_AND_PHYSICAL_RNG9024_PASS'in err
  times.append(float(re.search(r'wall_seconds=([0-9.]+)',(R/f'{stem}.log').read_text())[1]));groups.append(rows)
 (R/f'{name}-mapped-libraries.json').write_text(json.dumps(captured,indent=2)+'\n')
 assert all(rows==groups[0]for rows in groups)
 report={'name':name,'mode':mode,'workers':workers,'threads_each':2,'count_each':count,'group_elapsed_seconds_including_startup':elapsed,'individual_program_only_wall_seconds':times,'resolved_mapped_scalar_verified':True}
 reports.append(report);print(json.dumps(report),flush=True);return groups[0],report
env_hash='3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f'
sourcefiles=[R/'run.py',R/'run.sh',R/'DECLARATION.json',R/'RUNTIME-BINDINGS.json',R/'QUALIFICATION-REVIEW.json']
before={p.name:sha(p)for p in sourcefiles};(R/'SOURCE-PINS-BEFORE.json').write_text(json.dumps(before,indent=2)+'\n')
try:
 control1,_=run_group('control-generic','generic',4097,11,9,1,True,True)
 control2,_=run_group('control-direct','direct',4097,11,9,1,True,False);assert control1==control2
 reference=None
 for trial,mode in enumerate(d['trial_modes']):
  rows,report=run_group(f'trial{trial}-{mode}',mode,1,16384,4096,2)
  assert rows[:4096]==prefix and rows[4096:4107]==control1
  if reference is None:reference=rows
  else:assert rows==reference
  rate=32768/report['group_elapsed_seconds_including_startup'];hours=d['expected_nonces_model']/rate/3600
  report.update(rows_with_repetitions=32768,unique_fixed_nonces=16384,all_rows_equal_across_modes_and_workers=True,
   observed_four_core_amortized_nonces_per_second=rate,observed_four_core_mean_model_hours=hours,
   ideal_linear64_mean_model_hours_NOT_MEASURED=hours/16)
  (R/'PROGRESS.json').write_text(json.dumps(reports,indent=2)+'\n');print(json.dumps(report),flush=True)
finally:
 for _,proc in owned:
  if proc.poll()is None:proc.terminate()
 for _,proc in owned:
  try:proc.wait(timeout=10)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
check();after={p.name:sha(p)for p in sourcefiles};assert before==after;(R/'SOURCE-PINS-AFTER.json').write_text(json.dumps(after,indent=2)+'\n')
result={'status':'UNCHANGED_DISABLED_PLAIN67_PERSISTENT_COST_PILOT_AND_PROTOCOL_CONTROLS_PASS','trials':reports,
 'candidate_sha256':'268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d','expected_nonces_model':d['expected_nonces_model'],
 'all65536trial_rows_equal':True,'qualified4096prefix_equal':True,'extra_new_boundary_partial_and_full9024_controls':True,
 'original2a_function_via_fresh67_certificate':True,'A29_or_G_used':False,'executable_or_source_changed':False,'nonce_selected':None,'production_changed':False,'search_authority':False}
(R/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
