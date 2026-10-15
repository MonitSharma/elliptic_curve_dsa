"""Exact integer explanation of observed tick120; no circuit-score claim."""
from pathlib import Path
import json
root=Path(__file__).resolve().parent;p=2**256-2**32-977;f=2**256-p
parent=json.loads((root/'observer-analysis.json').read_text());wider=json.loads((root/'fold-analysis.json').read_text())
a=parent['first_tick_divergence'];b=wider['first_tick_divergence'];assert a['tick']==b['tick']==120
t=int(a['before_target'],16);s=int(a['source'],16);assert(t,s)==(229,p+217)
# Coefficient -5 corresponds to signs (+,-,-); complement weight Nm=2+4=6.
nm=6;x=t+s+2*((2**256-1)^s)+4*((2**256-1)^s);e=x>>256;low=x%(2**256)
assert e==1 and low==5*f-862
# m=0 yields exactly the signed representative that matches both observations.
folded=low+e+(e-nm)*(f-1);assert folded==-856
expected=(folded*pow(8,-1,p))%p;assert expected==p-107
checks=[]
for width,data in [(56,a),(57,b)]:
 wrapped=folded%(1<<width);predicted=wrapped//8;assert wrapped%8==0;assert predicted==int(data['actual_target'],16)
 delta=(predicted-expected)%p;assert delta==1<<(width-3)
 checks.append({'fold_width':width,'wrapped_fold':hex(wrapped),'observed_after_div8':data['actual_target'],'predicted_after_div8':hex(predicted),'delta_mod_p':hex(delta)})
result={'status':'exact explanation consistent with both observed streams; fold internals not directly observed','score':None,'input_target':t,'input_source':hex(s),'source_residue':s%p,'complement_weight':nm,'full_unsigned_sum':hex(x),'top_overflow':e,'signed_fold_m0':folded,'correct_after_div8':hex(expected),'checks':checks,'conclusion':'Increasing a truncated window preserves this negative-result wrap and increases its error. The full-width correction or representation invariant must handle the borrow.','limitations':['m=0 and the fold equation reproduce both results; internal quotient and borrow wires still require direct observation.','One production tick/input only.','No quantum implementation or general phase/correctness proof.']}
(root/'fold-counterexample.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
