exec((__import__('pathlib').Path(__file__).parent/'bind-carry-helpers.py').read_text().split('raw=load(')[0])
import collections
raw=load(root/'raw-builder.bin');final=load(root.parent/'product-exact-20261015/tip/ops.bin');helpers=[];carry=[];components=[]
for l in(out/'observer-complete-helpers.log').read_text().splitlines():
 if l.startswith('FULL_HELPER\t'):
  _,name,a,b=l.split('\t');helpers.append(dict(family=name,raw_begin=int(a),raw_end=int(b)))
 if l.startswith('COMPONENT_END '):components.append(l)
 if l.startswith('CARRY_RECS_BEGIN '):
  m=re.match(r'CARRY_RECS_BEGIN at=(\d+) tick=Some\(\((true|false), (\d+)\)\)',l)
  if m:carry.append((int(m[1]),m[2]=='true',int(m[3])))
seeds=[5497375,11099526,11114093,11128660,11243558,11255695]
containing={s:[r for r in helpers if r['raw_begin']<=s<r['raw_end']]for s in seeds}
families={r['family']for rr in containing.values()for r in rr if 16<=r['raw_end']-r['raw_begin']<=100000}
rows=[dict(r,admitted=False)for r in helpers if r['family']in families and 16<=r['raw_end']-r['raw_begin']<=100000]
for start,rev,tick in carry:
 lows=[r for r in helpers if r['family']=='y15_onefold.rs::fold_undo_low_c'and r['raw_begin']>=start]
 if lows:
  low=min(lows,key=lambda r:r['raw_begin'])
  rows.append(dict(family='carry-recs-through-low-END',raw_begin=start,raw_end=low['raw_end'],reverse=rev,tick=tick,admitted=False))
lib=ctypes.CDLL(str(root/'anchor_scan.so'));lib.anchor_find56_many.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.POINTER(ctypes.c_uint64),ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(ctypes.c_uint64),ctypes.c_size_t];lib.anchor_find56_many.restype=ctypes.c_int
def scan(anchors,width):
 cap=512;n=len(anchors);first=(ctypes.c_uint64*n)();counts=(ctypes.c_uint32*n)();hits=(ctypes.c_uint64*(n*cap))();assert lib.anchor_find56_many(final,len(final)//56,b''.join(anchors),n,width,first,counts,hits,cap)==0
 return [list(hits[i*cap:i*cap+counts[i]])if counts[i]<=cap else None for i in range(n)]
for width in[16,8,4]:
 chosen=[r for r in rows if not r['admitted']and r['raw_end']-r['raw_begin']>=2*width]
 if not chosen:continue
 starts=scan([raw[r['raw_begin']*56:(r['raw_begin']+width)*56]for r in chosen],width);tails=scan([raw[(r['raw_end']-width)*56:r['raw_end']*56]for r in chosen],width)
 for r,aa,bb in zip(chosen,starts,tails):
  if aa is None or bb is None:continue
  n=r['raw_end']-r['raw_begin'];tol=max(256,n//2);pairs=[(a,b+width)for a in aa for b in bb if a<=b and abs(b+width-a-n)<=tol]
  if len(pairs)!=1:continue
  a,b=pairs[0];depth=0;balanced=True
  for i in range(a,b):
   k=struct.unpack_from('<Q',final,i*56)[0]
   if k==15:depth+=1
   if k==16:depth-=1
   if depth<0:balanced=False;break
  if not balanced or depth:continue
  r.update(admitted=True,final_begin=a,final_end=b,anchor_width=width,final_sha256=hashlib.sha256(final[a*56:b*56]).hexdigest())
 print('BOUND_FULL',width,sum(r['admitted']for r in rows),len(rows),flush=True)
result=dict(containing=containing,components=components,families=sorted(families),rows=rows,status='DIAGNOSTIC_CANDIDATES; independent universal actual-final proof required')
(out/'complete-helper-spans.json').write_text(json.dumps(result,indent=2)+'\n')
(out/'complete-helper-proof-spans.tsv').write_text(''.join(f"{r['final_begin']}\t{r['final_end']}\t{r.get('tick',0)}\t{int(r.get('reverse',False))}\n"for r in rows if r['admitted']))
for seed,rr in containing.items():print('CONTAINING',seed,rr)
print('FAMILIES',collections.Counter(r['family']for r in rows if r['admitted']));print('CARRY126',[r for r in rows if r.get('tick')==126])
