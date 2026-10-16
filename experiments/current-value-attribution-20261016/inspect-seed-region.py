from pathlib import Path
import json,struct,ctypes,ctypes.util,hashlib,difflib
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016');assert(r/'seed-attribution.exit').read_text().strip()=='0'
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
m=json.loads((r/'actual-seed-markers.json').read_text());assert len(m['markers'])==2
a,b=m['markers'];assert a['before'] and not b['before'];raw=load(r/'raw-seed-builder.bin');actual=load(r.parent/'product-exact-20261015/tip/ops.bin')
x=[raw[i*56:(i+1)*56]for i in range(a['raw_at'],b['raw_at'])];y=[actual[i*56:(i+1)*56]for i in range(a['at'],b['at'])]
changes=[]
for tag,i,j,k,l in difflib.SequenceMatcher(a=x,b=y,autojunk=False).get_opcodes():
 if tag!='equal':changes.append(dict(kind=tag,raw_begin=a['raw_at']+i,raw_end=a['raw_at']+j,actual_begin=a['at']+k,actual_end=a['at']+l,raw=[list(struct.unpack('<7Q',v))for v in x[i:j]],actual=[list(struct.unpack('<7Q',v))for v in y[k:l]]))
out=dict(status='ACTUAL FULL SEED REGION RAW/FINAL DIFF; DIAGNOSTIC',raw_begin=a['raw_at'],raw_end=b['raw_at'],actual_begin=a['at'],actual_end=b['at'],raw_ops=len(x),actual_ops=len(y),raw_region_sha256=hashlib.sha256(b''.join(x)).hexdigest(),actual_region_sha256=hashlib.sha256(b''.join(y)).hexdigest(),complete_region_byte_identical=x==y,changes=changes)
(r/'seed-region-diff.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
