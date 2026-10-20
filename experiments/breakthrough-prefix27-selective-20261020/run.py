import hashlib,json,os,re,shutil,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 run(['python3','prepare.py'],'prepare',r);f=json.loads((r/'SOURCE_FREEZE.json').read_text());filters=['selective_room_tests','prefix27_width57_tests','prefix27_global_policy_tests','prefix27_activation_tests','prefix_schedule_cleanup_tests','prefix_schedule_tests'];counts=[]
 for i,filter in enumerate(filters):
  name='tests-'+str(i);run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit',filter,'--','--nocapture','--test-threads=1'],name);a=re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/(name+'.log')).read_text());assert len(a)==1;counts.append(int(a[0]))
 assert counts==[1,2,2,1,1,2];run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build');rows=[]
 for i,case in enumerate(f['cases']):
  assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());dest=r/('case'+str(i));dest.mkdir();env=dict(os.environ,BREAK_CAP='1234',BREAK_HARD=str(case['cap']),BREAK_PREFIX27_MODE=case['mode'],BREAK_PREFIX27_ROOM=str(case['room']));start=time.time()
  with(dest/'generate.log').open('xb')as log:
   p=subprocess.Popen(['timeout','1800',str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=log,stderr=subprocess.STDOUT);(dest/'child.pid').write_text(str(p.pid)+'\n');rc=p.wait()
  (dest/'generate.exit').write_text(str(rc)+'\n');log=(dest/'generate.log').read_text();assert f'BOUND_PREFIX27_SETTINGS mode={case["mode"]} room={case["room"]}'in log;row={**case,'index':i,'exit':rc,'seconds':time.time()-start,'builder_totals':[l for l in log.splitlines()if l.startswith('HEO_TOTAL ')],'prefix27_calls':len(re.findall(r'^PREFIX27_PRODUCTION ',log,re.M))}
  if rc==0:
   shutil.copyfile(t/'ops.bin',dest/'ops.bin');row['raw_sha256']=sha(dest/'ops.bin')
   if i==0:assert row['raw_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'and row['prefix27_calls']==0
  else:row['failure_tail']=log[-3000:]
  rows.append(row);(r/'ADMISSION-PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
 (r/'ADMISSION-RESULT.json').write_text(json.dumps({'status':'SELECTIVE_PREFIX27_RAW_GRID_NOT_SCORED','native_test_counts':counts,'cases':rows,'scope':f['scope']},indent=2)+'\n');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
