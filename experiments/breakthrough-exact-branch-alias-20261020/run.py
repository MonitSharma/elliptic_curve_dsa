import hashlib,json,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'tool';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,(name,rc)
try:
 run(['python3','prepare.py'],'prepare',r)
 run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','exact_branch_alias','--','--nocapture'],'tests',t)
 run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','exact_branch_alias'],'build',t)
 f=json.loads((r/'SOURCE_FREEZE.json').read_text());assert all(sha(t/p)==h for p,h in f['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items())
 run(['timeout','1800',str(t/'target/release/exact_branch_alias'),f['parent'],str(r/'public54fc')],'probe',t)
 (r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
