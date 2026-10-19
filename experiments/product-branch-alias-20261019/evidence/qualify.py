import json
from pathlib import Path
r=Path(__file__).resolve().parent
old=json.loads((r.parent/'product-support-tight-20261019/original-tight.json').read_text());new=json.loads((r/'probe.json').read_text())
assert all(new[k]==v for k,v in old.items()),[k for k,v in old.items() if new[k]!=v]
assert new['input_full_sha3_256']=='429af1c31b54064e17e7602be516b519c066c241e218d56f002287ea02b16842'
print(json.dumps({'status':'ALIAS_PROBE_OUTPUT_AND_ALL_EXISTING_FIELDS_IDENTICAL','output_full_sha3_256':new['output_full_sha3_256'],'probe':new['branch_alias_probe']},indent=2))
