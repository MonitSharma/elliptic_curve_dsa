import hashlib,json,resource,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'local-tool'/n)==h for n,h in f['tool_source_files'].items());deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/n)==h for n,h in f['protected_files'].items());stream=r/'official-ffe20.ops.bin';assert sha(stream)==f['input_streams']['official_ffe20'];exe=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/polynomial_rematerialization';results=[]
def limits():resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
for cap in f['declared_caps']:
 start=time.monotonic()
 with(r/('cap'+str(cap)+'.log')).open('xb')as log:p=subprocess.run(['timeout','900',str(exe),str(stream),str(r/('cap'+str(cap))),str(cap),str(f["recipe_term_limit"])],stdout=log,stderr=subprocess.STDOUT,preexec_fn=limits)
 row={'cap':cap,'exit':p.returncode,'seconds':time.monotonic()-start}
 if p.returncode==0:
  v=json.loads((r/('cap'+str(cap)+'.json')).read_text());row.update({k:v[k]for k in ['all_regions_covered','unproved_regions','unfinished_final_region','extra_executed_toffoli_per_shot_upper_bound']});row['regions']=len(v['regions']);row['result_sha256']=sha(r/('cap'+str(cap)+'.json'))
 results.append(row);(r/'PROGRESS.json').write_text(json.dumps(results,indent=2)+'\n')
(r/'RESULT.json').write_text(json.dumps({'status':'READ_ONLY_FIXED_CAP_GRID_COMPLETE_NOT_ACHIEVED_RESOURCES','native_controls':10,'cases':results,'scope':f['scope']},indent=2)+'\n')
