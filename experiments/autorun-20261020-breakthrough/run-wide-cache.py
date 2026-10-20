import hashlib,json,os,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'tool';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(args,log,cwd=t,env=None):
 with(r/log).open('xb')as out:
  p=subprocess.Popen(['timeout','1800']+args,cwd=cwd,env=env,stdout=out,stderr=subprocess.STDOUT);(r/(log+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(log+'.exit')).write_text(str(rc)+'\n');return rc
try:
 assert run(['python3','prepare.py'],'prepare.log',r)==0;f=json.loads((r/'SOURCE_FREEZE.json').read_text());assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','product_pareto_discover','--','--nocapture','--test-threads=1'],'tests.log')==0;assert re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/'tests.log').read_text())==['4'];assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','product_pareto_discover'],'build.log')==0
 rows=[];path=Path(f['input_path']);exe=t/'target/release/product_pareto_discover'
 for budget in f['donor_budgets']:
  assert sha(path)==f['input_sha256']and all(sha(t/p)==h for p,h in f['tool_source_files'].items())and all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items());env=dict(os.environ,RESEARCH_EXTRA_DONORS=str(budget));start=time.time();name='extra'+str(budget);rc=run([str(exe),str(path),str(r/name)],name+'.log',env=env);row={'extra_donor_limit':budget,'exit':rc,'seconds':time.time()-start,'binary_sha256':sha(exe)}
  if rc==0:
   data=json.loads((r/(name+'.json')).read_text());row.update(proposed=data['proposed'],proven_leases=len(data['leases']),diagnostic_depth_weight_saving=data['depth_weight_saving_diagnostic'],output_sha256=sha(r/(name+'.ops.bin')))
  rows.append(row);(r/'PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
 (r/'RESULT.json').write_text(json.dumps({'status':'EXACT_EXTRA_DONOR_COMPONENT_AUDIT_ONLY','cases':rows,'scope':f['scope']},indent=2)+'\n');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
