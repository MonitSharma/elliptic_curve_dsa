from pathlib import Path
import ctypes,ctypes.util,struct,json,bisect,time
root=Path('/home/hclau/ecdsa_research/precision-repair-20261016');none=(1<<64)-1;started=time.time()
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
raw=load(root/'raw-builder.bin');final=load(root.parent/'product-exact-20261015/tip/ops.bin');rows=json.loads((root/'surviving-folds.json').read_text())['rows']
write={};read={};kills={};depths=[];depth=0;n=len(raw)//56
for i in range(n):
 k,a,b,t,ct,cc,rt=struct.unpack_from('<7Q',raw,56*i);depths.append(depth)
 if k in (3,4,5,12):write.setdefault(ct,[]).append(i)
 if k==3:read.setdefault(ct,[]).append(i)
 if cc!=none:read.setdefault(cc,[]).append(i)
 if k in(4,5,12)and depth==0 and cc==none:kills.setdefault(ct,[]).append(i)
 if k==15:depth+=1
 if k==16:depth-=1;assert depth>=0
assert depth==0;depths.append(0)
def next_at(v,at):
 i=bisect.bisect_left(v,at);return v[i]if i<len(v)else n+1
for r in rows:
 a=r['start'];b=r['end'];original=b
 for attempt in range(32):
  bits={ct for ct,v in write.items()if next_at(v,a)<b};extend=b
  for ct in bits:
   kill=next_at(kills.get(ct,[]),b);first_read=next_at(read.get(ct,[]),b)
   if first_read<kill:extend=max(extend,kill)
  if extend==b:break
  b=extend
  if b>n:break
 else:raise AssertionError('no finite local closure')
 r['extended_end']=b;r['added_ops']=b-original;r['balanced']=b<=n and depths[a]==depths[b]==0
 r['local_in']=all(next_at(read.get(ct,[]),a)>=min(next_at(kills.get(ct,[]),a),b)for ct in bits)
 if r['balanced']and r['local_in']:
  block=raw[a*56:b*56];at=final.find(block);r['extended_match']=at>=0 and at%56==0 and final.find(block,at+56)<0
  if r['extended_match']:r['extended_final_start']=at//56
 else:r['extended_match']=False
result=dict(sites=len(rows),extended_matches=sum(r['extended_match']for r in rows),seconds=time.time()-started,rows=rows)
(root/'extended-regions.json').write_text(json.dumps(result,indent=2)+'\n');rank=json.loads((root/'PREDECLARED-FAMILY.json').read_text())['ranked_sites'];d={(r['reverse'],r['tick']):r for r in rows};print('EXTENDED_REGIONS',result['sites'],result['extended_matches'],result['seconds']);print('TOP16',[(r['reverse'],r['tick'],d[r['reverse'],r['tick']]['extended_match'],d[r['reverse'],r['tick']]['added_ops'])for r in rank[:16]])
