import hashlib,json,os,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';os.environ['PEBBLE_HARD_CAP']='1234';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t,env=None):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
def records(path):
 with path.open('rb',buffering=0)as raw:
  header=raw.read(16);assert header[:8]==b'QECCOPSZ';count=int.from_bytes(header[8:],'little');h=hashlib.sha3_256();size=0;p=subprocess.Popen(['zstd','-dc'],stdin=raw,stdout=subprocess.PIPE)
  while chunk:=p.stdout.read(1<<20):h.update(chunk);size+=len(chunk)
  assert p.wait()==0 and size==56*count
 return count,h.hexdigest()
try:
 assert(r/'run.exit').read_text().strip()=='1'and not(r/'RESULT.json').exists();f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());counts=[]
 filters=['exact_strip_port_tests','prime_clean_pool_tests','wide_loan_policy_tests','reverse_budget_tests','fin1_fold_tests','t0_shared_product_tests','core_loan_fold_tests','phase_cubic_cap_tests','phase_pebble','phase_fit','phase_fusion','zero_carry','plan7_tests','terminal_contract_tests','terminal_birth_phase_tests','direct_transport_tests']
 for i,filter in enumerate(filters):
  name='tests-env-'+str(i);run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit',filter,'--','--nocapture','--test-threads=1'],name);actual=re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/(name+'.log')).read_text());assert len(actual)==1 and int(actual[0])>0;counts.append(int(actual[0]))
 assert counts==[1,2,1,1,1,1,1,1,3,1,4,3,2,3,1,1],counts
 run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build');rows=[]
 for mode in f['modes']:
  assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());dest=r/mode;dest.mkdir();start=time.time();run([str(t/'target/release/build_circuit')],'generate-'+mode,dest,dict(os.environ,EXACT_NATIVE_PORT_MODE=mode));raw_count,raw_hash=records(dest/'raw.ops.bin');output_count,output_hash=records(dest/'ops.bin')
  if mode=='control':assert raw_count==f['baseline_raw_count']and raw_hash==f['baseline_raw_sha3'],'Control raw must reproduce a4ee source exactly'
  log=(r/('generate-'+mode+'.log')).read_text();stages=re.findall(r'^GENERIC_STAGE[^\n]+',log,re.M);assert len(stages)>=12;fields=dict(re.findall(r'(\w+)=([^ ]+)',stages[-1]));row={'mode':mode,'raw_count':raw_count,'raw_records_sha3':raw_hash,'raw_compressed_sha256':sha(dest/'raw.ops.bin'),'output_count':output_count,'output_records_sha3':output_hash,'output_compressed_sha256':sha(dest/'ops.bin'),'qubits':int(fields['nq']),'diagnostic_weight':float(fields['depth_weight']),'generic_stages':stages,'seconds':time.time()-start};rows.append(row);(r/'PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({k:v for k,v in row.items()if k!='generic_stages'}),flush=True)
 assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());(r/'RESULT.json').write_text(json.dumps({'status':'EXACT_NATIVE_PORT_RESEARCH_NOT_GATED_OR_SCORED','native_controls':sum(counts),'native_test_counts':counts,'cases':rows,'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json')},indent=2)+'\n');(r/'resumed.exit').write_text('0\n')
except BaseException:
 (r/'resumed.exit').write_text('1\n');raise
