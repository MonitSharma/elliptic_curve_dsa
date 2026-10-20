import json
from pathlib import Path
r=Path(__file__).resolve().parent;exp=r.parent;case=json.loads((exp/'breakthrough-prefix-xag-resynth-20261020/WINDOWS.json').read_bytes())['cases'][4];assert case['start']==9 and case['end']==16 and case['original_ANDs']==7 and case['required_nonlinear_rank']==5;k=7;shift=15+case['start'];required=[x>>shift for x in case['output_forms']]
def independent(vs):
 basis={};out=[]
 for original in vs:
  x=original
  while x:
   p=x.bit_length()-1
   if p not in basis:basis[p]=x;out.append(original);break
   x^=basis[p]
 return out
dual=[a for a in range(1,1<<k)if all((a&v).bit_count()%2==0 for v in required)];assert len(dual)==3;cases=[]
for parity in dual:
 allowed=sorted([x for x in range(1,1<<k)if(a:=x&parity).bit_count()%2==0],key=lambda x:(x.bit_count(),x));basis=independent(required+allowed);assert len(basis)==6;new=dict(case,original_required_nonlinear_rank=5,required_nonlinear_rank=6,new_gate_budget=6,output_forms=[x<<shift for x in basis],hyperplane_parity=parity,retained_auxiliary_dimensions=1);cases.append(new)
(r/'AUX-CASES.json').write_text(json.dumps({'status':'FIXED_RETAINED_AUXILIARY_MODEL_CASES','cases':cases,'scope':'All3 six-dimensional subspaces of the original7 new-AND function span containing the5 required forms. Seek6 ANDs for each complete retained interface. No packet inputs.'},indent=2)+'\n')
s=(exp/'breakthrough-prefix-factor-chain-20261020/search.py').read_text();s=s.replace("case['original_ANDs']==5 and case['new_gate_budget']==case['required_nonlinear_rank']==4","case['original_ANDs']==7 and case['new_gate_budget']==case['required_nonlinear_rank']==6").replace('time.time()-started<900','time.time()-started<120 and len(seen)<128').replace('time.time()-started>=900','time.time()-started>=120').replace('EXACT_FOUR_AND_CHAIN_ALL16384_VERIFIED_NOT_NATIVE','EXACT_SIX_AND_CHAIN_ALL16384_VERIFIED_NOT_NATIVE').replace('TIME_LIMIT_INCOMPLETE','RESOURCE_LIMIT_INCOMPLETE').replace('At4 target-function rank and4 AND budget','At6 retained-function rank and6 AND budget');(r/'search-template.py').write_bytes(s.encode());print(dual)
