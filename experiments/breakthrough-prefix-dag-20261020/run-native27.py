import hashlib,json,re,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t):
 with(r/(name+'.log')).open('xb')as out:
  p=subprocess.Popen(['timeout','1800']+cmd,cwd=cwd,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 run(['python3','prepare.py'],'prepare',r);f=json.loads((r/'SOURCE_FREEZE.json').read_text());run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','prefix_schedule_tests','--','--nocapture','--test-threads=1'],'tests');assert re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/'tests.log').read_text())==['2'];run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','exact_native_live_forward_prefix_matches_every_independent_fourteen_bit_input','--','--nocapture','--test-threads=1'],'original-control');assert re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/'original-control.log').read_text())==['1'];assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());(r/'NATIVE-RESULT.json').write_text(json.dumps({'status':'NATIVE_PREFIX_COMPONENT_PASS_NOT_POINT_ADD_RECORD','native_tests':3,'inputs':16384,'guards':3,'measurement_modes':15,'prefix_ANDs':31,'prefix_HMRs':11,'original_helper_peak':31,'helper_peak':27,'final_helpers':20,'additional_nonlinear_phase_gates':0,'source_freeze_sha256':sha(r/'SOURCE_FREEZE.json'),'scope':f['scope']},indent=2)+'\n');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
