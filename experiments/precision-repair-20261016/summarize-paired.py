from pathlib import Path
import json,math,hashlib
root=Path('/home/hclau/ecdsa_research/precision-repair-20261016');p=root/'fresh-paired'
def load(name):
 rows=[json.loads(l)for l in(p/(name+'.jsonl')).read_text().splitlines()];assert len(rows)==4096 and {r['batch']for r in rows}==set(range(4096));return {r['batch']:r for r in rows}
a,b=load('parent'),load('candidate')
def summary(rows):
 out={'shots':64*len(rows),'batches':len(rows),'toffoli':sum(r['toffoli']for r in rows.values())}
 for k in ['value','phase','dirty']:out[k+'_shots']=sum(r[k+'_shots']for r in rows.values())
 out['failed_batches']=sum(bool(r['failures'])for r in rows.values());out['failed_shots']=sum(len(r['failures'])for r in rows.values());out['mean_toffoli']=out['toffoli']/out['shots'];out['lambda_failed_batches_per9024']=out['failed_batches']/len(rows)*141;return out
fail=lambda r:{f['lane']:f for f in r['failures']}
changes=[];newly_good=newly_bad=unchanged_bad=0;deltas=[]
for batch in range(4096):
 x,y=fail(a[batch]),fail(b[batch]);deltas.append((b[batch]['toffoli']-a[batch]['toffoli'])/64)
 for lane in sorted(x.keys()|y.keys()):
  if lane in x and lane in y:
   assert x[lane]['k1']==y[lane]['k1']and x[lane]['k2']==y[lane]['k2'];unchanged_bad+=1
  elif lane in x:newly_good+=1
  else:newly_bad+=1
  if x.get(lane)!=y.get(lane):changes.append(dict(batch=batch,lane=lane,parent=x.get(lane),candidate=y.get(lane)))
avg=sum(deltas)/len(deltas);sd=math.sqrt(sum((v-avg)**2 for v in deltas)/(len(deltas)-1));se=sd/math.sqrt(len(deltas))
result=dict(parent=summary(a),candidate=summary(b),newly_good=newly_good,newly_bad=newly_bad,unchanged_bad=unchanged_bad,paired_mean_toffoli_delta=avg,paired_toffoli_delta_se=se,changes=changes,domain='ecdsa-research-failure-census-v1',label='public4b-precision-top1-posttable-fresh-20261016-v1',source_stream_sha256=hashlib.sha256((root/'posttable-v3-ops.bin').read_bytes()).hexdigest(),final_source_stream_sha256=hashlib.sha256((root/'candidate-posttable-top1/ops.bin').read_bytes()).hexdigest(),official_packet=False,nonce_search=False,resource_score=False)
assert result['source_stream_sha256']==result['final_source_stream_sha256']
(root/'paired-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
