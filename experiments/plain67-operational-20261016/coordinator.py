from pathlib import Path
import datetime,hashlib,json,os,subprocess,time
root=Path(__file__).resolve().parent;workers=4;lookahead=4096;count=134217728
acceptance=root/'ACCEPTANCE.json';receipt=json.loads(acceptance.read_text())
assert receipt['status']=='SOURCE_BOUND_MASK_TRANSFER_AND_RUNTIME_ACCEPTED_FOR_ASCENDING_SEARCH'
assert receipt['cost_gate_pass'] and receipt['failure_gate_pass']
assert (root/'build.exit').read_text().strip()=='0'
assert json.loads((root/'CONTROL.json').read_text())['status']=='CONTROL_ROWS_EQUAL_QUALIFIED_PREFIX'
threads=int(os.environ.get('SEARCH_THREADS_EACH','14'));assert 1<=threads<=14
assert not (root/'run-record.json').exists(),'never silently restart/overwrite an existing search'
passdir=root/'passes';passdir.mkdir();stop=root/'stop-after-nonce.txt';assert not stop.exists()
binary=root/'tool/target/release/value_prefilter';ops=root.parent/'product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin'
assert hashlib.sha256(ops.read_bytes()).hexdigest()==receipt['candidate_stream_sha256']
record={'status':'STARTED_ASCENDING_SOURCE_FROZEN_SEARCH','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'workers':workers,'threads_each':threads,'lookahead':lookahead,'count_cap_each':count,'wall_limit_hours':48,'candidate_sha256':receipt['candidate_stream_sha256'],'acceptance_sha256':hashlib.sha256(acceptance.read_bytes()).hexdigest(),'executable_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'submission_mode':'queue','search_from':1,'preliminary_control':'lane0 nonces 1..4096 (CONTROL.json), repeated from 1 in the search'}
(root/'run-record.json').write_text(json.dumps(record,indent=2)+'\n')
jobs=[];started=time.monotonic()
for lane in range(workers):
 env=os.environ.copy();env.update(SEARCH_LANE=str(lane),SEARCH_LANES=str(workers),SEARCH_STOP_FILE=str(stop),SEARCH_PROGRESS_FILE=str(root/f'worker{lane}-progress.json'),SEARCH_PASS_DIR=str(passdir),ACCEPTANCE_PATH=str(acceptance),ACCEPTANCE_SHA256=record['acceptance_sha256'])
 out=(root/f'worker{lane}.log').open('w');err=(root/f'worker{lane}.err').open('w')
 job=subprocess.Popen([str(binary),str(ops),'1',str(count),str(threads),str(root/f'worker{lane}.jsonl'),str(root.parent/'prefilter-20261015/model-source'),str(lookahead)],env=env,stdout=out,stderr=err);jobs.append((lane,job,out,err));(root/f'worker{lane}.pid').write_text(str(job.pid)+'\n')
best=None;deadline_stop=False
while any(job.poll() is None for _,job,_,_ in jobs):
 passes=[]
 for p in passdir.glob('pass-*.json'):
  row=json.loads(p.read_text());assert row['full_protected9024_pass'];passes.append(row['nonce'])
 if passes:
  current=min(passes)
  if best is None or current<best:
   best=current;tmp=stop.with_suffix('.tmp');tmp.write_text(str(best)+'\n');os.replace(tmp,stop)
 elif time.monotonic()-started>=48*3600 and not deadline_stop:
  deadline_stop=True;tmp=stop.with_suffix('.tmp');tmp.write_text('0\n');os.replace(tmp,stop)
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
summary={'status':'PASS_AWAITS_COMPLETE_LOG_AUDIT_AND_UNCHANGED_BENCHMARK' if prefix_complete else 'STOPPED_NO_CERTIFIED_PASS','best_full_protected_pass':best,'lowest_prefix_window_completion':prefix_complete,'requires_complete_jsonl_row_audit':True,'worker_exit_codes':codes,'progress':progress,'screened_unique_completed_rows':sum(r['cumulative_worker_rows'] for r in progress if r is not None),'wall_seconds':time.monotonic()-started,'deadline_stop':deadline_stop,'score':None,'submission_mode':'queue'}
(root/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
