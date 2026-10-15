from pathlib import Path
import json,struct,ctypes,ctypes.util,collections
r=Path('/home/hclau/ecdsa_research/phase-localization-20261016')
assert(r/'sensitivity64-wrapper.exit').read_text().strip()=='0'
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(path):
 d=path.read_bytes();n=struct.unpack_from('<Q',d,8)[0];b=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(b,len(b),d[16:],len(d)-16)==n*56;return b.raw
raw=load(r/'raw-builder.bin');final=load(r.parent/'product-exact-20261015/tip/ops.bin')
callers={};helpers=[]
for line in(r/'source-map.log').read_text().splitlines():
 f=line.split('\t')
 if f[0]=='PHASE_HMR':callers[int(f[1])]=dict(q=int(f[2]),bit=int(f[3]),file=f[4],line=int(f[5]))
 if f[0]=='FULL_HELPER':helpers.append(dict(family=f[1],start=int(f[2]),end=int(f[3])))
folds=json.loads((r.parent/'precision-repair-20261016/surviving-folds.json').read_text())['rows']
witnesses=json.loads((r/'phase-only-witnesses.json').read_text());rows=[];hist=collections.Counter()
for lane in range(64):
 f=r/f'sensitivity-{lane}-0.jsonl';assert(r/f'sensitivity-{lane}-0.exit').read_text().strip()=='0';events=[json.loads(l)for l in f.read_text().splitlines()];assert events[-1]['type']=='summary';hits=[e for e in events if e['type']=='sensitivity'];mapped=[]
 for h in hits:
  op=h['op'];matches=[];chosen_width=0
  for width in[8,32,128,512]:
   if op<width:continue
   anchor=final[(op-width)*56:(op+width+1)*56];found=[];start=0
   while True:
    pos=raw.find(anchor,start)
    if pos<0:break
    if pos%56==0:found.append(pos//56+width)
    start=pos+1
   if found:matches=found;chosen_width=width
   if len(found)==1:break
  cs=[callers[i]for i in matches if i in callers];assert len(cs)==len(matches)
  roles=sorted(set((c['file'],c['line'])for c in cs));contexts=[]
  for i in matches:
   bodies=[x for x in helpers if x['family']=='y15_onefold.rs::body'and x['start']<=i<x['end']]
   for body in bodies:
    ticks=[dict(reverse=x['reverse'],tick=x['tick'],width=x['width'])for x in folds if body['start']<=x['start']<body['end']]
    contexts.append(dict(raw_op=i,body=body,ticks=ticks))
  role=';'.join(f'{f}:{l}'for f,l in roles)or'UNMAPPED';hist[role]+=1
  mapped.append(dict(**h,raw_matches=matches,anchor_half_width=chosen_width,callers=cs,roles=roles,contexts=contexts))
 rows.append(dict(input_lane=lane,witness=witnesses[lane],summary=events[-1],hits=mapped))
summary=dict(witnesses=64,draws_scanned_each=906156,all_scans_exit0=True,phase_only_hits=sum(h['phase_change']and not h['quantum_change']for row in rows for h in row['hits']),quantum_changed_hits=sum(h['quantum_change']for row in rows for h in row['hits']),one_phase_only_hit_witnesses=sum(len(row['hits'])==1 and row['hits'][0]['phase_change']and not row['hits'][0]['quantum_change']for row in rows),role_counts=dict(hist),rows=rows,diagnostic_only=True,no_repair_selection=True)
(r/'phase-sensitivity-classification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items()if k!='rows'},indent=2))
