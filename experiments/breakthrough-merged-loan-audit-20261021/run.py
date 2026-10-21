import hashlib,json,resource,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-polynomial-rematerialization-20261021';f=json.loads((r/'SOURCE-FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'local-tool'/n)==h for n,h in f['tool_source_files'].items());deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/n)==h for n,h in f['protected_files'].items());assert sha(r/'official-ffe20.ops.bin')==f['input_streams']['official_ffe20'];deadline=time.monotonic()+1800
while not(old/'run.exit').exists():assert time.monotonic()<deadline;time.sleep(2)
assert(old/'run.exit').read_text().strip()=='0';grid=json.loads((old/'RESULT.json').read_text());assert all(x['exit']==0 for x in grid['cases']);plans={'plans':[{'path':str(old/('cap'+str(x['cap'])+'.json')),'sha256':sha(old/('cap'+str(x['cap'])+'.json'))}for x in grid['cases']]};(r/'INPUT-PLANS.json').write_text(json.dumps(plans,indent=2)+'\n');exe=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/merge_rematerialization_plans'
def limits():resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
with(r/'merge.log').open('xb')as log:subprocess.run(['timeout','900',str(exe),str(r/'official-ffe20.ops.bin'),str(r/'INPUT-PLANS.json'),str(r)],stdout=log,stderr=subprocess.STDOUT,preexec_fn=limits,check=True)
assert all(sha(Path(x['path']))==x['sha256']for x in plans['plans'])
