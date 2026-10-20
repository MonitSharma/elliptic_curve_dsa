import hashlib,json,os,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
try:
 for cmd,name,cwd in [(['python3','prepare-v2.py'],'prepare-v2',r),(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','export_native_prefix_linear_and_dag','--','--nocapture','--test-threads=1'],'export-v2',t)]:
  with(r/(name+'.log')).open('xb')as out:
   p=subprocess.Popen(cmd,cwd=cwd,env=dict(os.environ,PREFIX_DAG_OUT=str(r/'PREFIX-DAG.json')),stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
  (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
 f=json.loads((r/'SOURCE_FREEZE-v2.json').read_text());assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert 'test result: ok. 1 passed; 0 failed;'in(r/'export-v2.log').read_text();(r/'run-v2.exit').write_text('0\n')
except BaseException:
 (r/'run-v2.exit').write_text('1\n');raise
