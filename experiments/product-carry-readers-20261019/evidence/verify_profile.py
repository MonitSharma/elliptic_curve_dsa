import json,hashlib
from pathlib import Path
r=Path(__file__).resolve().parent
old=json.loads((r.parent/'product-support-tight-20261019/original-tight.json').read_text())
new=json.loads((r/'profile.json').read_text())
assert new['input_full_sha3_256']=='429af1c31b54064e17e7602be516b519c066c241e218d56f002287ea02b16842'
assert all(new[k]==v for k,v in old.items()), [k for k,v in old.items() if new[k]!=v]
print(json.dumps({'status':'INSTRUMENTATION_OUTPUT_AND_ALL_EXISTING_FIELDS_IDENTICAL',
                 'source_sha256':hashlib.sha256((r/'peak_profile.rs').read_bytes()).hexdigest(),
                 'output_full_sha3_256':new['output_full_sha3_256'],
                 'full_width_regions':len(new['full_width_regions']),
                 'entry_eligible':sum(new['carry_entry_all_operands_unknown_and_target_zero'])},indent=2))
