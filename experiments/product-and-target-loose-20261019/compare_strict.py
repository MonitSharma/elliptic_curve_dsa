import json
from pathlib import Path
r=Path(__file__).resolve().parent;s=r.parent/'product-and-target-20261019'
assert (r/'run-v2.exit').read_text().strip()=='0'
assert json.loads((r/'control.json').read_text())['status']=='PROTECTED_SIMULATOR_EVENT_SUBSEQUENCE_CONTROL_PASS'
keys=['input_full_sha3_256','output_full_sha3_256','input_count','output_count','site_count','parity_zero_products_removed','original_rng_events','remaining_rng_events']
old=json.loads((s/'absorbed.json').read_text());new=json.loads((r/'absorbed.json').read_text())
assert all(old[k]==new[k] for k in keys)
oldc=json.loads((s/'absorbed-tight.json').read_text());newc=json.loads((r/'absorbed-tight.json').read_text())
assert oldc==newc
out={'status':'GENERALIZED_SCREEN_ADMITS_NO_NEW_SITE_AND_EXACT_SAME_COMPLETE_OUTPUT',
     'matching_fields':{k:new[k] for k in keys},'colored_Q':newc['recolored_Q'],
     'colored_full_sha3_256':newc['output_full_sha3_256']}
(r/'COMPARE-STRICT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
