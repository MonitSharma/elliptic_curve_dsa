exec((__import__('pathlib').Path(__file__).parent/'bind-carry-helpers.py').read_text().split('raw=load(')[0])
raw=load(root/'raw-builder.bin');final=load(root.parent/'product-exact-20261015/tip/ops.bin');rows=[]
all_helpers=[]
for l in(out/'observer-complete-helpers.log').read_text().splitlines():
 if not l.startswith('FULL_HELPER\t'):continue
 _,name,a,b=l.split('\t');a=int(a);b=int(b)
 all_helpers.append(dict(family=name,raw_begin=a,raw_end=b,admitted=False))
 if name in['y15_onefold.rs::close','y15_onefold.rs::close_boundary']:
  rows.append(dict(family=name,raw_begin=a,raw_end=b,admitted=False))
 if name=='leapfrog.rs::yp8_double_sub_forced_erase':
  rows.append(dict(family=name,raw_begin=a,raw_end=b,admitted=False))
  previous=[j for j in range(max(0,a-256),a)if struct.unpack_from('<Q',raw,j*56)[0]==12]
  if previous:rows.append(dict(family=name+'+choice-HMR',raw_begin=max(previous),raw_end=b,helper_begin=a,admitted=False))
square_families={r['family']for r in all_helpers if r['raw_begin']<=5497375<r['raw_end']and r['raw_end']-r['raw_begin']<=200000}
rows.extend(r for r in all_helpers if r['family']in square_families and r['raw_end']-r['raw_begin']>=32)
norm=ctypes.CDLL(str(root/'normalize-bitids.so'));norm.normalize_bitids56.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t]
rn=ctypes.create_string_buffer(len(raw));fn=ctypes.create_string_buffer(len(final));norm.normalize_bitids56(raw,rn,len(raw)//56);norm.normalize_bitids56(final,fn,len(final)//56)
lib=ctypes.CDLL(str(root/'anchor_scan.so'));lib.anchor_find56_many.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.POINTER(ctypes.c_uint64),ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(ctypes.c_uint64),ctypes.c_size_t];lib.anchor_find56_many.restype=ctypes.c_int
def scan(anchors,width,dest):
 cap=1024;n=len(anchors);first=(ctypes.c_uint64*n)();counts=(ctypes.c_uint32*n)();hits=(ctypes.c_uint64*(n*cap))();assert lib.anchor_find56_many(dest,len(final)//56,b''.join(anchors),n,width,first,counts,hits,cap)==0
 return [list(hits[i*cap:i*cap+counts[i]])if counts[i]<=cap else None for i in range(n)]
for normalized in[False,True]:
 src=rn.raw if normalized else raw;dst=fn if normalized else final
 for width in[16,8,4]:
  chosen=[r for r in rows if not r['admitted']and r['raw_end']-r['raw_begin']>=2*width]
  if not chosen:continue
  starts=scan([src[r['raw_begin']*56:(r['raw_begin']+width)*56]for r in chosen],width,dst);tails=scan([src[(r['raw_end']-width)*56:r['raw_end']*56]for r in chosen],width,dst)
  for r,aa,bb in zip(chosen,starts,tails):
   r.setdefault('anchor_diagnostics',[]).append(dict(normalized=normalized,width=width,starts=None if aa is None else len(aa),tails=None if bb is None else len(bb)))
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
   r.update(admitted=True,final_begin=a,final_end=b,anchor_width=width,normalized_bitids=normalized,final_sha256=hashlib.sha256(final[a*56:b*56]).hexdigest())
  print('BOUND_PHASE',normalized,width,sum(r['admitted']for r in rows),len(rows),flush=True)
result=dict(rows=rows,status='DIAGNOSTIC_CANDIDATES; classical-ID-normalized anchors are mapping hints only; every actual-final span requires independent universal proof')
(out/'phase-lifetime-spans.json').write_text(json.dumps(result,indent=2)+'\n')
(out/'phase-lifetime-proof-spans.tsv').write_text(''.join(f"{r['final_begin']}\t{r['final_end']}\t0\t0\n"for r in rows if r['admitted']))
print('TARGETS',[r for r in rows if r['admitted']and any(r['final_begin']<=t<r['final_end']for t in[11466851,11481418,11495985,11610904])])
