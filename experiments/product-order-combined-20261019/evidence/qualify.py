import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
old=read(r.parent/'product-order-20261019/reordered.json');new=read(r/'fast-full.json')
assert new['output_full_sha3_256']==old['output_sha3_256']
assert new['permutation_sha3_256']==old['permutation_sha3_256']
old_g=read(r.parent/'product-guard-lifetimes-20261019/guard-colored.json');new_g=read(r/'annotations.json')
for key in ('output_full_sha3_256','release_event_sha3_256','recolored_Q','conditional_clean_releases','bool_nodes','support_cuts'):
    assert new_g[key]==old_g[key],key
receipt={'status':'COMPACT_SCHEDULER_AND_ANNOTATION_ONLY_ALLOCATOR_BYTE_IDENTITY_PASS',
    'scheduler_output_sha3_256':new['output_full_sha3_256'],'scheduler_permutation_sha3_256':new['permutation_sha3_256'],
    'allocator_output_sha3_256':new_g['output_full_sha3_256'],'allocator_release_event_sha3_256':new_g['release_event_sha3_256'],
    'annotated_clean_file_sha3_256':new_g['clean_event_file_sha3_256'],
    'sources':{p.name:hashlib.file_digest(p.open('rb'),'sha256').hexdigest() for p in [r/'order_fast.rs',r/'guard_annotated.rs',r/'legacy.rs']}}
(r/'QUALIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
