"""Summarize existing diagnostic rows; never label them scored results."""
import collections,json
from pathlib import Path
r=Path(__file__).resolve().parent
segments=[l.split('\t')[0]for l in(r/'segment-map.tsv').read_text().splitlines()]
sums=collections.Counter();rows=[json.loads(l)for l in(r/'region-census.jsonl').read_bytes().splitlines()]
assert len(rows)==512
for row in rows:
    assert len(row['regional_toffoli'])==len(segments)
    assert sum(row['regional_toffoli'])==row['toffoli']
    for name,n in zip(segments,row['regional_toffoli']):sums[name]+=n
res={'scope':'Unoptimized byte-identical raw arithmetic observation; diagnostic means, not scored results. Payload is explicit wrapper union, other contains rail plus residual endpoints/setup.',
    'batches':len(rows),'shots':len(rows)*64,'mean_executed_toffoli':{k:v/(len(rows)*64)for k,v in sums.items()},
    'total_mean':sum(x['toffoli']for x in rows)/(len(rows)*64)}
(r/'DIRECT-DOMAIN-PROFILE.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
