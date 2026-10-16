from pathlib import Path
import json
r=Path(__file__).parent
p=json.loads((r/'original-candidates.json').read_text())
assert p['mapped_shadow']==p['hints']==6 and p['unmapped']==0
hints=[dict(kind='shadow',tick=x['hint']['tick'],old_start=x['mapping']['start'],old_end_exclusive=x['mapping']['end_exclusive'])for x in p['rows']]
(r/'original-final-hints.json').write_text(json.dumps(dict(status='ACTUAL_ORIGINAL_ENDPOINT_CANDIDATES_REQUIRE_PROOF',hints=hints),indent=2)+'\n')
