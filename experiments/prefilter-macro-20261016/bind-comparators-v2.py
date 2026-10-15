from pathlib import Path
import ctypes,ctypes.util,struct,json,bisect,hashlib,time,collections
root=Path('/home/hclau/ecdsa_research/prefilter-macro-20261016');none=(1<<64)-1;started=time.time();old=json.loads((root/'comparator-spans.json').read_text())
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
raw=load(root/'raw-builder.bin');final=load(root.parent/'product-exact-20261015/tip/ops.bin');lib=ctypes.CDLL(str(root/'anchor_scan.so'));lib.anchor_find56_many.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.POINTER(ctypes.c_uint64),ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(ctypes.c_uint64),ctypes.c_size_t];lib.anchor_find56_many.restype=ctypes.c_int
def scan(anchors,width):
 cap=256;n=len(anchors);first=(ctypes.c_uint64*n)();counts=(ctypes.c_uint32*n)();hits=(ctypes.c_uint64*(n*cap))();assert lib.anchor_find56_many(final,len(final)//56,b''.join(anchors),n,width,first,counts,hits,cap)==0
 return [list(hits[i*cap:i*cap+counts[i]])if counts[i]<=cap else None for i in range(n)]
rows=old['rows']
for width in [16,8,4]:
 selected=[r for r in rows if not r.get('admitted_for_local_proof')and r['raw_end']-r['raw_begin']>=2*width]
 if not selected:continue
 p=scan([raw[r['raw_begin']*56:(r['raw_begin']+width)*56]for r in selected],width);s=scan([raw[(r['raw_end']-width)*56:r['raw_end']*56]for r in selected],width)
 for r,starts,tails in zip(selected,p,s):
  if starts is None or tails is None:continue
  length=r['raw_end']-r['raw_begin'];tolerance=max(64,length//4);pairs=[]
  for a in starts:
   lo=bisect.bisect_left(tails,max(a,a+length-tolerance-width));hi=bisect.bisect_right(tails,a+length+tolerance-width)
   for b in tails[lo:hi]:
    pairs.append((a,b+width))
    if len(pairs)>1:break
   if len(pairs)>1:break
  if len(pairs)!=1:continue
  a,b=pairs[0];depth=0;balanced=True
  for i in range(a,b):
   k=struct.unpack_from('<Q',final,i*56)[0]
   if k==15:depth+=1
   if k==16:depth-=1
   if depth<0:balanced=False;break
  if not balanced or depth:continue
  r.update(admitted_for_local_proof=True,final_begin=a,final_end=b,final_ops=b-a,anchor_width=width,unique_joint_anchor_pair=True,prefix_matches=len(starts),suffix_matches=len(tails),balanced_relative_scope=True,final_sha256=hashlib.sha256(final[56*a:56*b]).hexdigest())
 print('JOINT_ANCHOR_PROGRESS width',width,'admitted',sum(r.get('admitted_for_local_proof',False)for r in rows),flush=True)
result=dict(source_revision=old['source_revision'],original_final_sha256=old['original_final_sha256'],source_calls=len(rows),admitted_for_local_proof=sum(r.get('admitted_for_local_proof',False)for r in rows),seconds=time.time()-started,rows=rows,proof_status='exact source-anchor candidate spans; universal per-final-region proof still required')
(root/'comparator-spans-v2.json').write_text(json.dumps(result,indent=2)+'\n');(root/'comparator-proof-spans-v2.tsv').write_text(''.join(f"{r['final_begin']}\t{r['final_end']}\t{r['width']}\t{int(r['borrow'])}\n"for r in rows if r.get('admitted_for_local_proof')));print('JOINT_ANCHOR_COMPLETE',result['admitted_for_local_proof'],result['seconds'])
