from pathlib import Path
import json,hashlib,math
r=Path('/home/hclau/ecdsa_research/value-carry-contracts-20261016');p=r/'square-fresh'
assert(r/'square-fresh.exit').read_text().strip()=='0'
f=json.loads((r/'SQUARE4-PREDECLARATION.json').read_text());n=f['fresh_gate']['batches'];assert n==32768
def load(name):
 rows=[json.loads(x)for x in(p/f'{name}.jsonl').read_text().splitlines()];assert len(rows)==n and{row['batch']for row in rows}==set(range(n));return{row['batch']:row for row in rows}
a,b=load('parent'),load('candidate')
def summary(rows):
 out=dict(shots=64*len(rows),batches=len(rows),toffoli=sum(x['toffoli']for x in rows.values()))
 for k in['value','phase','dirty']:out[k+'_shots']=sum(x[k+'_shots']for x in rows.values())
 out['failed_batches']=sum(bool(x['failures'])for x in rows.values());out['failed_shots']=sum(len(x['failures'])for x in rows.values());out['mean_toffoli']=out['toffoli']/out['shots'];out['lambda_failed_batches_per9024']=out['failed_batches']/len(rows)*141;return out
fail=lambda x:{row['lane']:row for row in x['failures']}
changes=[];repairs={k:[]for k in['value','phase','dirty']};regressions={k:[]for k in repairs};good=bad=unchanged=batch_good=batch_bad=0;deltas=[]
for batch in range(n):
 x,y=fail(a[batch]),fail(b[batch]);delta=(b[batch]['toffoli']-a[batch]['toffoli'])/64;deltas.append(delta)
 assert delta==16,'all original classical/MR functions must be unchanged; exact16unconditional additional CCX'
 batch_good+=bool(x)and not y;batch_bad+=bool(y)and not x
 for lane in sorted(x.keys()|y.keys()):
  if lane in x and lane in y:
   assert x[lane]['k1']==y[lane]['k1']and x[lane]['k2']==y[lane]['k2'];unchanged+=1
  elif lane in x:good+=1
  else:bad+=1
  record=dict(batch=batch,lane=lane,parent=x.get(lane),candidate=y.get(lane))
  if x.get(lane)!=y.get(lane):changes.append(record)
  for kind in repairs:
   before=x.get(lane,{}).get(kind,0);after=y.get(lane,{}).get(kind,0)
   if before and not after:repairs[kind].append(record)
   if after and not before:regressions[kind].append(record)
pa,pb=summary(a),summary(b);assert pb['mean_toffoli']-pa['mean_toffoli']==16
out=dict(status='SOLE FIXED FRESH GATE TERMINAL',parent=pa,candidate=pb,newly_passing_shots=good,newly_failing_shots=bad,unchanged_failing_shots=unchanged,newly_passing_batches=batch_good,newly_failing_batches=batch_bad,
 repairs=repairs,regressions=regressions,changes=changes,paired_mean_toffoli_delta=16,paired_toffoli_delta_se=0,
 strict_paired_failure_gate_passed=pb['failed_batches']<=pa['failed_batches']and pb['lambda_failed_batches_per9024']<=18,
 label=f['fresh_gate']['label'],domain='ecdsa-research-failure-census-v1',source_stream_sha256=hashlib.sha256((r/'square4-candidate/ops.bin').read_bytes()).hexdigest(),family_predeclaration_sha256=hashlib.sha256((r/'SQUARE4-PREDECLARATION.json').read_bytes()).hexdigest(),
 Q=1234,added_T=16,added_MR=0,old_MR_draw_ordinal_coupling='identity; no added draws or classical/scope edits; common labelled input/RNG stream',
 no_resampling=True,nonce_search=False,official_packet=False,resource_score=False,old_arithmetic_mask_transferred=False,
 eligibility='Standalone costs16T and cannot improve a resource record alone; cache composition requires independent exact lease/source/interface proof and a separately frozen whole-composite gate.')
(r/'square-paired-summary.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items()if k not in['changes','repairs','regressions']},indent=2))
print('REPAIRS',{k:len(v)for k,v in repairs.items()},'REGRESSIONS',{k:len(v)for k,v in regressions.items()})
