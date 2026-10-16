from pathlib import Path
import struct,ctypes,ctypes.util,json,hashlib,ast
r=Path('/home/hclau/ecdsa_research/quantum-borrow-family-20261016');NONE=2**64-1
z=ctypes.CDLL(ctypes.util.find_library('zstd'))
z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
z.ZSTD_compressBound.argtypes=[ctypes.c_size_t];z.ZSTD_compressBound.restype=ctypes.c_size_t
z.ZSTD_compress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_int];z.ZSTD_compress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
def enc(rows):return b''.join(struct.pack('<7Q',*o)for o in rows)
def save(p,data):
 o=ctypes.create_string_buffer(z.ZSTD_compressBound(len(data)));n=z.ZSTD_compress(o,len(o),data,len(data),3);p.write_bytes(b'QECCOPSZ'+struct.pack('<Q',len(data)//56)+o.raw[:n])
def op(k,t=NONE,a=NONE,zq=NONE,bt=NONE,bc=NONE):return(k,zq,a,t,bt,bc,NONE)
raw=load(r/'raw-builder.bin');final=load(r.parent/'product-exact-20261015/tip/ops.bin');profile=json.loads((r/'family-cost-profile.json').read_text());frames={}
assert hashlib.sha256((r/'raw-builder.bin').read_bytes()).hexdigest()==profile['raw_stream_sha256']
for line in(r/'flag-frames.tsv').read_text().splitlines():
 f=line.split('\t');_,at,round,mul,k,target,A,B,seed=f;frames[int(at)+2]=dict(round=int(round),multiply=bool(int(mul)),k=int(k),target=int(target),a=ast.literal_eval(A),b=ast.literal_eval(B),seed=int(seed[5:-1]))
selected=[s for s in profile['source_entries']if s['family']=='pingpong::flag_erase'];assert len(selected)==len(frames)==12
result=[];extra_bit=45701
for j,s in enumerate(selected):
 f=frames[s['raw_at']];n=f['k'];lo=256-n;A,B=f['a'],f['b'];assert len(A)==len(B)==256;assert s['u']==A[lo:]and s['v']==B[lo:]and s['borrow']==B[lo-1]==f['seed'];lower=(A[lo-1],B[lo-1],B[lo-2]);target=f['target'];assert len(set([target,*lower,*s['u'],*s['v']]))==2*n+4
 begin=s['raw_at']-2;end=s['raw_body_end']+1;old=raw[begin*56:end*56];assert s['actual_wrapper_bound']and len(s['final_matches'])==1
 at=s['final_matches'][0]-2;assert final[at*56:(at+len(old)//56)*56]==old;assert final.count(old)==1
 rows=list(struct.iter_unpack('<7Q',old));assert rows[0][0]==12 and rows[0][3]==target and rows[1][0]==15 and rows[-1][0]==16
 # The first and last borrow-control affine pairs are the only occurrences of the old seed.
 indices=[i for i,o in enumerate(rows)if o[0]in(8,9,13,14)and f['seed']in o[1:4]];assert len(indices)==4,indices
 changed=[]
 for i in indices:
  o=list(rows[i]);
  for q in range(1,4):
   if o[q]==f['seed']:o[q]=target
  rows[i]=tuple(o);changed.append(i)
 la,lb,ls=lower
 compute=[op(6,la),op(8,la,ls),op(8,lb,ls),op(13,target,lb,la),op(8,lb,ls),op(8,la,ls),op(6,la),op(8,target,ls)]
 cleanup=[op(12,target,bt=extra_bit),op(15,bc=extra_bit),op(7,lb),op(7,ls),op(9,lb,la),op(9,ls,la),op(9,ls,lb),op(16)]
 new=enc(rows[:2]+compute+rows[2:-1]+cleanup+rows[-1:]);save(r/f'old-flag-{j}.bin',old);save(r/f'new-flag-{j}.bin',new)
 # Negative changes one required cleanup CZ to the opposite lower variable; alias-free shape retained.
 bad=list(struct.iter_unpack('<7Q',new));index=len(bad)-4;o=list(bad[index]);assert o[0]==9 and o[2]==la;o[2]=s['u'][-1];bad[index]=tuple(o);save(r/f'negative-flag-{j}.bin',enc(bad))
 scratch=sorted({o[3]for o in struct.iter_unpack('<7Q',old)if o[0]==13});assert len(scratch)==n-1
 result.append(dict(site=j,**f,raw_start=begin,raw_end=end,final_start=at,final_end=at+len(old)//56,lower=lower,old_seed=f['seed'],old_bytes_sha256=hashlib.sha256(old).hexdigest(),new_bytes_sha256=hashlib.sha256(new).hexdigest(),scratch=scratch,changed_seed_rows=changed,added_MR_bit=extra_bit,old_ops=len(old)//56,new_ops=len(new)//56))
(r/'flag-regions.json').write_text(json.dumps(result,indent=2)+'\n');print('All12 complete raw/final wrappers byte-identical, source-bit seeds and full lower operands bound; +16ops/site,+1CCX,+1HMR')
