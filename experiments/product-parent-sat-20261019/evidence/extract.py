import ctypes,ctypes.util,hashlib,json,struct
from pathlib import Path
r=Path(__file__).resolve().parent
base=Path('/home/hclau/ecdsa_research/product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin')
b=base.read_bytes();n=struct.unpack_from('<Q',b,8)[0];assert n==17891821
z=ctypes.CDLL(ctypes.util.find_library('zstd'))
z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
raw=ctypes.create_string_buffer(n*56)
assert z.ZSTD_decompress(raw,n*56,b[16:],len(b)-16)==n*56
bodyhash=hashlib.sha3_256(memoryview(raw)[:-96*56]).hexdigest()
assert bodyhash=='c143e90580bb0c6f6a12996a50147c179c4fdfe3a50d8af85350bf9e6d755e04'
leases=json.loads(Path('/home/hclau/ecdsa_research/product-pareto-20261019/parent4-transfer/leases.json').read_text())
starts={s[0]:j for j,s in enumerate(leases)};depths={};stack=[]
for i in range(max(starts)+1):
    kind=struct.unpack_from('<Q',raw,i*56)[0]
    if i in starts:depths[i]=len(stack)
    if kind==15:stack.append(struct.unpack_from('<Q',raw,i*56+40)[0])
    elif kind==16:stack.pop()
manifest=[]
for j,s in enumerate(leases):
    lo,hi=s[:2];prefix=f'lease-{j+1:02}'
    chunk=bytes(memoryview(raw)[lo*56:(hi+1)*56]);(r/(prefix+'.raw')).write_bytes(chunk)
    d={'lease':j+1,'first':lo,'last':hi,'initial_depth':depths[lo],
       'base_pre_tail_sha3_256':bodyhash,'raw_sha256':hashlib.sha256(chunk).hexdigest(),
       'raw_file':prefix+'.raw','row':s,'statement':'Equality of the endpoint control products, over arbitrary boundary wires/flags and arbitrary measurement outcomes. Initial effective guards are true, separately certified by the global interpreter.'}
    (r/(prefix+'.json')).write_text(json.dumps(d,indent=2)+'\n');manifest.append(d)
(r/'INPUT-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Extracted',len(manifest),'source-bound exact lease intervals')
