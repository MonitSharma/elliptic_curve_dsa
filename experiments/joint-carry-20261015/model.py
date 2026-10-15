"""Finite Y21 cleanup model without fold, rails or quantum implementation."""
from pathlib import Path
import json
rows=[]
for n in range(4,9):
 k=n//2;lo=n-k;i0=lo-1;mask=(1<<n)-1
 counts={'cases':0,'joint_wrong':0,'reconstructed_h1_wrong':0,'reconstructed_window_wrong':0,'comparison_wrong_with_exact_chain':0,'exact_boundary_wrong':0};example=None
 for a in range(1<<n):
  for b in range(1<<n):
   for s0 in (b,b^mask):
    for s1 in (b,b^mask):
     x0=(a+s0)&mask;g0=(a+s0)>>n;x1=(x0+2*s1)&mask;h1=(x0+((2*s1)&mask))>>n
     r=[(s1>>(i0-1))&1]
     for i in range(i0,n-1):
      si=(s1>>i)&1;ci=r[-1];r.append(ci^((si^ci)&(((x1>>(i+1))&1)^si)))
     window=0
     for j in range(lo,n):window|=(((x1>>j)^(s1>>(j-1))^r[j-1-i0])&1)<<(j-lo)
     source=s0>>lo;seed=(s0>>(lo-1))&1
     cmp=int(window<source+seed);exact_window=x0>>lo
     full_seed=int((x0&((1<<lo)-1))<(s0&((1<<lo)-1)))
     exact_pred=int(exact_window<source+full_seed)
     lowmask=(1<<(i0+1))-1
     true_chain=[((x0&lowmask)+((2*s1)&lowmask))>>(i0+1)]
     for i in range(i0,n-1):
      si=(s1>>i)&1;ci=true_chain[-1];true_chain.append(ci^((si^ci)&(((x1>>(i+1))&1)^si)))
     exact_rebuilt=sum((((x1>>j)^(s1>>(j-1))^true_chain[j-1-i0])&1)<<(j-lo) for j in range(lo,n))
     assert exact_rebuilt==exact_window and true_chain[-1]==h1
     assert (true_chain[-1]^exact_pred)==(g0^h1)
     counts['cases']+=1;counts['joint_wrong']+=int((r[-1]^cmp)!=(g0^h1));counts['reconstructed_h1_wrong']+=r[-1]!=h1;counts['reconstructed_window_wrong']+=window!=exact_window
     counts['comparison_wrong_with_exact_chain']+=int(exact_window<source+seed)!=g0;counts['exact_boundary_wrong']+=exact_pred!=g0
     if example is None and (r[-1]^cmp)!=(g0^h1):example={'a':a,'s0':s0,'s1':s1,'x0':x0,'x1':x1,'g0':g0,'h1':h1,'rebuilt_h1':r[-1],'window':window,'exact_window':exact_window,'seed':seed,'cmp':cmp}
 assert counts['exact_boundary_wrong']==0
 rows.append({'bits':n,'window':k,**counts,'first_counterexample':example})
result={'status':'finite arithmetic model only','score':None,'rows':rows,'limitations':['No fold or rail effects.','No quantum phase proof or measured gate cost.','Inputs exhaust n-bit a,b and independent complement choices, not production reachable-state distributions.','Exact comparison uses the true lower-word borrow; retaining or computing it has not been implemented.']}
(Path(__file__).resolve().parent/'model.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
