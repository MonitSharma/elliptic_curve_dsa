from pathlib import Path
import datetime,hashlib,json,os,subprocess,time
PROPOSAL_DISABLED=True
assert not PROPOSAL_DISABLED,'source proposal only: no launch authority; separate reviewed revision required'
root=Path(__file__).resolve().parent;workers=4;lookahead=4096;count=134217728
acceptance=root/'ACCEPTANCE.json';receipt=json.loads(acceptance.read_text())
assert receipt['status']=='REPAIRED67_CONDITIONAL_FULL_SOURCE_PROOF_RUNTIME_COST_ACCEPTED_FOR_ASCENDING_SEARCH'
assert receipt['cost_gate_pass'] and receipt['failure_gate_pass']
assert (root/'build.exit').read_text().strip()=='0'
assert receipt['disabled_qualification_pass'] and receipt['independent_operational_review_pass']
assert receipt['fresh_public_record_comparison_pass'] and receipt['measured_expected_hours_8threads']<=24
assert receipt['workers']==4 and receipt['threads_each']==2 and receipt['aggregate_threads_max']==8
assert receipt['aggregate_memory_GiB_max']==48 and receipt['wall_cap_hours']==24
assert receipt['candidate_stream_sha256']=='0beec42b117e5f623736c4171e156d8ffdfaeeb585285636f91bab2838e7c10b'
assert receipt['conditional_theorem_sha256']=='b351ae4cbf4fab52a8248a83d517502c331a0a4291f73f0123370cad645a2c03'
assert receipt['guard_sha256']=='355f9951eda21a7204a96fd391b3208e8d6e000dce6a14feb40d8f19b637f2b3'
assert 1+count*workers<=2**48
threads=int(os.environ.get('SEARCH_THREADS_EACH','2'));assert threads==2 and workers*threads<=8
assert not (root/'run-record.json').exists(),'never silently restart/overwrite an existing search'
passdir=root/'passes';passdir.mkdir();stop=root/'stop-after-nonce.txt';assert not stop.exists()
binary=root/'tool/target/release/value_prefilter';ops=root.parent/'product-exact-20261015/repair-to67-rank-20261016/repair-67-retained-1024-proxy.bin'
assert hashlib.sha256(ops.read_bytes()).hexdigest()==receipt['candidate_stream_sha256']
assert hashlib.sha256(binary.read_bytes()).hexdigest()==receipt['operational_executable_sha256']
required_manifest=root/'REQUIRED_RUNTIME_ARTIFACTS.json'
assert hashlib.sha256(required_manifest.read_bytes()).hexdigest()==receipt['required_runtime_artifacts_manifest_sha256']
required=json.loads(required_manifest.read_text())['artifacts']
accepted_artifacts={item['path']:item['sha256'] for item in receipt['runtime_artifacts']}
assert len(accepted_artifacts)==len(receipt['runtime_artifacts']),'duplicate runtime artifact path'
for item in required:assert accepted_artifacts.get(item['path'])==item['sha256'],item['path']
for item in receipt['runtime_artifacts']:
 assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
