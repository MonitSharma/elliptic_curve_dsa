from pathlib import Path
import json
r=Path(__file__).parent;p=json.loads((r/'original-candidates.json').read_text())
chosen={}
for row in p['rows']:
 m=row['mapping']
 if m and m['start']<=5570715<m['end_exclusive'] and m['end_exclusive']-m['start']<=100000:
  chosen[(m['start'],m['end_exclusive'])]=row
h=[dict(kind='shadow',old_start=a,old_end_exclusive=b,raw_hint=x['hint'])for(a,b),x in sorted(chosen.items())]
(r/'original-containing-hints.json').write_text(json.dumps(dict(status='UNIQUE_LITERAL_ANCHORS_CANDIDATES_ONLY',hints=h),indent=2)+'\n');print('containing',len(h))
