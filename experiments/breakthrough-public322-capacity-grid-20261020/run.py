import hashlib,json,os,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t,env=None):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
def records(path):
 h=hashlib.sha3_256();size=0
 with path.open('rb',buffering=0)as source:
  header=source.read(16);assert header[:8]==b'QECCOPSZ';n=int.from_bytes(header[8:],'little');p=subprocess.Popen(['zstd','-dc'],stdin=source,stdout=subprocess.PIPE)
  while chunk:=p.stdout.read(1<<20):h.update(chunk);size+=len(chunk)
  assert p.wait()==0 and size==n*56
 return n,h.hexdigest()
try:
 run(['python3','prepare.py'],'prepare',r);f=json.loads((r/'SOURCE-FREEZE.json').read_text());counts=[]
 for i,filter in enumerate(['prime_clean_pool_tests','wide_loan_policy_tests','phase_fit','phase_fusion','direct_transport_tests']):
  name='tests-'+str(i);run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit',filter,'--','--nocapture','--test-threads=1'],name,env=dict(os.environ,PEBBLE_HARD_CAP='1234'));a=re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/(name+'.log')).read_text());assert len(a)==1;counts.append(int(a[0]))
 assert counts==[2,1,1,4,1];run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build');rows=[]
 for hard,square in f['cases']:
  assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());dest=r/f'hard{hard}-square{square}';dest.mkdir();start=time.time();env=dict(os.environ,BREAK_HARD_CAP=str(hard),BREAK_SQUARE_CAP=str(square))
  with(dest/'generate.log').open('xb')as log:
   p=subprocess.Popen(['timeout','1800',str(t/'target/release/build_circuit')],cwd=dest,env=env,stdout=log,stderr=subprocess.STDOUT);(dest/'child.pid').write_text(str(p.pid)+'\n');rc=p.wait()
  (dest/'generate.exit').write_text(str(rc)+'\n');text=(dest/'generate.log').read_text();assert f'BOUND_CAPACITY hard={hard} square={square}'in text;row={'hard':hard,'square':square,'exit':rc,'seconds':time.time()-start}
  if rc==0:
   row['raw_sha256']=sha(dest/'ops.bin');row['operations'],row['records_sha3_256']=records(dest/'ops.bin');last=re.findall(r'CAPACITY_RAW nq=(\d+) nb=(\d+) native=(\d+) depth_weight=([\d.]+)',text);assert len(last)==1;row.update(zip(['qubits','bits','native','diagnostic_weight'],[int(last[0][0]),int(last[0][1]),int(last[0][2]),float(last[0][3])]))
   if hard==1536 and square==1408:assert row['operations']==10543037 and row['records_sha3_256']==f['control_raw_records_sha3']
  else:row['failure_tail']=text[-3000:]
  rows.append(row);(r/'PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
 (r/'RESULT.json').write_text(json.dumps({'status':'RAW_CAPACITY_GRID_NOT_SCORED','native_controls':sum(counts),'cases':rows,'scope':f['scope']},indent=2)+'\n');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
