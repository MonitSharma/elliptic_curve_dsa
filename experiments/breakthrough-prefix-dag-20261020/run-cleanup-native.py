import hashlib,json,re,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t):
 with(r/(name+'.log')).open('xb')as out:
  p=subprocess.Popen(['timeout','1800']+cmd,cwd=cwd,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 run(['python3','prepare.py'],'prepare',r);f=json.loads((r/'SOURCE_FREEZE.json').read_text());counts=[]
 for filter,name in [('prefix_schedule_cleanup_tests','cleanup'),('prefix27_full_fold_tests','full-fold'),('prefix_schedule_tests','retained-control')]:
  run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit',filter,'--','--nocapture','--test-threads=1'],name);a=re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/(name+'.log')).read_text());assert len(a)==1;counts.append(int(a[0]))
 assert counts==[1,1,2];assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());(r/'NATIVE-RESULT.json').write_text(json.dumps({'status':'NATIVE_COMPLETE_FOLD_COMPONENT_PASS_NOT_POINT_ADD_RECORD','native_tests':4,'counts':counts,'source_freeze_sha256':sha(r/'SOURCE_FREEZE.json'),'full_fold_diagnostic_lines':[l for l in(r/'full-fold.log').read_text().splitlines()if l.startswith('PREFIX27_FULL_FOLD')],'scope':f['scope']},indent=2)+'\n');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
