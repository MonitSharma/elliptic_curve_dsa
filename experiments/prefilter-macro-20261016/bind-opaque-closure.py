exec((__import__('pathlib').Path(__file__).parent/'bind-carry-helpers.py').read_text().split('raw=load(')[0])
raw=load(root/'raw-builder.bin');final=load(root.parent/'product-exact-20261015/tip/ops.bin');none=(1<<64)-1
old=json.loads((out/'phase-lifetime-spans.json').read_text());bases=[r for r in old['rows']if r['family'].startswith('square.rs::')and r['raw_begin']<=5497375<r['raw_end']];rows=[]
for r in bases:
 for pad in[0,8,16,32,64,128,256,512,1024,2048,4096,8192,16384,32768]:rows.append(dict(family=r['family'],raw_begin=r['raw_begin']-pad,raw_end=r['raw_end']+pad,pad=pad))
lib=ctypes.CDLL(str(root/'anchor_scan.so'));lib.anchor_find56_many.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.POINTER(ctypes.c_uint64),ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(ctypes.c_uint64),ctypes.c_size_t];lib.anchor_find56_many.restype=ctypes.c_int
def scan(anchors,width):
 cap=1024;n=len(anchors);first=(ctypes.c_uint64*n)();counts=(ctypes.c_uint32*n)();hits=(ctypes.c_uint64*(n*cap))();assert lib.anchor_find56_many(final,len(final)//56,b''.join(anchors),n,width,first,counts,hits,cap)==0
 return [list(hits[i*cap:i*cap+counts[i]])if counts[i]<=cap else None for i in range(n)]
pairs=[]
for width in[16,8,4]:
 aa=scan([raw[r['raw_begin']*56:(r['raw_begin']+width)*56]for r in rows],width);bb=scan([raw[(r['raw_end']-width)*56:r['raw_end']*56]for r in rows],width)
 for r,starts,tails in zip(rows,aa,bb):
  r.setdefault('diagnostics',[]).append(dict(width=width,starts=None if starts is None else len(starts),tails=None if tails is None else len(tails)))
  if starts is None or tails is None:continue
  length=r['raw_end']-r['raw_begin'];tol=max(200000,length*2);pp=[(a,b+width)for a in starts for b in tails if a<=5498416<b+width and abs(b+width-a-length)<=tol and b+width-a<=400000]
  # Ambiguous source ancestry is explicitly retained as a diagnostic only.
  # The independent actual-final universal proof is the sole semantic gate.
  for a,b in pp:pairs.append(dict(r,anchor_width=width,anchor_pair_count=len(pp),final_begin=a,final_end=b))
print('OPAQUE_ANCHOR_PAIRS',len(pairs),flush=True)
stack=[];close={};parents={};points={r[k]for r in pairs for k in['final_begin','final_end']};atpoint={}
for i in range(len(final)//56):
 if i in points:atpoint[i]=tuple(stack)
 k=struct.unpack_from('<Q',final,i*56)[0]
 if k==15:stack.append(i)
 if k==16:
  a=stack.pop();close[a]=i+1
accepted=[]
for r in pairs:
 a,b=r['final_begin'],r['final_end'];sa=atpoint[a];sb=atpoint[b];common=0
 while common<min(len(sa),len(sb))and sa[common]==sb[common]:common+=1
 if len(sa)>common:a=min(a,sa[common])
 if len(sb)>common:b=max(b,max(close[p]for p in sb[common:]))
 # Verify exact balance after widening and no remaining crossing scope.
 depth=0;ok=True
 for i in range(a,b):
  k=struct.unpack_from('<Q',final,i*56)[0]
  if k==15:depth+=1
  if k==16:depth-=1
  if depth<0:ok=False;break
 if not ok or depth:continue
 accepted.append(dict(r,closure_begin=a,closure_end=b,closure_ops=b-a,final_sha256=hashlib.sha256(final[a*56:b*56]).hexdigest()))
dedup={}
for r in accepted:dedup.setdefault((r['closure_begin'],r['closure_end']),r)
selected=sorted(dedup.values(),key=lambda r:r['closure_ops'])
(out/'opaque-closure-spans.json').write_text(json.dumps(dict(rows=rows,pairs=pairs,selected=selected,status='DIAGNOSTIC_CANDIDATES: actual-final balanced scope closures; mandatory independent universal proof'),indent=2)+'\n')
(out/'opaque-closure-proof-spans.tsv').write_text(''.join(f"{r['closure_begin']}\t{r['closure_end']}\t0\t0\n"for r in selected))
print('OPAQUE_CLOSURES',[(r['family'],r['pad'],r['closure_begin'],r['closure_end'],r['closure_ops'])for r in selected])
