import hashlib,json,os,resource,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());src=r.parent/'breakthrough-local-de8-replay-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'local-tool'/p)==h for p,h in f['tool_source_files'].items());assert sha(src/'candidate/ops.bin')==f['input_stream_sha256'];deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/p)==h for p,h in f['protected_files'].items());exe=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/product_pareto_discover';stats=r.parent/'breakthrough-public1829-width-port-local-v4-20261020/stats-tool/target/release/native_width_stats';results={}
def limits():resource.setrlimit(resource.RLIMIT_AS,(5*1024**3,5*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
for extra in f['declared_extra_donor_budgets']:
 name='extra'+str(extra);start=time.monotonic()
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(['timeout','1200',str(exe),str(src/'candidate/ops.bin'),str(r/name)],env=dict(os.environ,RESEARCH_EXTRA_DONORS=str(extra)),stdout=log,stderr=subprocess.STDOUT,preexec_fn=limits);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');row={'exit':rc,'seconds':time.monotonic()-start}
 if rc==0:
  proof=json.loads((r/(name+'.json')).read_text());assert all(x[2]<1464+extra for x in proof['leases'])
  with(r/(name+'-stats.log')).open('xb')as log:subprocess.run([str(stats),str(r/(name+'.ops.bin')),str(r/(name+'-STATS.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)
  s=json.loads((r/(name+'-STATS.json')).read_text());assert s['qubits_protected_analyzer']<=1464+extra;row.update(leases=len(proof['leases']),proposed=proof['proposed'],diagnostic_saving=proof['depth_weight_saving_diagnostic'],output_sha256=sha(r/(name+'.ops.bin')),static_diagnostics=s)
 results[name]=row;(r/'PROGRESS.json').write_text(json.dumps(results,indent=2)+'\n')
(r/'RESULT.json').write_text(json.dumps({'status':'FIXED_SECOND_CACHE_RESOURCE_GRID_COMPLETE_NOT_SCORED','native_controls':9,'cases':results,'scope':f['scope']},indent=2)+'\n')
