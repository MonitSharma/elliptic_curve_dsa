exec((__import__('pathlib').Path(__file__).parent/'bind-carry-helpers.py').read_text().split('raw=load(')[0])
raw=load(root/'raw-builder.bin');final=load(root.parent/'product-exact-20261015/tip/ops.bin');old=json.loads((out/'phase-lifetime-spans.json').read_text());chosen=[]
for r in old['rows']:
 if r['family'].endswith('+choice-HMR')or r['family']in['y15_onefold.rs::close','y15_onefold.rs::close_boundary']or(r['family'].startswith('square.rs::')and r['raw_begin']<=5497375<r['raw_end']):
  if not r['admitted']:chosen.append(r)
rows=[]
for r in chosen:
 for pad in[8,16,32,64,128,256,512,1024]:
  rows.append(dict(family=r['family'],helper_raw_begin=r['raw_begin'],helper_raw_end=r['raw_end'],raw_begin=max(0,r['raw_begin']-pad),raw_end=r['raw_end']+pad,pad=pad,admitted=False))
lib=ctypes.CDLL(str(root/'anchor_scan.so'));lib.anchor_find56_many.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.POINTER(ctypes.c_uint64),ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(ctypes.c_uint64),ctypes.c_size_t];lib.anchor_find56_many.restype=ctypes.c_int
def scan(anchors,width):
 cap=1024;n=len(anchors);first=(ctypes.c_uint64*n)();counts=(ctypes.c_uint32*n)();hits=(ctypes.c_uint64*(n*cap))();assert lib.anchor_find56_many(final,len(final)//56,b''.join(anchors),n,width,first,counts,hits,cap)==0
 return [list(hits[i*cap:i*cap+counts[i]])if counts[i]<=cap else None for i in range(n)]
for width in[16,8]:
 selected=[r for r in rows if not r['admitted']]
 aa=scan([raw[r['raw_begin']*56:(r['raw_begin']+width)*56]for r in selected],width);bb=scan([raw[(r['raw_end']-width)*56:r['raw_end']*56]for r in selected],width)
 for r,starts,tails in zip(selected,aa,bb):
  if starts is None or tails is None:continue
  length=r['raw_end']-r['raw_begin'];tol=max(2048,length//2);pairs=[(a,b+width)for a in starts for b in tails if a<=b and abs(b+width-a-length)<=tol]
  if len(pairs)!=1:continue
  a,b=pairs[0];depth=0;balanced=True
  for i in range(a,b):
   k=struct.unpack_from('<Q',final,i*56)[0]
   if k==15:depth+=1
   if k==16:depth-=1
   if depth<0:balanced=False;break
  if not balanced or depth:continue
  r.update(admitted=True,final_begin=a,final_end=b,anchor_width=width,final_sha256=hashlib.sha256(final[a*56:b*56]).hexdigest())
 print('EXPANDED',width,sum(r['admitted']for r in rows),len(rows),flush=True)
accepted=[r for r in rows if r['admitted']];best={}
for r in sorted(accepted,key=lambda r:r['pad']):best.setdefault((r['family'],r['helper_raw_begin'],r['helper_raw_end']),r)
(out/'expanded-lifetime-spans.json').write_text(json.dumps(dict(rows=rows,selected=list(best.values()),status='DIAGNOSTIC_CANDIDATES, padded source context; independent actual-final universal proof mandatory'),indent=2)+'\n')
(out/'expanded-lifetime-proof-spans.tsv').write_text(''.join(f"{r['final_begin']}\t{r['final_end']}\t0\t0\n"for r in best.values()))
print('SELECTED',len(best));print('TARGETS',[r for r in best.values()if any(r['final_begin']<=t<r['final_end']for t in[5498416,11466851,11481418,11495985,11610904])])
