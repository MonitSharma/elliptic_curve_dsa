import hashlib,json,os,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t,env=None):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 run(['python3','prepare.py'],'prepare',r);f=json.loads((r/'SOURCE-FREEZE.json').read_text());counts=[]
 for i,filter in enumerate(['classical_factors_xor::tests','classical_wide::tests','classical_wide::wide_table_tests']):
  name='tests-'+str(i);run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit',filter,'--','--nocapture','--test-threads=1'],name);a=re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/(name+'.log')).read_text());assert len(a)==1 and int(a[0])>0;counts.append(int(a[0]))
 run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build');start=time.time();run([str(t/'target/release/build_circuit')],'generate',env=dict(os.environ,BREAK_PRODUCT_INPUT=f['public_input']));assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());stages=re.findall(r'^GENERIC_STAGE[^\n]+',(r/'generate.log').read_text(),re.M);first=stages[0];last=stages[-1];weight=lambda line:float(re.search(r'depth_weight=([\d.]+)',line)[1]);result={'status':'PUBLIC54FC_REPEAT_GENERIC_RESEARCH_NOT_SCORED','native_test_counts':counts,'input_diagnostic_weight':weight(first),'output_diagnostic_weight':weight(last),'diagnostic_saving':weight(first)-weight(last),'qubits':int(re.search(r'nq=(\d+)',last)[1]),'operations':int.from_bytes((t/'ops.bin').open('rb').read(16)[8:],'little'),'output_stream_sha256':sha(t/'ops.bin'),'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'stages':stages,'seconds':time.time()-start,'scope':f['scope']};(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(r/'run.exit').write_text('0\n');print(json.dumps(result),flush=True)
except BaseException:
 (r/'run.exit').write_text('1\n');raise
