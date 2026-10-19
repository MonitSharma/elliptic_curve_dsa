import json
from pathlib import Path
r=Path(__file__).resolve().parent
old=json.loads((r.parent/'product-support-tight-20261019/original-tight.json').read_text())
new=json.loads((r/'annotations.json').read_text())
assert all(new[k]==v for k,v in old.items()),[k for k,v in old.items() if new[k]!=v]
print(json.dumps({'status':'STRONG_ANNOTATION_OUTPUT_AND_ALL_EXISTING_FIELDS_IDENTICAL',
                 'output_full_sha3_256':new['output_full_sha3_256'],
                 'clean_event_file_sha3_256':new['clean_event_file_sha3_256'],
                 'conditional_clean_releases':new['conditional_clean_releases']},indent=2))
