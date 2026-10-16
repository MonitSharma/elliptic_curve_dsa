exec((__import__('pathlib').Path(__file__).parent/'map-residual-sites.py').read_text().split('raw=load(')[0])
import hashlib
raw=load(root/'raw-builder.bin');final=load(root.parent/'product-exact-20261015/tip/ops.bin');lib=ctypes.CDLL(str(root/'anchor_scan.so'));lib.anchor_find56.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.POINTER(ctypes.c_uint64),ctypes.POINTER(ctypes.c_uint32)];lib.anchor_find56.restype=ctypes.c_int
targets=[5498416,11466851,11481418,11495985,11610904,11623042]
positions=[(t,t+d)for t in targets for d in range(-2048,2049,32)];n=len(positions);anchors=b''.join(final[a*56:(a+16)*56]for t,a in positions);first=(ctypes.c_uint64*n)();counts=(ctypes.c_uint32*n)();assert lib.anchor_find56(raw,len(raw)//56,anchors,n,16,first,counts)==0
fragments=[];comparators=[]
for l in(root/'observer.log').read_text().splitlines():
 if l.startswith('DIRTY_FRAGMENT\t'):
  f=l.split('\t');fragments.append(dict(kind=f[1],width=int(f[2]),begin=int(f[3]),end=int(f[4]),tail=f[5:]))
 if l.startswith('C35_SITE\t'):comparators.append(l)
folds=[l.strip().split('\t')for l in(root/'fold-marks.tsv').read_text().splitlines()]
rows=[]
for t in targets:
 matches=[dict(final=a,raw=int(first[i]),delta=a-t)for i,(tt,a)in enumerate(positions)if tt==t and counts[i]==1]
 near=sorted(matches,key=lambda x:abs(x['delta']))[:8]
 lo=max((r for r in matches if r['final']<=t),key=lambda x:x['final'],default=None);hi=min((r for r in matches if r['final']>=t),key=lambda x:x['final'],default=None)
 pos=(lo or hi or{}).get('raw',0)
 rows.append(dict(target=t,anchors=near,nearest_before=lo,nearest_after=hi,raw_near_fragments=[r for r in fragments if r['begin']-3000<=pos<=r['end']+3000],raw_near_folds=[r[:5]for r in folds if abs(int(r[0])-pos)<50000]))
(out/'context-anchors.json').write_text(json.dumps(rows,indent=2)+'\n')
for r in rows:print(json.dumps(r))
