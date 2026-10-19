import json
from pathlib import Path
root=Path(__file__).resolve().parent
rows=[]
for cut in (1233,1232,1230,1220,1200):
    s=json.loads((root/f'borrow-{cut}.json').read_text())
    w=json.loads((root/f'width-{cut}.json').read_text())
    q=w['peak_simultaneous_lifetimes']; extra=s['added_unconditional_Toffolis']
    rows.append(dict(cut=cut,converted=s['replaced_carries'],conservative_Q=q,
        added_T=extra,budgeted_product=q*(761096+extra),
        product_delta=q*(761096+extra)-939192464,
        status='DIAGNOSTIC_NOT_A_SCORED_RESULT'))
(root/'RESULT.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
