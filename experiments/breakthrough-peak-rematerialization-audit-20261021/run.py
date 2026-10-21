import hashlib,json,resource,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'local-tool'/p)==h for p,h in f['tool_source_files'].items());deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/p)==h for p,h in f['protected_files'].items());exe=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/peak_rematerialization_audit';stats=r.parent/'breakthrough-public1829-width-port-local-v4-20261020/stats-tool/target/release/native_width_stats';results={}
def limits():resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
for name,path in [('public1829',r.parent/'breakthrough-public1829-width-port-local-v4-20261020/public/ops.bin'),('official_ffe20',r/'official-ffe20.ops.bin')]:
 if False:
  deadline=time.monotonic()+1800
  while not(r.parent/'breakthrough-local-de8-replay-20261020/run.exit').exists():assert time.monotonic()<deadline;time.sleep(2)
  assert(r.parent/'breakthrough-local-de8-replay-20261020/run.exit').read_text().strip()=='0'
 assert sha(path)==f['input_streams'][name];start=time.monotonic()
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(['timeout','900',str(exe),str(path),str(r/name)],stdout=log,stderr=subprocess.STDOUT,preexec_fn=limits);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');row={'exit':rc,'seconds':time.monotonic()-start}
 if rc==0:
  report=json.loads((r/(name+'.json')).read_text());row.update(report)
 results[name]=row;(r/'PROGRESS.json').write_text(json.dumps(results,indent=2)+'\n')
(r/'RESULT.json').write_text(json.dumps({'status':'COMPONENT_GRID_COMPLETE_PRESERVE_RESOURCE_FAILURES_NOT_SCORED','native_controls':5,'cases':results,'scope':f['scope'],'binary_sha256':sha(exe)},indent=2)+'\n')
