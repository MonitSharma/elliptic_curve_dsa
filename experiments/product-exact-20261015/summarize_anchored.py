import json,re
from pathlib import Path
root=Path(__file__).resolve().parent
records={};anchors={};left_failures={}
for folder in ['anchored-replay-20261016','anchored-new-20261016','product-continuation-20261016']:
    source=root/folder
    if not source.exists():continue
    for path in sorted(source.glob('*.log')):
        text=path.read_text(errors='replace')
        lines=[line for line in text.splitlines() if line.startswith('DIAGNOSTIC_ONLY ')]
        if not lines:continue
        assert len(lines)==1
        family='independent' if path.stem.endswith('-independent') else 'structured'
        track='product' if path.stem.startswith(('product','stage-')) else 'wide'
        row=dict(re.findall(r'(\w+)=(\S+)',lines[0]));assert row['unequal_batches']=='0'
        original_failures=tuple(row[key] for key in ['left_bad','left_phase_batches','left_dirty_batches'])
        key=(track,family)
        if key in left_failures:assert left_failures[key]==original_failures
        else:left_failures[key]=original_failures
        for line in text.splitlines():
            if not line.startswith('ANCHORED_ORIGINAL_MR '):continue
            match=re.fullmatch(r'ANCHORED_ORIGINAL_MR batch=(\d+) events=(\d+) first=(.*)',line);assert match
            batch,events,first=match.groups();key=(track,batch);value=(events,first)
            if key in anchors:assert anchors[key]==value
            else:anchors[key]=value
        records[str(path.relative_to(root))]=row
summary={'protocol':'Original MR words filled by immutable source-event ordinal; added cache MR words use a disjoint fixed XOF. Original anchor-header sanity checks and left failure outcomes agree across variants. Counts describe these fixed packets, not universal means or scored benchmarks.','score':None,'packets':records,'anchor_headers_checked':len(anchors)}
(root/'anchored-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
