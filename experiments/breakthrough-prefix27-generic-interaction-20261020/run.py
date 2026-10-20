import hashlib,json,os,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t,env=None):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 run(['python3','prepare.py'],'prepare',r);f=json.loads((r/'SOURCE-FREEZE.json').read_text());counts=[]
 for i,filter in enumerate(['prime_clean_pool_tests','wide_loan_policy_tests','phase_fit','phase_fusion','direct_transport_tests']):
  name='tests-'+str(i);run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit',filter,'--','--nocapture','--test-threads=1'],name,env=dict(os.environ,PEBBLE_HARD_CAP='1234'));a=re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/(name+'.log')).read_text());assert len(a)==1;counts.append(int(a[0]))
 assert counts==[2,1,1,4,1];run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build');rows=[]
 for case in f['raw_cases']:
  assert sha(Path(case['path']))==case['sha256']and all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());dest=r/case['label'];dest.mkdir();start=time.time();name='generate-'+case['label'];run(['timeout','1800',str(t/'target/release/build_circuit')],name,dest,dict(os.environ,BREAK_RAW_INPUT=case['path']));text=(r/(name+'.log')).read_text();stages=re.findall(r'^GENERIC_STAGE[^\n]+',text,re.M);last=stages[-1];row={**case,'operations':int.from_bytes((dest/'ops.bin').open('rb').read(16)[8:],'little'),'qubits':int(re.search(r'nq=(\d+)',last)[1]),'diagnostic_weight':float(re.search(r'depth_weight=([\d.]+)',last)[1]),'stream_sha256':sha(dest/'ops.bin'),'seconds':time.time()-start,'stages':stages};rows.append(row);(r/'PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({k:v for k,v in row.items()if k not in['stages','raw_row']}),flush=True)
 assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());(r/'RESULT.json').write_text(json.dumps({'status':'FULL_GENERIC_INTERACTION_DIAGNOSTIC_NOT_SCORED','native_controls':sum(counts),'cases':rows,'compact_minus_control_diagnostic_weight':rows[1]['diagnostic_weight']-rows[0]['diagnostic_weight'],'scope':f['scope']},indent=2)+'\n');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