record={'status':'STARTED_ASCENDING_SOURCE_FROZEN_SEARCH','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'workers':workers,'threads_each':threads,'lookahead':lookahead,'count_cap_each':count,'wall_limit_hours':24,'candidate_sha256':receipt['candidate_stream_sha256'],'acceptance_sha256':hashlib.sha256(acceptance.read_bytes()).hexdigest(),'executable_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'submission_mode':'queue','search_from':1,'preliminary_distinct_timing_nonces':receipt['preliminary_distinct_timing_nonces'],'preliminary_controls_are_repeated_from1':True}
(root/'run-record.json').write_text(json.dumps(record,indent=2)+'\n')
import resource
def worker_limits():resource.setrlimit(resource.RLIMIT_AS,(12*1024**3,12*1024**3))
jobs=[];started=time.monotonic()
for lane in range(workers):
 env=os.environ.copy()
 for key in ['FAST_ZERO_DISPATCH','PACKED_ZERO_SHADOW','EARLY_FULLSTATE_SHADOW','FIXED_TRANSFER_SHADOW','FORCE_FULL_FALLBACK','CANDIDATE_SEED_SHADOW','SCALAR_FAST_LIB']:env.pop(key,None)
 env.update(SEARCH_LANE=str(lane),SEARCH_LANES=str(workers),SEARCH_STOP_FILE=str(stop),SEARCH_PROGRESS_FILE=str(root/f'worker{lane}-progress.json'),SEARCH_PASS_DIR=str(passdir),ACCEPTANCE_PATH=str(acceptance),ACCEPTANCE_SHA256=record['acceptance_sha256'])
 out=(root/f'worker{lane}.log').open('w');err=(root/f'worker{lane}.err').open('w')
 job=subprocess.Popen([str(binary),str(ops),'1',str(count),str(threads),str(root/f'worker{lane}.jsonl'),str(root.parent/'prefilter-20261015/model-source'),str(lookahead)],env=env,stdout=out,stderr=err,preexec_fn=worker_limits);jobs.append((lane,job,out,err));(root/f'worker{lane}.pid').write_text(str(job.pid)+'\n')
best=None;deadline_stop=False;hard_deadline_stop=False
while any(job.poll() is None for _,job,_,_ in jobs):
 passes=[]
 for p in passdir.glob('pass-*.json'):
  row=json.loads(p.read_text());assert row['full_protected9024_pass'];passes.append(row['nonce'])
 if passes:
  current=min(passes)
  if (best is None or current<best) and not deadline_stop:
   best=current;tmp=stop.with_suffix('.tmp');tmp.write_text(str(best)+'\n');os.replace(tmp,stop)
 if time.monotonic()-started>=24*3600-300 and not deadline_stop:
  deadline_stop=True;tmp=stop.with_suffix('.tmp');tmp.write_text('0\n');os.replace(tmp,stop)
 if time.monotonic()-started>=24*3600:
  hard_deadline_stop=True
  for _,job,_,_ in jobs:
   if job.poll() is None:job.kill() # Only child Popen objects launched by this coordinator.
 for lane,job,_,_ in jobs:
  if job.poll() not in [None,0]:
   # A worker failure prevents lowest-pass certification. Stop cleanly at the
   # next completed window; retain every log and never infer missing rejects.
   tmp=stop.with_suffix('.tmp');tmp.write_text('0\n');os.replace(tmp,stop)
 time.sleep(1)
codes=[]
for lane,job,out,err in jobs:
 code=job.wait();codes.append(code);out.close();err.close();(root/f'worker{lane}.exit').write_text(str(code)+'\n')
terminal_passes=[json.loads(p.read_text())['nonce'] for p in passdir.glob('pass-*.json')]
if terminal_passes:best=min(terminal_passes)
progress=[json.loads((root/f'worker{lane}-progress.json').read_text()) if (root/f'worker{lane}-progress.json').exists() else None for lane in range(workers)]
prefix_complete=False
if best is not None and codes==[0]*workers:
 group=(best-1)//lookahead;cycle,target_lane=divmod(group,workers)
 required=[(cycle+(lane<=target_lane))*lookahead for lane in range(workers)]
 prefix_complete=all((row['cumulative_worker_rows'] if row is not None else 0)>=n for row,n in zip(progress,required))
 # A pass racing the wall deadline can remain unqualified if a lower worker
 # already stopped. Retain it as evidence without certifying/selecting it.
summary={'status':'PASS_AWAITS_COMPLETE_LOG_AUDIT_AND_UNCHANGED_BENCHMARK' if prefix_complete else 'STOPPED_NO_CERTIFIED_PASS','best_full_protected_pass':best,'lowest_prefix_window_completion':prefix_complete,'requires_complete_jsonl_row_audit':True,'worker_exit_codes':codes,'progress':progress,'screened_unique_completed_rows':sum(r['cumulative_worker_rows'] for r in progress if r is not None),'wall_seconds':time.monotonic()-started,'deadline_stop':deadline_stop,'hard_deadline_stop':hard_deadline_stop,'score':None,'submission_mode':'queue'}
(root/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
