from pathlib import Path
import json,math,hashlib
root=Path('/home/hclau/ecdsa_research/back-seam-repair-20261016');p=root/'fresh-paired'
assert(root/'fresh-paired.exit').read_text().strip()=='0'
def load(name):
 rows=[json.loads(l)for l in(p/(name+'.jsonl')).read_text().splitlines()];assert len(rows)==4096 and {r['batch']for r in rows}==set(range(4096));return {r['batch']:r for r in rows}
a,b=load('parent'),load('candidate')
def summary(rows):
 out=dict(shots=64*len(rows),batches=len(rows),toffoli=sum(r['toffoli']for r in rows.values()))
 for k in['value','phase','dirty']:out[k+'_shots']=sum(r[k+'_shots']for r in rows.values())
 out['failed_batches']=sum(bool(r['failures'])for r in rows.values());out['failed_shots']=sum(len(r['failures'])for r in rows.values());out['mean_toffoli']=out['toffoli']/out['shots'];out['lambda_failed_batches_per9024']=out['failed_batches']/len(rows)*141;return out
fail=lambda r:{f['lane']:f for f in r['failures']}
changes=[];newly_good=newly_bad=unchanged_bad=0;deltas=[];value_good=[];value_bad=[];phase_good=[];phase_bad=[];batch_good=batch_bad=0
for batch in range(4096):
 x,y=fail(a[batch]),fail(b[batch]);deltas.append((b[batch]['toffoli']-a[batch]['toffoli'])/64);batch_good+=bool(x)and not y;batch_bad+=bool(y)and not x
 assert a[batch]['toffoli']==b[batch]['toffoli'],('Toffoli count changed',batch)
 for lane in x.keys()|y.keys():
  for field in ['value','dirty']:
   assert bool(x.get(lane,{}).get(field,False))==bool(y.get(lane,{}).get(field,False)),('quantum value/garbage changed',batch,lane,field)
 for lane in sorted(x.keys()|y.keys()):
  if lane in x and lane in y:
   assert x[lane]['k1']==y[lane]['k1']and x[lane]['k2']==y[lane]['k2'];unchanged_bad+=1
  elif lane in x:newly_good+=1
  else:newly_bad+=1
  if x.get(lane)!=y.get(lane):changes.append(dict(batch=batch,lane=lane,parent=x.get(lane),candidate=y.get(lane)))
  xv=x.get(lane,{}).get('value',0);yv=y.get(lane,{}).get('value',0)
  if xv and not yv:value_good.append(dict(batch=batch,lane=lane,parent=x.get(lane),candidate=y.get(lane)))
  if yv and not xv:value_bad.append(dict(batch=batch,lane=lane,parent=x.get(lane),candidate=y.get(lane)))
  xp=x.get(lane,{}).get('phase',0);yp=y.get(lane,{}).get('phase',0)
  if xp and not yp:phase_good.append(dict(batch=batch,lane=lane,parent=x.get(lane),candidate=y.get(lane)))
  if yp and not xp:phase_bad.append(dict(batch=batch,lane=lane,parent=x.get(lane),candidate=y.get(lane)))
avg=sum(deltas)/len(deltas);sd=math.sqrt(sum((v-avg)**2 for v in deltas)/(len(deltas)-1));se=sd/math.sqrt(len(deltas));pa=summary(a);pb=summary(b)
result=dict(parent=pa,candidate=pb,newly_good=newly_good,newly_bad=newly_bad,unchanged_bad=unchanged_bad,newly_passing_batches=batch_good,newly_failing_batches=batch_bad,value_repairs=value_good,value_regressions=value_bad,phase_repairs=phase_good,phase_regressions=phase_bad,paired_mean_toffoli_delta=avg,paired_toffoli_delta_se=se,changes=changes,domain='ecdsa-research-failure-census-v1',label=(p/'input-label.txt').read_text().strip(),source_stream_sha256=hashlib.sha256((root/'candidate/ops.bin').read_bytes()).hexdigest(),strict_paired_failure_gate_passed=pb['failed_batches']<=pa['failed_batches']and pb['lambda_failed_batches_per9024']<=18,nonce_search=False,official_packet=False,resource_score=False,eligibility='zero T/Q/MR precision repair; no resource record alone. Any exact-cache composite requires fresh leases, native source binding and its own fixed fresh census before search.')
(root/'paired-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['changes','value_repairs','value_regressions','phase_repairs','phase_regressions']},indent=2));print('VALUE_REPAIRS',len(value_good),'VALUE_REGRESSIONS',len(value_bad),'PHASE_REPAIRS',len(phase_good),'PHASE_REGRESSIONS',len(phase_bad))
