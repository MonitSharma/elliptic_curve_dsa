import hashlib,json,subprocess,time
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research');r=ws/'breakthrough-certified-leases-20261020';old=ws/'breakthrough-guarded-lease-prover-20261020';t=old/'tool';c=ws/'breakthrough-certified-prefix-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
try:
 assert not(r/'INPUT-FREEZE.json').exists();f=json.loads((old/'SOURCE_FREEZE.json').read_text());cf=json.loads((c/'SOURCE_FREEZE.json').read_text());assert(c/'run.exit').read_text().strip()=='0'
 assert all(sha(t/p)==h for p,h in f['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items());assert all(sha(c/'observer'/p)==h for p,h in{**cf['source_files'],**cf['protected_files']}.items())
 path=c/'certified/ops.bin';assert sha(path)=='85958b9f90cc93c7bba94d158cba2b4dde890bf9f4231cd70dc5b4fd9f1218b2';exe=t/'target/release/product_pareto_discover'
 (r/'INPUT-FREEZE.json').write_text(json.dumps({'input_path':str(path),'input_sha256':sha(path),'tool_freeze_path':str(old/'SOURCE_FREEZE.json'),'tool_freeze_sha256':sha(old/'SOURCE_FREEZE.json'),'source_freeze_path':str(c/'SOURCE_FREEZE.json'),'source_freeze_sha256':sha(c/'SOURCE_FREEZE.json'),'binary_path':str(exe),'binary_sha256':sha(exe),'scope':'Fresh exact guarded lease discovery on original-stream certified prefix. No nonce, gate or scored result; input certificate exactness still needs separate review.'},indent=2)+'\n')
 start=time.time()
 with(r/'discovery.log').open('xb')as out:
  p=subprocess.Popen(['timeout','1800',str(exe),str(path),str(r/'certified')],stdout=out,stderr=subprocess.STDOUT);(r/'discovery.pid').write_text(str(p.pid)+'\n');rc=p.wait()
 (r/'discovery.exit').write_text(str(rc)+'\n');assert rc==0
 result=json.loads((r/'certified.json').read_text());(r/'RESULT.json').write_text(json.dumps({'status':'EXACT_COMPONENT_DISCOVERY_COMPLETE_NOT_SCORED','proposed':result['proposed'],'proven_leases':len(result['leases']),'depth_weight_saving_diagnostic':result['depth_weight_saving_diagnostic'],'unproved':len(result['rejected_unproven']),'output_sha256':sha(r/'certified.ops.bin'),'seconds':time.time()-start},indent=2)+'\n');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
