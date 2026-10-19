import hashlib,heapq,json
from collections import Counter
from pathlib import Path
r=Path(__file__).resolve().parent
freeze=json.loads((r/'SOURCE_FREEZE-v2.json').read_text())
assert hashlib.sha256((r/'observer/ops.bin').read_bytes()).hexdigest()==freeze['expected_native_raw_sha256']
phases=[];regions=[];names=Counter()
for line in(r/'generate.log').read_text().splitlines():
 if line.startswith('BREAK_PHASE\t'):
  name,end,*_=line.split('\t')[1:];phases.append((name,int(end)))
 if line.startswith('BREAK_REGION\t'):
  phase,name,start,end=line.split('\t')[1:];start=int(start);end=int(end);assert start<=end
  names[name]+=1
  if start<end:regions.append((phase,name,start,end))
(r/'REGION-NAMES-v2.json').write_text(json.dumps(dict(names),indent=2)+'\n')
def category(name):
 if name.startswith('n2.'):
  if 'rails' in name:return 'rail_n2'
  if 'pay' in name:return 'payload_n2'
  return 'mixed_n2_last'
 if name.endswith('.k_erase')or name.endswith('.choice_erase'):return 'rail_history_erase'
 if name.endswith('.endpoint'):return 'endpoint'
 if name.endswith('.p1_unseed'):return 'payload_unseed' 
 if '.pay_'in name:return'payload_'+name.split('.pay_',1)[1]
 if '.rail_'in name:return'rail_'+name.split('.rail_',1)[1]
 if '.yp8_'in name or name.startswith('yp8.'):return'rail_choice_inside_add'
 if name.endswith('.choice'):return'rail_choice'
 if name.endswith('.seed')or name.endswith('.unseed'):return'rail_seed_unseed'
 if name.endswith('.p1_setup')or name.endswith('.pay_setup'):return'payload_setup'
 return None
intervals=[]
for phase,name,start,end in regions:
 cat=category(name)
 if cat:intervals.append((start,end,phase+'/'+cat))
last=0
for phase,end in phases:
 if end>last:intervals.append((last,end,phase+'/unclassified'))
 last=end
assert last==int.from_bytes((r/'observer/ops.bin').read_bytes()[8:16],'little')
intervals.sort();points=sorted({x for a,b,_ in intervals for x in(a,b)})
heap=[];cursor=0;segments=[]
for begin,end in zip(points,points[1:]):
 while cursor<len(intervals)and intervals[cursor][0]<=begin:
  a,b,cat=intervals[cursor];heapq.heappush(heap,(b-a,cat,cursor,b));cursor+=1
 while heap and heap[0][3]<=begin:heapq.heappop(heap)
 assert heap
 cat=heap[0][1]
 if segments and segments[-1][0]==cat:segments[-1]=(cat,end)
 else:segments.append((cat,end))
assert segments[-1][1]==last
(r/'segment-map-v2.tsv').write_text(''.join(f'{cat}\t{end}\t{end}\t0\n'for cat,end in segments))
(r/'SEGMENTS-v2.json').write_text(json.dumps({'status':'EXACT_BYTE_IDENTICAL_RAW_REGION_MAP','prepass_regions':len(regions),'eligible_intervals':len(intervals),'merged_segments':len(segments),'categories':sorted({cat for cat,_ in segments}),'scope':'Partition of raw arithmetic; no score or complete optimized-circuit region attribution.'},indent=2)+'\n')
print('Regions',len(regions),'segments',len(segments))
