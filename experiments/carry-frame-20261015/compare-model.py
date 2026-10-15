"""Exhaustive independent-word model; not a production input-distribution claim."""
from pathlib import Path
import json
rows=[]
for n in range(2,9):
    for k in range(1,n):
        h=n-k;seeded=wide=equal_seeded=equal_wide=0
        for t in range(1<<n):
            for s in range(1<<n):
                actual=t<s
                a=(t>>h)<((s>>h)+((s>>(h-1))&1))
                b=(t>>(h-1))<(s>>(h-1))
                seeded+=a!=actual;wide+=b!=actual
                if t==s:equal_seeded+=a!=actual;equal_wide+=b!=actual
        assert seeded==1<<(2*n-k-2)
        assert wide==seeded-(1<<(n-1))
        assert equal_seeded==1<<(n-1) and equal_wide==0
        rows.append({'width':n,'old_window':k,'pairs':1<<(2*n),'seeded_errors':seeded,'widened_unseeded_errors':wide,'equal_operand_seeded_errors':equal_seeded,'equal_operand_unseeded_errors':equal_wide})
out={'score':None,'scope':'Uniform independent n-bit target and source; exact predicate target<source; source-bit predictor directly below a k-bit window. No fold, no production-distribution claim.','result':'One additional unseeded bit has fewer predicate errors in this model and fixes all equality cases. Neither truncated policy is generally exact.','seeded_error_probability':'2^(-k-2)','widened_unseeded_error_probability':'2^(-k-2)-2^(-n-1)','rows':rows,'pairs_exhausted':sum(r['pairs'] for r in rows)}
Path(__file__).with_name('compare-model.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='rows'}))
