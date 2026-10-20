import hashlib,json,os,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t,env=None):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');return rc
try:
 assert run(['python3','prepare.py'],'prepare',r)==0;f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','compact_compare_tests','--','--nocapture','--test-threads=1'],'comparator-tests')==0;assert 'test result: ok. 4 passed; 0 failed;'in(r/'comparator-tests.log').read_text();assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','stack_plan7_','--','--nocapture','--test-threads=1'],'tests')==0;assert 'test result: ok. 4 passed; 0 failed;'in(r/'tests.log').read_text();assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','public_reverse_drop_policy_tests','--','--nocapture','--test-threads=1'],'drop-policy-tests')==0;assert 'test result: ok. 1 passed; 0 failed;'in(r/'drop-policy-tests.log').read_text();assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build')==0;rows=[]
 for mode in f['modes']:
  assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());dest=r/mode;dest.mkdir();start=time.time();rc=run(['timeout','1800',str(t/'target/release/build_circuit')],'generate-'+mode,dest,dict(os.environ,STACK_WIDTH_RESEARCH=mode));row={'mode':mode,'exit':rc,'seconds':time.time()-start}
  if rc:
   assert mode!='public','Exact public control failed; stop rather than bypass binding'
  else:
   path=dest/'ops.bin';header=path.open('rb').read(16);assert header[:8]==b'QECCOPSZ';row.update(stream_sha256=sha(path),operations=int.from_bytes(header[8:],'little'))
   if mode=='public':assert row['stream_sha256']==f['public_exact_sha256'],'Every current publicacd0 output byte must reproduce'
   stats=r.parent/'breakthrough-stackv3-width-stats-20261020/tool/target/release/native_width_stats';assert run([str(stats),str(path),str(r/(mode+'-STATS.json'))],'stats-'+mode,r)==0;st=json.loads((r/(mode+'-STATS.json')).read_text());row.update(qubits=st['qubits_protected_analyzer'],diagnostic_weight=st['fair_guard_depth_proxy'],records_sha3=st['records_sha3'])
  rows.append(row);(r/'PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
 assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());(r/'RESULT.json').write_text(json.dumps({'status':'CURRENT_PUBLIC_ACD0_EXACT_COMPONENT_COMPLETE_WIDTH_GRID_NOT_SCORED','cases':rows,'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json')},indent=2)+'\n');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
