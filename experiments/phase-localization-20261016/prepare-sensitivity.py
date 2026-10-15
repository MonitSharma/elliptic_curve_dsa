from pathlib import Path
import ctypes,ctypes.util,struct,json,shutil
r=Path('/home/hclau/ecdsa_research/phase-localization-20261016')
body=(r/'body.rs').read_text();body=body.replace('drop(initial);let timer=', 'drop(initial);std::fs::write("initial-q.bin",iq.iter().flat_map(|v|v.to_le_bytes()).collect::<Vec<_>>()).unwrap();std::fs::write("initial-b.bin",ib.iter().flat_map(|v|v.to_le_bytes()).collect::<Vec<_>>()).unwrap();let timer=')
(r/'tool/src/body.rs').write_text(body)
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
d=(r.parent/'product-exact-20261015/tip/ops.bin').read_bytes();n=struct.unpack_from('<Q',d,8)[0];buf=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(buf,len(buf),d[16:],len(d)-16)==n*56
ops=bytearray();mr=[];none=2**64-1;depth=maximum=0
for i,(k,b,a,t,bt,c,reg)in enumerate(struct.iter_unpack('<7Q',buf.raw)):
 if k in[1,2,17]:continue
 vals=[65535 if v==none else v for v in[a,b,t,c,bt]];assert max(vals)<=65535
 ops.extend(struct.pack('<5HBx',*vals,k))
 if k in[11,12]:mr.append(i)
 if k==15:depth+=1;maximum=max(depth,maximum)
 if k==16:depth-=1
assert depth==0
(r/'compact.bin').write_bytes(ops);(r/'mr-map.bin').write_bytes(struct.pack('<'+'I'*len(mr),*mr))
(r/'compact-meta.json').write_text(json.dumps(dict(ops=len(ops)//12,mr=len(mr),max_depth=maximum,nq=1234,nb=45701),indent=2)+'\n')
for name in['simd8.c','simd8.h']:shutil.copy2(r.parent/'simd-prefilter-20261015/tool'/name,r/name)
print(len(ops)//12,len(mr),maximum)
