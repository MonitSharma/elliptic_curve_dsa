import hashlib,json,os,re,shutil,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t):
 with(r/(name+'.log')).open('xb')as out:
  p=subprocess.Popen(cmd,cwd=cwd,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 run(['python3','prepare-v2.py'],'prepare-v2',r);f=json.loads((r/'SOURCE_FREEZE-v2.json').read_text());run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build-v2');rows=[]
 for i,case in enumerate(f['cases']):
  assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());dest=r/('v2-case'+str(i));dest.mkdir();env=dict(os.environ,BREAK_CAP='1234',BREAK_HARD=str(case['cap']),BREAK_PREFIX27_MODE=case['mode'],BREAK_PREFIX27_ROOM=str(case['room']));start=time.time()
  with(dest/'generate.log').open('xb')as log:
   p=subprocess.Popen(['timeout','1800',str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=log,stderr=subprocess.STDOUT);(dest/'child.pid').write_text(str(p.pid)+'\n');rc=p.wait()
  (dest/'generate.exit').write_text(str(rc)+'\n');log=(dest/'generate.log').read_text();assert f'BOUND_PREFIX27_SETTINGS mode={case["mode"]} room={case["room"]}'in log;row={**case,'index':i,'exit':rc,'seconds':time.time()-start,'builder_totals':[l for l in log.splitlines()if l.startswith('HEO_TOTAL ')],'prefix27_calls':len(re.findall(r'^PREFIX27_PRODUCTION ',log,re.M)),'contexts':dict(__import__('collections').Counter(re.findall(r'^PREFIX27_CONTEXT [^\n]+',log,re.M)))}
  if rc==0:
   shutil.copyfile(t/'ops.bin',dest/'ops.bin');row['raw_sha256']=sha(dest/'ops.bin')
   if i==0:assert row['raw_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'and row['prefix27_calls']==0
  else:row['failure_tail']=log[-3000:]
  rows.append(row);(r/'ADMISSION-PROGRESS-v2.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
 (r/'ADMISSION-RESULT-v2.json').write_text(json.dumps({'status':'BOUND_PREFIX27_RAW_GRID_NOT_SCORED','cases':rows,'scope':f['binding_correction']},indent=2)+'\n');(r/'run-v2.exit').write_text('0\n')
except BaseException:
 (r/'run-v2.exit').write_text('1\n');raise
