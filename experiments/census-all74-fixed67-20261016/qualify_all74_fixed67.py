"""Consume the sole predeclared whole composite sample, never inspect interim rates."""
from pathlib import Path
import hashlib,json,math,subprocess,concurrent.futures
r=Path(__file__).resolve().parent;d=r/'all74-native67-20261016';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((r/'all74-cache67-20261016/DECLARATION.json').read_text());gate=plan['sole_final_fresh_gate'];assert gate['label']=='product-all74-fixed67-independent-20261016-v1' and gate['batches_per_source']==32768 and gate['first_batch']==0
assert json.loads((r/'all74-cache67-20261016/stage-67-resources.jsonl').read_text())['qubits']==1234;freeze=json.loads((r/'ALL74_FIXED67_FREEZE.json').read_text());receipt=json.loads((d/'NATIVE_RECEIPT.json').read_text());candidate=d/'candidate/ops.bin';parent=r/'tip/ops.bin'
assert receipt['native_stream_sha256']==freeze['external_stream_sha256']==sha(candidate);assert sha(parent)==plan['original_stream_sha256']
stages=json.loads((r/'all74-cache67-20261016/CACHE_STAGE_RECEIPTS.json').read_text());assert len(stages)==67 and all(x['status']=='UNIVERSAL_PASS'for x in stages)
certificate=json.loads((r/'all74-cache67-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json').read_text());assert certificate['stage_count']==67 and certificate['candidate_stream_sha256']==sha(candidate)and certificate['baseline_stream_sha256']==freeze['all74_parent_sha256']
runner=Path('/home/hclau/ecdsa_research/simd-census-v2-20261016/bin/simd_census_v2');runnerhash='790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66';assert sha(runner)==runnerhash
bindings={'declaration_sha256':sha(r/'all74-cache67-20261016/DECLARATION.json'),'final_freeze_sha256':sha(r/'ALL74_FIXED67_FREEZE.json'),'native_receipt_sha256':sha(d/'NATIVE_RECEIPT.json'),'parent_sha256':sha(parent),'candidate_sha256':sha(candidate),'runner':str(runner),'runner_sha256':runnerhash,'label':gate['label'],'first_batch':0,'batches_each':32768,'shots_per_batch':64,'workers_each':1,'total_cpu_workers':2,'no_nonce_search':True,'no_interim_selection':True}
bindings['cache_certificate_sha256']=sha(r/'all74-cache67-20261016/CACHE_EQUIVALENCE_CERTIFICATE.json')
assert bindings['cache_certificate_sha256']==receipt['cache_certificate_sha256']
assert not(d/'CENSUS_FROZEN_BINDINGS.json').exists();(d/'CENSUS_FROZEN_BINDINGS.json').write_text(json.dumps(bindings,indent=2)+'\n')
available=int(next(x.split()[1]for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))*1024;assert available>=124*1024**3
def run(role,ops):
 out=d/f'{role}-census.jsonl';assert not out.exists();assert sha(runner)==runnerhash
 with (d/f'{role}-census-preflight.json').open('w')as f:subprocess.run(['python3','/home/hclau/ecdsa_research/server-preflight.py'],stdout=f,check=True)
 with (d/f'{role}-census.log').open('w')as log:
  p=subprocess.Popen([str(runner),str(ops),gate['label'],'0','32768','1',str(out),'0'],stdout=log,stderr=subprocess.STDOUT);(d/f'{role}-census.pid').write_text(str(p.pid)+'\n');rc=p.wait()
 (d/f'{role}-census.exit').write_text(str(rc)+'\n');assert rc==0
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
 futures=[pool.submit(run,role,ops)for role,ops in [('parent',parent),('candidate',candidate)]]
 for future in futures:future.result()
rows=[]
for role in ['parent','candidate']:
 data=[json.loads(line)for line in(d/f'{role}-census.jsonl').read_text().splitlines()];assert len(data)==32768 and sorted(x['batch']for x in data)==list(range(32768))and all(x['shots']==64 for x in data);rows.append({x['batch']:x for x in data})
a,b=rows;delta=[(a[i]['toffoli']-b[i]['toffoli'])/64 for i in range(32768)];mean=sum(delta)/32768;fail=[sum(bool(x['failures'])for x in data.values())for data in rows];dirty=[sum(x['dirty_shots']for x in data.values())for data in rows]
summary={'status':'TERMINAL_FIXED_ALL74_FIXED67_CENSUS_NOT_A_RESOURCE_RECORD','label':gate['label'],'batches_each':32768,'shots_each':2097152,'parent_sha256':sha(parent),'candidate_sha256':sha(candidate),'failed_batches':dict(zip(['parent','candidate'],fail)),'failures_per_packet':dict(zip(['parent','candidate'],[141*f/32768 for f in fail])),'dirty_shots':dirty,'paired_mean_T_saving':mean,'saving_standard_error':math.sqrt(sum((x-mean)**2 for x in delta)/(32768*32767)),'failure_gate_pass':fail[1]<=fail[0]and 141*fail[1]/32768<=18 and dirty[1]==0,'all_declared_rows_retained':True,'nonce_search_performed':False,'score':None}
# Retain every fixed-sample lane change; these use the common physical MR tape,
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
(d/'census-lane-changes.json').write_text(json.dumps(sample_changes,indent=2)+'\n')
summary.update(kind_counts=kind_counts,sample_newly_passing_shots=passing_shots,sample_newly_failing_shots=failing_shots,sample_newly_passing_batches=passing_batches,sample_newly_failing_batches=failing_batches,sample_kind_repairs=kind_repairs,sample_kind_regressions=kind_regressions,physical_MR_tape_coupling='Common raw labelled MR stream; added private cache draws shift old draw ordinals. Changes are paired sample changes, not fixed-projected-original-MR causal repair claims.',lane_changes_sha256=sha(d/'census-lane-changes.json'))
(d/'census-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
