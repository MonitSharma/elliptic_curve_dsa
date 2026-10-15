from pathlib import Path
import ctypes,ctypes.util,struct,json,re,hashlib,time,collections
root=Path('/home/hclau/ecdsa_research/prefilter-macro-20261016');none=(1<<64)-1;started=time.time()
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
raw=load(root/'raw-builder.bin');final=load(root.parent/'product-exact-20261015/tip/ops.bin');sites={};rows=[]
for l in(root/'observer.log').read_text().splitlines():
 if l.startswith('C35_SITE\t'):
  _,where,n,seed,at=l.split('\t');sites.setdefault(int(at),[]).append(dict(source=where,width=int(n),borrow=bool(int(seed)),raw_begin=int(at)))
 if l.startswith('C35_END\t'):
  _,at,end,n,seed=l.split('\t');r=sites[int(at)].pop();assert r['width']==int(n)and r['borrow']==bool(int(seed));r['raw_end']=int(end);rows.append(r)
assert all(not v for v in sites.values())
lib=ctypes.CDLL(str(root/'anchor_scan.so'));lib.anchor_find56.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.POINTER(ctypes.c_uint64),ctypes.POINTER(ctypes.c_uint32)];lib.anchor_find56.restype=ctypes.c_int
def find(anchors,width):
 first=(ctypes.c_uint64*len(anchors))();counts=(ctypes.c_uint32*len(anchors))();assert lib.anchor_find56(final,len(final)//56,b''.join(anchors),len(anchors),width,first,counts)==0;return list(first),list(counts)
selected=[r for r in rows if r['raw_end']-r['raw_begin']>=32];prefix=[raw[56*r['raw_begin']:56*(r['raw_begin']+16)]for r in selected];suffix=[raw[56*(r['raw_end']-16):56*r['raw_end']]for r in selected];pa,pc=find(prefix,16);sa,sc=find(suffix,16)
for idx in range(min(32,len(selected))):
 assert final.find(prefix[idx])==(pa[idx]*56 if pc[idx]else-1)
 assert final.find(suffix[idx])==(sa[idx]*56 if sc[idx]else-1)
for r,a,c,b,d in zip(selected,pa,pc,sa,sc):
 r['prefix_matches']=c;r['suffix_matches']=d;r['candidate_bound']=c==d==1 and a<b+16
 if not r['candidate_bound']:continue
 r['final_begin']=a;r['final_end']=b+16;r['final_ops']=b+16-a;r['raw_ops']=r['raw_end']-r['raw_begin'];r['length_plausible']=abs(r['final_ops']-r['raw_ops'])<=max(1000,r['raw_ops']//2)
 depth=0;balanced=True;counts=collections.Counter();scratch=set();qs=set();classical=set()
 for i in range(a,b+16):
  k,q2,q1,t,ct,cc,rt=struct.unpack_from('<7Q',final,56*i);counts[k]+=1;qs.update(q for q in(q2,q1,t)if q!=none);classical.update(x for x in(ct,cc)if x!=none)
  if k in(11,12):scratch.add(t)
  if k==15:depth+=1
  if k==16:depth-=1
  if depth<0:balanced=False;break
 r['balanced_relative_scope']=balanced and depth==0;r['admitted_for_local_proof']=r['length_plausible']and r['balanced_relative_scope'];r['counts']={str(k):v for k,v in sorted(counts.items())};r['qubits']=sorted(qs);r['reset_targets']=sorted(scratch);r['classical_bits']=sorted(classical);r['final_sha256']=hashlib.sha256(final[56*a:56*(b+16)]).hexdigest()
for r in rows:
 r.setdefault('admitted_for_local_proof',False)
result=dict(source_revision='4b2ec52fc55da796aa8f5ef851290297e8706424',original_final_sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e',source_calls=len(rows),long_calls=len(selected),bound=sum(r.get('candidate_bound',False)for r in rows),admitted_for_local_proof=sum(r['admitted_for_local_proof']for r in rows),seconds=time.time()-started,rows=sorted(rows,key=lambda r:r['raw_begin']),proof_status='candidate spans only; each final region still requires arbitrary-input reset-projection proof')
(root/'comparator-spans.json').write_text(json.dumps(result,indent=2)+'\n');(root/'comparator-proof-spans.tsv').write_text(''.join(f"{r['final_begin']}\t{r['final_end']}\t{r['width']}\t{int(r['borrow'])}\n"for r in rows if r['admitted_for_local_proof']));print('COMPARATOR_BINDINGS',json.dumps({k:v for k,v in result.items()if k!='rows'}))
