import hashlib,json,os,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();os.environ['PEBBLE_HARD_CAP']='1234'
def run(cmd,name,cwd=t,env=None):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 run(['python3','prepare.py'],'prepare',r);f=json.loads((r/'SOURCE-FREEZE.json').read_text());filters=['prefix_retained_core_tests','prefix_retained_full_fold_tests','prefix_window_policy_tests','prefix27_full_fold_tests','selective_room_tests','prefix27_width57_tests','prefix27_global_policy_tests','prefix27_activation_tests','prefix_schedule_cleanup_tests','prefix_schedule_tests'];counts=[]
 for i,filter in enumerate(filters):
  name='tests-'+str(i);run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit',filter,'--','--nocapture','--test-threads=1'],name);a=re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/(name+'.log')).read_text());assert len(a)==1;counts.append(int(a[0]))
 assert counts==[1,1,1,1,1,2,2,1,1,2];run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build');rows=[]
 for mode in ['tick129','tick130']:
  assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());dest=r/mode;dest.mkdir();start=time.time();
  try:run(['timeout','1800',str(t/'target/release/build_circuit')],'generate-'+mode,dest,dict(os.environ,BREAK_TICK_MODE=mode))
  except AssertionError:
   rows.append({'mode':mode,'status':'CONSTRUCTION_FAILED_UNCHANGED_BINDINGS','exit':(r/('generate-'+mode+'.exit')).read_text().strip(),'seconds':time.time()-start});(r/'PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');continue
  assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());row={'mode':mode,'stream_sha256':sha(dest/'ops.bin'),'operations':int.from_bytes((dest/'ops.bin').open('rb').read(16)[8:],'little'),'seconds':time.time()-start}
  if mode=='control':assert row['stream_sha256']==f['control_exact_public_stream_sha256'],'Full control differs from exact current public source stream; do not weaken bindings'
  rows.append(row);(r/'PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
 (r/'RESULT.json').write_text(json.dumps({'status':'ISOLATED_TICK_CONSTRUCTIONS_TERMINAL_NOT_GATED_OR_SCORED','native_test_counts':counts,'cases':rows,'scope':f['scope']},indent=2)+'\n');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
