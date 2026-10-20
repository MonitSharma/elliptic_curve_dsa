import hashlib,json,os,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'candidate';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();env=dict(os.environ,PEBBLE_HARD_CAP='1234')
def run(cmd,name,cwd=t):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 run(['python3','prepare.py'],'prepare',r);f=json.loads((r/'SOURCE-FREEZE.json').read_text());filters=['context_lease_cache','square_lease_cache','prime_clean_pool_tests','wide_loan_policy_tests','reverse_budget_tests','fin1_fold_tests','t0_shared_product_tests','core_loan_fold_tests','phase_cubic_cap_tests','phase_pebble','phase_fit','phase_fusion','zero_carry','plan7_tests','terminal_contract_tests','terminal_birth_phase_tests','direct_transport_tests'];counts=[]
 for i,filter in enumerate(filters):
  name='tests-'+str(i);run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit',filter,'--','--nocapture','--test-threads=1'],name);a=re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/(name+'.log')).read_text());assert len(a)==1;counts.append(int(a[0]))
 assert counts==[1,1,2,1,1,1,1,1,1,3,1,4,3,2,3,1,1];run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build');start=time.time();run(['timeout','1800',str(t/'target/release/build_circuit')],'generate');assert all(sha(t/path)==h for path,h in{**f['source_files'],**f['protected_files']}.items());stages=re.findall(r'^GENERIC_STAGE[^\n]+',(r/'generate.log').read_text(),re.M);last=stages[-1];header=(t/'ops.bin').open('rb').read(16);assert header[:8]==b'QECCOPSZ';result={'status':'CONTEXT213_FINISHED_NONCE0_NOT_GATED_OR_SCORED','native_tests':sum(counts),'native_test_counts':counts,'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'native_stream_sha256':sha(t/'ops.bin'),'operations':int.from_bytes(header[8:],'little'),'qubits':int(re.search(r'nq=(\d+)',last)[1]),'classical_bits':int(re.search(r'nb=(\d+)',last)[1]),'diagnostic_weight':float(re.search(r'depth_weight=([\d.]+)',last)[1]),'stages':stages,'seconds':time.time()-start,'scope':f['scope']};(r/'FINISHED-RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(r/'run.exit').write_text('0\n');print(json.dumps(result),flush=True)
except BaseException:
 (r/'run.exit').write_text('1\n');raise
