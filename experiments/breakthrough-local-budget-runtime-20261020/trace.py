import hashlib,json
from collections import Counter
from pathlib import Path
r=Path(__file__).resolve().parent;ad=json.loads((r/'ADMISSION-RESULT.json').read_text());assert[c['exit']for c in ad['cases']]==[0,0,0];traces={};rows=[]
for c in ad['cases']:
 cap=c['cap'];p=r/f'cap{cap}';trace=[l.split('\t')[1:]for l in(p/'generate.log').read_text().splitlines()if l.startswith('LAYOUT_AUDIT\t')];traces[cap]=trace;data=(json.dumps(trace,indent=2)+'\n').encode();(p/'replay-sites.json').write_bytes(data);rows.append({'cap':cap,'sites':len(trace),'trace_sha256':hashlib.sha256(data).hexdigest(),'raw_sha256':c['raw_sha256']})
baseline=Counter(tuple(t)for t in traces[1234]);comparisons=[]
for cap in [1233,1232]:
 counter=Counter(tuple(t)for t in traces[cap]);comparisons.append({'cap':cap,'identical_ordered_trace':traces[1234]==traces[cap],'identical_site_multiset':baseline==counter,'old_only':sum((baseline-counter).values()),'new_only':sum((counter-baseline).values())})
report={'cases':rows,'comparisons':comparisons,'scope':'Metadata covers existing replay-site calls only; identical traces do not prove completeness for every approximation. No full-stream correctness gate or scored result.'};(r/'LAYOUT-COMPARISON.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report))
