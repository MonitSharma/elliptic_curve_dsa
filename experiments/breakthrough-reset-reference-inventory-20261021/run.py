import hashlib,json,resource,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_bytes());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert all(sha(r/'local-tool'/p)==h for p,h in f['tool_source_files'].items());deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/p)==h for p,h in f['protected_files'].items());exe=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/reset_reference_inventory'
paths={'public1829': '/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-public1829-width-port-local-v4-20261020/public/ops.bin', 'compact1233': '/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-compact-context-alias-20261021/cap1233-r012.ops.bin', 'compact1234': '/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-compact-context-alias-20261021/cap1234-t21.ops.bin', 'official_ffe20': '/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-global-quantum-alias-v3-20261021/official-ffe20.ops.bin'};rows={}
def limits():resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
for n,p in paths.items():
 p=Path(p);assert sha(p)==f['input_streams'][n];start=time.monotonic()
 with(r/(n+'.log')).open('xb')as log:
  job=subprocess.Popen(['timeout','900',str(exe),str(p),str(r/n)],stdout=log,stderr=subprocess.STDOUT,preexec_fn=limits);(r/(n+'.pid')).write_text(str(job.pid)+'\n');rc=job.wait()
 (r/(n+'.exit')).write_text(str(rc)+'\n');row={'exit':rc,'seconds':time.monotonic()-start}
 if rc==0:
  data=json.loads((r/(n+'.json')).read_bytes());hits=data['proof']['reset_reference_inventory'];row.update(total=len(hits),by_kind={k:sum(h['reference_kind']==k for h in hits)for k in ['constant','quantum','classical']},report_sha256=sha(r/(n+'.json')))
 rows[n]=row;(r/'PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n')
(r/'RESULT.json').write_text(json.dumps({'status':'READ_ONLY_RESET_REFERENCE_INVENTORY_COMPLETE','cases':rows,'native_controls':18,'binary_sha256':sha(exe),'scope':f['scope']},indent=2)+'\n')
