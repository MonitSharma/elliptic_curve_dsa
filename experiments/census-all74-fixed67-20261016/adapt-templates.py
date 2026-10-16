from pathlib import Path
import hashlib,json
r=Path(__file__).resolve().parent;t=r/'templates';names=['run_all70_cache67.py','consolidate_all70_cache67.py','prepare_all70_native67.py','verify_all70_native67.py','qualify_all70_fixed67.py']
for name in names:
 s=(t/name).read_text().replace('all70','all74').replace('ALL70','ALL74');s=s.replace('Fresh ALL74 value model/mask bound to06cdc5de... source/prefix','Fresh ALL74 value model/mask bound to the new ALL74 base source/prefix')
 if name=='run_all70_cache67.py':
  s=s.replace("before=sha(previous)","assert sha(exe)==bindings['generator_sha256'] and sha(verifier)==bindings['verifier_sha256'];before=sha(previous)")
  s=s.replace("after=sha(output);assert sha(previous)==before", "after=sha(output);assert sha(exe)==bindings['generator_sha256'] and sha(verifier)==bindings['verifier_sha256'];assert sha(previous)==before")
  needle="stdout=out,stderr=subprocess.STDOUT,env=env,check=True)\n  for script,namepart"
  assert needle in s;s=s.replace(needle,"stdout=out,stderr=subprocess.STDOUT,env=env,cwd=r,check=True)\n  for script,namepart")
 if name=='qualify_all70_fixed67.py':
  s=s.replace("freeze=json.loads((r/'ALL74_FIXED67_FREEZE.json').read_text());", "assert json.loads((r/'all74-cache67-20261016/stage-67-resources.jsonl').read_text())['qubits']==1234;freeze=json.loads((r/'ALL74_FIXED67_FREEZE.json').read_text());")
  needle="(d/'census-summary.json').write_text"
  extra='''# Retain every fixed-sample lane change; these use the common physical MR tape,
# not the cache certificate's projected-original MR coupling.
sample_changes=[];kind_counts={};kind_repairs={k:0 for k in ['value','phase','dirty']};kind_regressions={k:0 for k in kind_repairs};passing_shots=failing_shots=passing_batches=failing_batches=0
for role,data in zip(['parent','candidate'],rows):
 kind_counts[role]={kind:sum(x[kind+'_shots'] for x in data.values()) for kind in kind_repairs};kind_counts[role]['failed_shots']=sum(len(x['failures'])for x in data.values())
for batch in range(32768):
 before={x['lane']:x for x in a[batch]['failures']};after={x['lane']:x for x in b[batch]['failures']};passing_batches+=bool(before)and not after;failing_batches+=bool(after)and not before
 for lane in sorted(before.keys()|after.keys()):
  x=before.get(lane,{});y=after.get(lane,{})
  if x and y:assert x['k1']==y['k1']and x['k2']==y['k2']
  passing_shots+=bool(x)and not y;failing_shots+=bool(y)and not x
  for kind in kind_repairs:
   kind_repairs[kind]+=bool(x.get(kind,0))and not y.get(kind,0);kind_regressions[kind]+=bool(y.get(kind,0))and not x.get(kind,0)
  if x!=y:sample_changes.append(dict(batch=batch,lane=lane,parent=x or None,candidate=y or None))
(d/'census-lane-changes.json').write_text(json.dumps(sample_changes,indent=2)+'\\n')
summary.update(kind_counts=kind_counts,sample_newly_passing_shots=passing_shots,sample_newly_failing_shots=failing_shots,sample_newly_passing_batches=passing_batches,sample_newly_failing_batches=failing_batches,sample_kind_repairs=kind_repairs,sample_kind_regressions=kind_regressions,physical_MR_tape_coupling='Common raw labelled MR stream; added private cache draws shift old draw ordinals. Changes are paired sample changes, not fixed-projected-original-MR causal repair claims.',lane_changes_sha256=sha(d/'census-lane-changes.json'))
'''
  assert needle in s;s=s.replace(needle,extra+needle)
 if name=='prepare_all70_native67.py':
  s=s.replace("freeze['resources']=resources", "assert resources['qubits']==1234;freeze['resources']=resources")
 (r/name.replace('all70','all74')).write_text(s)
# Stable recipe is copied byte-for-byte, never rebuilt from a guessed config list.
data=(t/'PRODUCT67_FREEZE.json').read_bytes();assert hashlib.sha256(data).hexdigest()=='30922550c7301a745bb7d611a2b20e38a9f58121e37f8ccdaf5e5073eae4471c';(r/'PRODUCT67_FREEZE.json').write_bytes(data)
(r/'TEMPLATE-PINS.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in t.iterdir()if p.is_file()},indent=2)+'\n')
