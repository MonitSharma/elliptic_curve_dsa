import json
from pathlib import Path
r=Path(__file__).resolve().parent
rows=[]
for cut in (1232,1230,1220):
    b=json.loads((r/f'borrow-{cut}.json').read_text())
    m=json.loads((r/f'combined-{cut}.json').read_text())
    w=json.loads((r/f'combined-width-{cut}.json').read_text())
    q=w['peak_simultaneous_lifetimes']
    extra=b['added_unconditional_Toffolis']+m['predicted_additional_toffoli']
    rows.append(dict(cut=cut,converted_carries=b['replaced_carries'],
        recomputed_caches=len(m['unwrappings']),conservative_Q=q,added_T=extra,
        budgeted_product=q*(761096+extra),product_delta=q*(761096+extra)-939192464,
        status='COMBINED_DIAGNOSTIC_NOT_A_SCORED_RESULT'))
(r/'COMBINED-RESULT.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
