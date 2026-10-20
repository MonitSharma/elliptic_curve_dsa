"""Rank-admissible exact Boolean resynthesis windows in the active31-AND DAG."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;dpath=r.parent/'breakthrough-prefix-dag-20261020/PREFIX-DAG.json';d=json.loads(dpath.read_bytes());desired=[1]+d['low_sum_masks']+[1<<(i+1)for i in range(6,14)]+d['field_masks']+[d['c6_mask']]
def independent(vs):
 basis={};out=[]
 for original in vs:
  v=original
  while v:
   bit=v.bit_length()-1
   if bit not in basis:basis[bit]=v;out.append(original);break
   v^=basis[bit]
 return out
cases=[]
for end in range(1,32):
 required=desired.copy()
 for _,a,b in d['gates'][end:]:required.extend([a,b])
 for width in range(2,min(end,10)+1):
  start=end-width;window=((1<<width)-1)<<(15+start);forms=independent([x&window for x in required]);deficit=width-len(forms)
  if deficit<=0:continue
  boundary=0
  for _,a,b in d['gates'][start:end]:boundary|=(a|b)&((1<<(15+start))-1)
  boundary_columns=[i for i in range(15+start)if boundary>>i&1]
  cases.append({'start':start,'end':end,'original_ANDs':width,'required_nonlinear_rank':len(forms),'rank_slack':deficit,'new_gate_budget':width-1,'output_forms':forms,'boundary_columns':boundary_columns,'boundary_width':len(boundary_columns)})
cases.sort(key=lambda x:(x['original_ANDs'],x['boundary_width'],-x['rank_slack'],x['start']))
(r/'WINDOWS.json').write_text(json.dumps({'status':'RANK_ADMISSIBLE_WINDOWS_NOT_SYNTHESIS_RESULTS','dag_sha256':hashlib.sha256(dpath.read_bytes()).hexdigest(),'cases':cases,'scope':'Conservative structural screen only. A lower projected required rank permits but does not prove a lower AND count. Any synthesized replacement must verify all16384 inputs and then native phases/cleanup before integration.'},indent=2)+'\n');print(json.dumps(cases[:12],indent=2));print('windows',len(cases))
