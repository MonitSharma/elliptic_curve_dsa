import hashlib,json,re
from pathlib import Path
root=Path(__file__).resolve().parent
stages=[('retained',128,64,0),('affine',128,64,0),('anf',512,64,0),('retained',512,64,0),('retained',128,64,0),('retained',512,64,0),('retained',1024,64,0),('anf',512,64,0),('retained',128,64,0),('retained',512,64,0),('retained',1024,64,0),('scratch',1024,64,8),('unfold',128,64,0),('affine',128,64,0),('retained',512,256,0)]
packets={}
for family in ['independent','structured']:
    text=(root/f'anchored-new-20261016/wide-{family}.log').read_text()
    line=next(line for line in text.splitlines() if line.startswith('DIAGNOSTIC_ONLY '));row=dict(re.findall(r'(\w+)=(\S+)',line));assert row['unequal_batches']=='0';packets[family]=row
frozen={'base_revision':'5a7c390233c72133df9b591c92e43422c5892142','candidate':'candidate-wide-compound','stages':[dict(family=family,atom_cap=cap,pair_cap=pairs,extra_zero_slots_offered=extra,product_cap=1000000,rank='density',split=True) for family,cap,pairs,extra in stages],'scope':'exact semantic rewrites, no input-selected tables/cuts; inherited failures retained','external_stream':'wide-compound-20261016/wide-15-retained-512.bin','external_stream_sha256':hashlib.sha256((root/'wide-compound-20261016/wide-15-retained-512.bin').read_bytes()).hexdigest(),'anchored_diagnostic_packets':packets,'diagnostic_rng_protocol':'Original MR words indexed by immutable original-event ordinal; fresh added-cache MR words use a separate fixed XOF. Not a universal exact mean.','resources':json.loads((root/'wide-compound-20261016/resources.jsonl').read_text()),'label':'wide-compound-frozen-20261016','batches_per_source':4096,'shots_per_source':262144,'nonce_search_performed':False,'score':None}
(root/'WIDE_COMPOUND_FREEZE.json').write_text(json.dumps(frozen,indent=2)+'\n')
print(json.dumps(frozen,indent=2))
