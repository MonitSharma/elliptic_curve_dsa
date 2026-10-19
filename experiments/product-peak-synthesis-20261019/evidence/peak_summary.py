import json,heapq
from pathlib import Path
r=Path(__file__).resolve().parent
out={}
for prefix in ('parent','residual'):
    p=json.loads((r/f'{prefix}-peaks.json').read_text())
    regions=p['peak_regions']
    out[prefix]={'peak':p['peak_simultaneous_lifetimes'],'peak_intervals':len(regions),
        'operations_at_peak':sum(b-a+1 for a,b in regions),'first_twenty':regions[:20]}
if (r/'parent-borrow.json').exists():
    b=json.loads((r/'parent-borrow.json').read_text())
    p=json.loads((r/'parent-peaks.json').read_text())
    cover=[]; sites=sorted(b['sites'],key=lambda s:s['start']); active=[]; cursor=0
    for lo,hi in p['peak_regions']:
        while cursor<len(sites) and sites[cursor]['start']+2<=lo:
            heapq.heappush(active,sites[cursor]['end']);cursor+=1
        while active and active[0]<hi:heapq.heappop(active)
        cover.append({'range':[lo,hi],'borrow_options':len(active)})
    out['borrow_coverage']={'covered':sum(bool(x['borrow_options']) for x in cover),
        'total':len(cover),'uncovered_first_twenty':[x for x in cover if not x['borrow_options']][:20]}
(r/'PEAK-SUMMARY.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
