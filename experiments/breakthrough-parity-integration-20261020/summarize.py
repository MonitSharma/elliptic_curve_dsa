import hashlib,json,re
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE_FREEZE.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(r/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
log=(r/'generate.log').read_text();uses=[]
for line in log.splitlines():
    if line.startswith('PARITY_USE\t'):
        phase,start,end,n,active,borrowed=line.split('\t')[1:]
        uses.append({'phase':phase,'start':int(start),'end':int(end),'width':int(n),'active_before':int(active),'borrowed_carries':int(borrowed)})
assert uses
totals=[line for line in log.splitlines()if line.startswith('HEO_TOTAL ')]
peaks=[line for line in log.splitlines()if'PEAK_CENSUS'in line]
result={'status':'RAW_INTEGRATION_GENERATION_ONLY_NOT_A_RESOURCE_SCORE','uses':len(uses),'borrowed_stage_sum':sum(x['borrowed_carries']for x in uses),
    'raw_sha256':sha(r/'observer/ops.bin'),'raw_bytes':(r/'observer/ops.bin').stat().st_size,
    'builder_total_lines':totals,'peak_lines':peaks,
    'scope':'Generation/ownership evidence only. Complete replay correctness, final optimized width/Toffolis, sole final census and benchmark remain unperformed.'}
(r/'USE-ROWS.json').write_text(json.dumps(uses,indent=2)+'\n');(r/'GENERATION-RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
