import hashlib,json
from collections import Counter
from pathlib import Path
r=Path(__file__).resolve().parent;freeze=json.loads((r/'SOURCE_FREEZE.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(r/'observer/ops.bin')==freeze['expected_native_raw_sha256']
assert all(sha(r/'observer'/p)==h for p,h in{**freeze['source_files'],**freeze['protected_files']}.items())
sites={};rows=[]
for line in(r/'generate.log').read_text().splitlines():
    if line.startswith('PARITY_SITE\t'):
        phase,kind,start,n,active,room,cin,hook,disjoint,indices=line.split('\t')[1:]
        start=int(start);key=(kind,start);assert key not in sites
        sites[key]={'phase':phase,'kind':kind,'begin':start,'width':int(n),'active':int(active),'room':int(room),
            'cin':bool(int(cin)),'pending_hook':bool(int(hook)),'source_disjoint':bool(int(disjoint)),
            'exclusive_carry_positions':list(map(int,indices.split(',')))if indices else[]}
    if line.startswith('PARITY_SITE_END\t'):
        kind,start,end=line.split('\t')[1:];key=(kind,int(start));row=sites.pop(key);row['end']=int(end);rows.append(row)
assert not sites
rows.sort(key=lambda x:x['begin'])
first_peak=1444634
result={'status':'BYTE_IDENTICAL_PARITY_PIVOT_SITE_AUDIT','raw_sha256':freeze['expected_native_raw_sha256'],
    'sites':len(rows),'kinds':dict(Counter(x['kind']for x in rows)),
    'first_peak_covering_calls':[x for x in rows if x['begin']<=first_peak<x['end']],
    'plain_sites_with_pivots_without_hooks':sum(x['kind']=='plain'and bool(x['exclusive_carry_positions'])and not x['pending_hook']for x in rows),
    'scope':'Availability only. Paused callbacks may require unchanged source values; no component integration, reduced width or resource score.'}
(r/'SITE-ROWS.json').write_text(json.dumps(rows,indent=2)+'\n')
(r/'SITE-AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
