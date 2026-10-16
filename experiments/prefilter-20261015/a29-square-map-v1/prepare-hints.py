from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
bounds=set()
for line in (r.parent/'prefilter-macro-20261016/additional/observer-complete-helpers.log').read_text().splitlines():
 p=line.split()
 if len(p)!=4 or p[0]!='FULL_HELPER' or not p[1].startswith('square.rs::'):continue
 a,b=map(int,p[2:])
 if a<5393190 or b>5775614 or p[1].endswith('row_addsub_cin'):continue
 if b-a<750:continue
 for pad in [0,8,16,64]:bounds.add((max(0,a-pad),b+pad,p[1]))
hints=[dict(kind='shadow',old_start=a,old_end_exclusive=b,source_helper=n)for a,b,n in sorted(bounds)]
(r/'a29-square-map-v1/hints.json').write_text(json.dumps(dict(status='RAW_HELPER_BOUNDARIES_ONLY_ACTUAL_GATE_PROOF_REQUIRED',hints=hints),indent=2)+'\n')
print('hints',len(hints))
