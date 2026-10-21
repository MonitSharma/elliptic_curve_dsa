import hashlib,json,resource,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_bytes());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'local-tool'/p)==h for p,h in f['tool_source_files'].items());deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/p)==h for p,h in f['protected_files'].items())
parent=r.parent/'breakthrough-compact-generic-repeat-20261021';assert(parent/'run.exit').read_text().strip()=='0';pf=json.loads((parent/'RESULT.json').read_bytes());paths={n:parent/(n+'.ops.bin')for n in ['compact1233','compact1234']};inputs={n:sha(p)for n,p in paths.items()};(r/'INPUT-FREEZE.json').write_text(json.dumps({'streams':inputs,'parent_result_sha256':sha(parent/'RESULT.json'),'scope':'Input circuit streams frozen before any execution; no point inputs.'},indent=2)+'\n')
exe=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/current_cap11';stats=r.parent/'breakthrough-public1829-width-port-local-v4-20261020/stats-tool/target/release/native_width_stats';rows={}
def limits():resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
for n,p in paths.items():
 rr={}
 for mode in ['control9','compat9','cap11']:
  assert sha(p)==inputs[n];key=n+'-'+mode;start=time.monotonic()
  with(r/(key+'.log')).open('xb')as log:job=subprocess.Popen(['timeout','900',str(exe),str(p),str(r/key),mode],stdout=log,stderr=subprocess.STDOUT,preexec_fn=limits);(r/(key+'.pid')).write_text(str(job.pid)+'\n');rc=job.wait()
  (r/(key+'.exit')).write_text(str(rc)+'\n');assert rc==0,(n,mode,rc)
  output=r/(key+'.ops.bin');rr[mode]={'seconds':time.monotonic()-start,'output_sha256':sha(output),'protected':json.loads((r/(key+'.json')).read_bytes())['qualification']['protected_fullstream_comparisons']}
  if mode=='compat9':assert rr['control9']['output_sha256']==rr['compat9']['output_sha256'],'Independent cap9 stream control failed'
  if mode=='cap11':
   with(r/(key+'-stats.log')).open('xb')as log:subprocess.run([str(stats),str(output),str(r/(key+'-STATS.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)
   rr[mode]['static_diagnostics']=json.loads((r/(key+'-STATS.json')).read_bytes())
  rows[n]=rr;(r/'PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n')
(r/'RESULT.json').write_text(json.dumps({'status':'CURRENT_CAP11_COMPONENT_COMPLETE_NOT_SCORED','cases':rows,'binary_sha256':sha(exe),'scope':f['scope']},indent=2)+'\n')
