"""Apply the independent hard limit only to Y15 fold/shed planning."""
import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-paused-read-20261020';audit=ws/'breakthrough-paused-pool-audit-20261020'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not t.exists()and(old/'run.exit').read_text().strip()=='0'and(audit/'run-v2.exit').read_text().strip()=='0'
ad=json.loads((old/'ADMISSION-RESULT.json').read_text());assert [row['exit']for row in ad['cases']]==[0,101]
assert json.loads((audit/'POOL-AUDIT.json').read_text())['status']=='ORIGINAL_CONTROL_EXACT_SAME_CANDIDATE_POOL_FAILURE'
f=json.loads((old/'SOURCE_FREEZE.json').read_text());assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'observer/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'observer');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes()
def region_replace(raw,begin,end,old,new):
 start=raw.index(begin);finish=raw.index(end,start);part=raw[start:finish];assert old in part
 return raw[:start]+part.replace(old,new)+raw[finish:]
raw=region_replace(raw,b'fn fold_plan_d(',b'fn fold_plan_0(',b'cells::cap()',b'hard_carry_cap()')
raw=region_replace(raw,b'fn body(c: ',b'fn body_capped(',b'cells::cap()',b'hard_carry_cap()')
raw=region_replace(raw,b'fn body_capped(',b'pub(super) fn fwd_tick(',b'cells::cap()',b'hard_carry_cap()')
p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in f['protected_files'].items())
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'fold-only.patch').write_bytes(subprocess.run(['git','diff','--no-index',str(old/'observer/src/point_add/y15_onefold.rs'),str(p)],capture_output=True,check=False).stdout)
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],
 'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
 'caps':[1234,1233],'walk_and_square_planner_caps':1234,'scope':'Y15 fold_plan_d, body shed/drop/copy planning and body peak assertion use independent hardcarry. Tested seven-carry schedule retained. Other original planners/windows/iterations unchanged; previous paused-read contracts remain audited. Preserve Y42 allocator assertions; exact13f6 baseline required. No final gate/nonce or scored result.'},indent=2)+'\n')
