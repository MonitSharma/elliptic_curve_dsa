import json
from pathlib import Path
r=Path(__file__).resolve().parent
cases=json.loads((r/'DECLARED-CASES.json').read_text());assert len(cases)==6
rows=[]
for c in cases:
    x=json.loads((r/(c['name']+'.json')).read_text())
    assert x['input_full_sha3_256']==c['input_sha3_256'] and x['max_original_operation_gap']==c['gap']
    assert x['pair_count']==0 and x['output_full_sha3_256'] is None
    assert not (r/(c['name']+'.ops.bin')).exists()
    rows.append({'name':c['name'],'input_sha3_256':c['input_sha3_256'],'gap':c['gap'],'pair_count':0})
(r/'SIX-CASE-CONTROL.json').write_text(json.dumps({'status':'ALL_SIX_FIXED_SOURCE_QUERIES_ZERO_WITH_MATCHED_SOURCE_HASHES','rows':rows},indent=2)+'\n')
