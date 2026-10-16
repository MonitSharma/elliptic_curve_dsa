from pathlib import Path
import ctypes,ctypes.util,struct,json,re,bisect
root=Path('/home/hclau/ecdsa_research/prefilter-macro-20261016');out=root/'additional';out.mkdir(exist_ok=True);none=(1<<64)-1
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
raw=load(root/'raw-builder.bin');final=load(root.parent/'product-exact-20261015/tip/ops.bin');targets=[11495985,11481418,11466851,11623042,11610904,5498416];compact=0;rows=[];stack=[];scope_stack=[];wanted=set(targets);original_targets={3332030}
for i in range(len(final)//56):
 r=struct.unpack_from('<7Q',final,i*56);k,q2,q1,t,ct,cc,rt=r
 if k not in(1,2):
  if compact in wanted:original_targets.add(i);rows.append(dict(compact=compact,original=i,record=r,scope=list(stack)))
  compact+=1
 if i==3332030:rows.append(dict(original=i,record=r,scope=list(stack)))
 if k==15:stack.append((i,cc))
 if k==16:stack.pop()
fragments=[]
for l in(root/'observer.log').read_text().splitlines():
 if l.startswith('DIRTY_FRAGMENT\t'):
  f=l.split('\t');fragments.append(dict(kind=f[1],width=int(f[2]),begin=int(f[3]),end=int(f[4]),tail=f[5:]))
top=json.loads((root/'complete-top1-spans.json').read_text())['rows'];comparators=json.loads((root/'comparator-spans-v2.json').read_text())['rows']
for row in rows:
 i=row['original'];row['neighborhood']=[dict(at=j,record=struct.unpack_from('<7Q',final,j*56))for j in range(max(0,i-12),i+18)];row['raw_matches']=[]
 for width in[16,8,4,1]:
  signature=final[i*56:(i+width)*56];at=raw.find(signature);positions=[]
  while at>=0 and len(positions)<257:
   if at%56==0:positions.append(at//56)
   at=raw.find(signature,at+1)
  row['raw_matches'].append(dict(anchor_width=width,positions=positions))
  if len(positions)==1:
   pos=positions[0];row['raw_original_hint']=pos;row['source_fragments']=[r for r in fragments if r['begin']<=pos<r['end']];row['nearest_top1']=[{k:r[k]for k in['reverse','tick','complete_raw_begin','end','complete_final_begin','complete_final_end']}for r in top if abs(r.get('complete_final_begin',0)-i)<5000];break
(out/'residual-sites.json').write_text(json.dumps(dict(compact_ops=compact,original_ops=len(final)//56,rows=rows),indent=2)+'\n')
for r in rows:print('SITE',json.dumps({k:v for k,v in r.items()if k not in['neighborhood','raw_matches']}))
