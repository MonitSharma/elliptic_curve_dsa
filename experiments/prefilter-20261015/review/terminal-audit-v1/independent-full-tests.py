from pathlib import Path
import ast,collections,hashlib,importlib.util,json,tempfile
r=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('audit',r/'audit-terminal.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
# Synthetic trust anchors isolate terminal bookkeeping/disposition tests.
# No operational log or artifact is read. The unmodified source is snapshotted.
tree=ast.parse((r/'audit-terminal.py').read_text());f=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='audit');assign=next(n for n in ast.walk(f)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='extra'for t in n.targets));extra=ast.literal_eval(assign.value)
original_hash=m.hash_file
m.hash_file=lambda p:extra.get(Path(p).as_posix())or original_hash(p)
checks=[]
def reject(n):return dict(nonce=n,proof_accepted=True,witnesses_tried=1,certified_wrong_value=True,authoritative_rejection=True,witness_batch=0,witness_shot=1)
def passed(n):return dict(nonce=n,proof_accepted=True,witnesses_tried=0,certified_wrong_value=False,candidate_full_fallback_pass=True,authoritative_rejection=False,exact_early_kind='pass',exact_early_shots=9024,protected_shots=9024)
def case(name,counts,passes=(),mutate=None,valid=True):
 with tempfile.TemporaryDirectory(prefix='synthetic-',dir=r)as td:
  root=Path(td);(root/'passes').mkdir();(root/'tool/target/release').mkdir(parents=True);binary=root/'tool/target/release/value_prefilter';binary.write_bytes(b'synthetic nonproduction executable');m.BINARY=original_hash(binary)
  acc=root/'ACCEPTANCE.json';acc.write_text(json.dumps(dict(runtime_artifacts={})));m.ACCEPTANCE=original_hash(acc)
  run=dict(acceptance_sha256=m.ACCEPTANCE,executable_sha256=m.BINARY,workers=4,lookahead=4096,count_cap_each=134217728,threads_each=12,search_from=1,submission_mode='queue',preliminary_distinct_timing_nonces=0);(root/'run-record.json').write_text(json.dumps(run));(root/'search.exit').write_text('0\n');progress=[];covered=set()
  for lane,count in enumerate(counts):
   rows=[]
   for i in range(count):
    nonce=1+((i//4096)*4+lane)*4096+i%4096;covered.add(nonce);rows.append(passed(nonce)if nonce in passes else reject(nonce))
   (root/f'worker{lane}.jsonl').write_text(''.join(json.dumps(row)+'\n'for row in rows));(root/f'worker{lane}.exit').write_text('0\n')
   p=None
   if count:
    first=1+(((count//4096)-1)*4+lane)*4096;p=dict(cumulative_worker_rows=count,lane=lane,count=4096,first=first,last=first+4095,status='COMPLETE_WINDOW_ALL_ROWS_RECORDED');(root/f'worker{lane}-progress.json').write_text(json.dumps(p))
   progress.append(p)
  assert set(passes)<=covered
  for nonce in passes:(root/f'passes/pass-{nonce}.json').write_text(json.dumps(dict(nonce=nonce,full_protected9024_pass=True)))
  prefix=0
  while prefix+1 in covered:prefix+=1
  best=min(passes)if passes else None;complete=best is not None and best<=prefix
  result=dict(worker_exit_codes=[0]*4,progress=progress,best_full_protected_pass=best,lowest_prefix_window_completion=complete,screened_unique_completed_rows=len(covered));(root/'RESULT.json').write_text(json.dumps(result))
  if mutate:mutate(root)
  try:out=m.audit(root)
  except (ValueError,KeyError):assert not valid,name
  else:
   assert valid,name;assert out['complete_global_prefix']==prefix and out['lowest_full_protected_pass']==best and out['operational_unique_nonces']==len(covered);assert out['score']is None
  checks.append(dict(case=name,expected_accept=valid))
def alter_result(root,field,value):
 p=root/'RESULT.json';x=json.loads(p.read_text());x[field]=value;p.write_text(json.dumps(x))
case('four complete lanes minimum3 vs5000',[4096]*4,[3,5000])
case('lane0 next window extends exact prefix',[8192,4096,4096,4096])
case('lane1 next window leaves earlier hole',[4096,8192,4096,4096])
case('zero progress lane no pass is safe',[0,4096,4096,4096])
case('pass with incomplete lower prefix rejected',[0,4096,4096,4096],[5000],valid=False)
case('missing saved pass rejected',[4096]*4,[3],lambda p:(p/'passes/pass-3.json').unlink(),False)
case('worker nonzero rejected',[4096]*4,[],lambda p:alter_result(p,'worker_exit_codes',[0,1,0,0]),False)
case('reported higher pass rejected',[4096]*4,[3,5000],lambda p:alter_result(p,'best_full_protected_pass',5000),False)
case('reported extra completed row rejected',[4096]*4,[],lambda p:alter_result(p,'screened_unique_completed_rows',16385),False)
def bad_progress(root):
 p=root/'worker0-progress.json';x=json.loads(p.read_text());x['first']=2;p.write_text(json.dumps(x))
case('progress range corruption rejected',[4096]*4,[],bad_progress,False)
def duplicate(root):
 p=root/'worker0.jsonl'
 with p.open('a')as f:f.write(json.dumps(reject(1))+'\n')
case('complete log duplicate rejected',[4096]*4,[],duplicate,False)
report=dict(status='FULL_SYNTHETIC_TERMINAL_AUDIT_CONTROLS_PASS',checks=checks,source_sha256=hashlib.sha256((r/'audit-terminal.py').read_bytes()).hexdigest(),production_logs_read=False,synthetic_hash_trust_anchors=True,actual_runtime_artifact_rehash_not_exercised_here=True)
(r/'full-synthetic-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],checks=len(checks))))
