import hashlib,json,os,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent
def run(cmd,name,env=None):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=r/'tool',env=env,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');code=p.wait()
 (r/(name+'.exit')).write_text(str(code)+'\n');assert code==0,name
try:
 run(['cargo','build','--release','--offline'],'build')
 exe=r/'tool/target/release/value_prefilter';(r/'BINARY.sha256').write_text(hashlib.sha256(exe.read_bytes()).hexdigest()+'\n')
 args=[str(exe),str(ws/'breakthrough-public140-finished-20261020/candidate/ops.bin'),'1','65536','8',str(r/'production.jsonl'),'UNUSED','64']
 run(args,'qualification',dict(os.environ,QUALIFY='1'))
 assert 'QUALIFICATION_PASS' in(r/'qualification.log').read_text()
 (r/'QUALIFICATION.json').write_text(json.dumps({'status':'PASS','unique_nonce_controls':8,'production_screens':0,'log_sha256':hashlib.sha256((r/'qualification.log').read_bytes()).hexdigest()},indent=2)+'\n')
 run(args,'search')
 rows=[json.loads(x)for x in(r/'production.jsonl').read_text().splitlines()];passed=sorted(x['nonce']for x in rows if x['pass']);nonces=sorted(x['nonce']for x in rows)
 assert len(set(nonces))==len(nonces)and nonces==list(range(1,max(nonces)+1))
 result={'status':'LOWEST_PASS_FOUND'if passed else'EXHAUSTED_DECLARED_PREFIX','selected_nonce':min(passed)if passed else None,'production_screens':len(rows),'highest_screened':max(nonces),'passes':passed,'control_unique_nonces':8,'control_nonces':'1..8, partial-packet state controls, repeated in production','production_rows_sha256':hashlib.sha256((r/'production.jsonl').read_bytes()).hexdigest()}
 (r/'SEARCH-RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
