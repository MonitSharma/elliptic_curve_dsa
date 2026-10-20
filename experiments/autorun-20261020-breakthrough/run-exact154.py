import hashlib,json,os,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'candidate';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();env=dict(os.environ,PEBBLE_HARD_CAP='1234')
def run(args,name,cwd=t):
 with(r/(name+'.log')).open('xb')as out:
  p=subprocess.Popen(['timeout','1800']+args,cwd=cwd,env=env,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 run(['python3','prepare.py'],'prepare',r);f=json.loads((r/'SOURCE-FREEZE.json').read_text());filters=['exact154_cache','prime_clean_pool_tests','wide_loan_policy_tests','reverse_budget_tests','fin1_fold_tests','t0_shared_product_tests','core_loan_fold_tests','phase_cubic_cap_tests','phase_pebble','phase_fit','phase_fusion','zero_carry','plan7_tests','terminal_contract_tests','terminal_birth_phase_tests','direct_transport_tests']
 counts=[]
 for i,filter in enumerate(filters):
  name='tests-'+str(i);run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit',filter,'--','--nocapture','--test-threads=1'],name);a=re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/(name+'.log')).read_text());assert len(a)==1;counts.append(int(a[0]))
 assert counts==[1,2,1,1,1,1,1,1,3,1,4,3,2,3,1,1]
 assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build');start=time.time();run([str(t/'target/release/build_circuit')],'generate');assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert sha(t/'ops.bin')==f['proof_rewritten_stream_sha256'],'Native output must reproduce exact prover stream including nonce0 tail'
 log=(r/'generate.log').read_text();matches=re.findall(r'EXACT154_CACHE leases=(\d+) operations=(\d+) qubits=(\d+) bits=(\d+)',log);assert len(matches)==1;leases,ops,q,bits=map(int,matches[0]);assert leases==154 and ops+96==10553247
 (r/'FINISHED-RESULT.json').write_text(json.dumps({'status':'FINISHED_NONCE0_NATIVE_REPRODUCES_EXACT_PROVER_STREAM_NOT_YET_GATED','native_tests':sum(counts),'native_test_counts':counts,'stream_sha256':sha(t/'ops.bin'),'operations':ops+96,'qubits':q,'classical_bits':bits,'seconds':time.time()-start,'native_binary_sha256':sha(t/'target/release/build_circuit'),'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'scope':'Independent exact154 candidate. Native tests and exact output binding only; separate final gate versus current official4045 required before any nonce screening.'},indent=2)+'\n');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
