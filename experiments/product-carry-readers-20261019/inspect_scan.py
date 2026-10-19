import json,collections
from pathlib import Path
r=Path(__file__).resolve().parent
s=json.loads((r/'scan.json').read_text());cells=s['cells']
p=json.loads((r.parent/'product-peak-synthesis-20261019/parent-peaks.json').read_text())
out={k:v for k,v in s.items() if k!='cells'}
out.update(cost_histogram=dict(collections.Counter(x['worst_case_added_T'] for x in cells)),
           compact_cells=sum(x['compact'] for x in cells),
           operand_read_cells=sum(x['operand_queries']>0 for x in cells),
           longest_cells=sorted(cells,key=lambda x:x['end']-x['start'],reverse=True)[:8],
           old_reset_only_peak_region_count=len(p['peak_regions']))
(r/'scan-summary.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
