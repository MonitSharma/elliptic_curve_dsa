"""Compare truncated carry reconstruction policies with seedless comparisons.
No fold, quantum implementation, stream selection or scored result.
"""
from pathlib import Path
import json
rows=[]
for n in range(5,9):
 k=n//2;lo=n-k;mask=(1<<n)-1
 policies={name:{'cases':0,'wrong_h1':0,'wrong_window':0,'wrong_joint_phase':0,'first_error':None} for name in ['source_seed','zero_seed','zero_seed_extra_bit']}
 for a in range(1<<n):
  for b in range(1<<n):
   for s0 in (b,b^mask):
    for s1 in (b,b^mask):
     x0=(a+s0)&mask;g0=(a+s0)>>n;x1=(x0+2*s1)&mask;h1=(x0+((2*s1)&mask))>>n
     for name,d in policies.items():
      i0=lo-1-int(name=='zero_seed_extra_bit');r=[((s1>>(i0-1))&1) if name=='source_seed' else 0]
      for i in range(i0,n-1):
       si=(s1>>i)&1;ci=r[-1];r.append(ci^((si^ci)&(((x1>>(i+1))&1)^si)))
      window=sum((((x1>>j)^(s1>>(j-1))^r[j-1-i0])&1)<<(j-lo) for j in range(lo,n))
      pred=int(window<(s0>>lo));wrong=(r[-1]^pred)!=(g0^h1)
      d['cases']+=1;d['wrong_h1']+=r[-1]!=h1;d['wrong_window']+=window!=(x0>>lo);d['wrong_joint_phase']+=wrong
      if wrong and d['first_error'] is None:d['first_error']={'target':a,'source0':s0,'source1':s1,'exact_h1':h1,'rebuilt_h1':r[-1],'g0':g0,'compare':pred}
 rows.append({'bits':n,'comparison_width':k,'policies':policies})
result={'status':'finite arithmetic model only','score':None,'rows':rows,'limitations':['No fold or rail effects.','Seedless comparison itself remains truncated.','No quantum phase proof or measured resource cost.','Counts concern these exhaustive small domains, not production failure rates.']}
(Path(__file__).resolve().parent/'chain-model.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'rows':[{**{k:r[k] for k in ['bits','comparison_width']},'counts':{p:{k:d[k] for k in ['cases','wrong_h1','wrong_joint_phase']} for p,d in r['policies'].items()}} for r in rows]},indent=2))
