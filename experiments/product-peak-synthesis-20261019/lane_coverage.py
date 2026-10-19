import json,heapq
from pathlib import Path
r=Path(__file__).resolve().parent
d=json.loads((r/'telemetry-recolor.json').read_text())
sites=sorted(json.loads((r/'parent-borrow.json').read_text())['sites'],key=lambda s:s['start'])
active=[];cursor=0;cover=[];options=[];selected=[]
# Uniform-cost interval cover on the actual live peaks, allowing the lowest
# donor IDs too. Counts are a diagnostic lower bound on a concrete rewrite.
for lo,hi in d['full_width_regions']:
    while cursor<len(sites) and sites[cursor]['start']+2<=lo:
        heapq.heappush(active,(-sites[cursor]['end'],cursor));cursor+=1
    if active and -active[0][0]>=hi:
        which=active[0][1];cover.append((lo,hi));
        if which not in options:options.append(which)
    else:cover.append(None)
result={k:d[k] for k in ('recolored_physical_Q','arithmetic_live_peak','proved_zero_releases','registered_releases','final_zero_output_allocations','final_output_swaps')}
result.update({'full_width_intervals':len(d['full_width_regions']),
    'intervals_with_borrow_options':sum(x is not None for x in cover),
    'uncovered_intervals':sum(x is None for x in cover),'farthest_end_cover_cells':len(options),
    'first_twenty_full_regions':d['full_width_regions'][:20],
    'source':'telemetry-recolor.json','status':'ACTUAL_LANE_COVERAGE_DIAGNOSTIC_NOT_A_SCORE'})
(r/'LANE-COVERAGE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
