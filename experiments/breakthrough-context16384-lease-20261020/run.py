import hashlib,json,os,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'tool';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t,env=None):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 run(['python3','prepare.py'],'prepare',r);f=json.loads((r/'SOURCE-FREEZE.json').read_text());run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','product_pareto_discover','--','--nocapture'],'tests');assert re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/'tests.log').read_text())==['7'];run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','product_pareto_discover'],'build');start=time.time();run(['timeout','3600',str(t/'target/release/product_pareto_discover'),f['input'],str(r/'context16')],'discover',env=dict(os.environ,RESEARCH_EXTRA_DONORS='16'));assert all(sha(t/p)==h for p,h in f['tool_source_files'].items());a=json.loads((r/'context16.json').read_text());result={'status':'EXACT_CONTEXT_LEASE_COMPONENT_NOT_SCORED','native_controls':7,'leases':len(a['leases']),'proposed':a['proposed'],'diagnostic_saving':a['depth_weight_saving_diagnostic'],'output_stream_sha256':sha(r/'context16.ops.bin'),'max_donor':max((x[2]for x in a['leases']),default=None),'seconds':time.time()-start,'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json')};(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(r/'run.exit').write_text('0\n');print(json.dumps(result),flush=True)
except BaseException:
 (r/'run.exit').write_text('1\n');raise
