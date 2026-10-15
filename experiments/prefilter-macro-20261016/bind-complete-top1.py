from pathlib import Path
import ctypes,ctypes.util,struct,json,re,hashlib,bisect,time
root=Path('/home/hclau/ecdsa_research/prefilter-macro-20261016');started=time.time();none=(1<<64)-1
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
raw=load(root/'raw-builder.bin');final=load(root.parent/'product-exact-20261015/tip/ops.bin');rows=json.loads((root/'bound-spans.json').read_text())['rows'];entry={}
for l in(root/'observer.log').read_text().splitlines():
 m=re.match(r'MACRO_TOP1_ENTER rev=(true|false) tick=(\d+) at=(\d+)',l)
 if m:entry[m[1]=='true',int(m[2])]=int(m[3])
lib=ctypes.CDLL(str(root/'anchor_scan.so'));lib.anchor_find56_many.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.POINTER(ctypes.c_uint64),ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(ctypes.c_uint64),ctypes.c_size_t];lib.anchor_find56_many.restype=ctypes.c_int
for r in rows:r['complete_raw_begin']=entry[r['reverse'],r['tick']];r['complete_admitted_candidate']=False
for width in[16,8,4]:
 selected=[r for r in rows if not r['complete_admitted_candidate']and r['prefix_unique']];n=len(selected);cap=256;anchors=b''.join(raw[r['complete_raw_begin']*56:(r['complete_raw_begin']+width)*56]for r in selected)
 first=(ctypes.c_uint64*n)();counts=(ctypes.c_uint32*n)();hits=(ctypes.c_uint64*(n*cap))();assert lib.anchor_find56_many(final,len(final)//56,anchors,n,width,first,counts,hits,cap)==0
 for idx,r in enumerate(selected):
  if counts[idx]>cap:continue
  length=r['end']-r['complete_raw_begin'];tol=max(128,length//4);end=r['final_end'];positions=[a for a in hits[idx*cap:idx*cap+counts[idx]]if abs(end-a-length)<=tol]
  if len(positions)!=1:continue
  a=positions[0];depth=0;balanced=True
  for i in range(a,end):
   k=struct.unpack_from('<Q',final,56*i)[0]
   if k==15:depth+=1
   if k==16:depth-=1
   if depth<0:balanced=False;break
  if not balanced or depth:continue
  r.update(complete_admitted_candidate=True,complete_final_begin=a,complete_final_end=end,complete_final_ops=end-a,entry_anchor_width=width,complete_final_sha256=hashlib.sha256(final[a*56:end*56]).hexdigest())
 print('COMPLETE_TOP1_PROGRESS',width,sum(r['complete_admitted_candidate']for r in rows),flush=True)
result=dict(source_revision='4b2ec52fc55da796aa8f5ef851290297e8706424',source_family='entire Y21 top1 clause across bitx/bit0/nbx branches',instances=len(rows),admitted_candidates=sum(r['complete_admitted_candidate']for r in rows),seconds=time.time()-started,rows=rows,universal_proof_required=True)
(root/'complete-top1-spans.json').write_text(json.dumps(result,indent=2)+'\n');(root/'complete-top1-proof-spans.tsv').write_text(''.join(f"{r['complete_final_begin']}\t{r['complete_final_end']}\t{r['tick']}\t{int(r['reverse'])}\n"for r in rows if r['complete_admitted_candidate']));print('COMPLETE_TOP1_BINDINGS',result['admitted_candidates'],result['seconds']);print('FIRST',json.dumps(next(r for r in rows if not r['reverse']and r['tick']==3)))
