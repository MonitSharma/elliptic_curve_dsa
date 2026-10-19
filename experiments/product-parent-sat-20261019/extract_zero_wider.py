import ctypes,ctypes.util,hashlib,json,struct
from pathlib import Path
r=Path(__file__).resolve().parent
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
    b=p.read_bytes();n=struct.unpack_from('<Q',b,8)[0];raw=ctypes.create_string_buffer(n*56)
    assert z.ZSTD_decompress(raw,n*56,b[16:],len(b)-16)==n*56
    return raw,n
base,nbase=load(Path('/home/hclau/ecdsa_research/product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin'))
row=bytes(memoryview(base)[17876171*56:17876172*56]);del base
assert hashlib.sha3_256(row).hexdigest()=='167c7dad3201c7b11743b8d6bdd1949fa61952ac7201f71692a3a369be305823'
parent,n=load(Path('/home/hclau/ecdsa_research/product-pareto-20261019/parent/ops.bin'))
assert hashlib.sha3_256(memoryview(parent)).hexdigest()=='429af1c31b54064e17e7602be516b519c066c241e218d56f002287ea02b16842'
i=17876252
h=hashlib.sha3_256();h.update(memoryview(parent)[:i*56]);h.update(row);h.update(memoryview(parent)[i*56:-96*56]);bodyhash=h.hexdigest()
assert bodyhash=='468e86dd1628976643d42b4bb50bdb8c43211f4d29bfbc3df60b11f7342ac619'
targets={i-k:k for k in (8192,32768,131072)};starts={};depth=0;last_root=0
for j in range(i):
    if depth==0:last_root=j
    if j in targets:starts[targets[j]]=last_root
    kind=struct.unpack_from('<Q',parent,j*56)[0]
    if kind==15:depth+=1
    if kind==16:depth-=1
for k,start in starts.items():
    prefix=f'zero-{k}';chunk=bytes(memoryview(parent)[start*56:i*56])+row;(r/(prefix+'.raw')).write_bytes(chunk)
    d={'start':start,'first':i,'last':i,'initial_depth':0,'lookback':k,
       'base_pre_tail_sha3_256':bodyhash,'row_sha3_256':hashlib.sha3_256(row).hexdigest(),
       'raw_sha256':hashlib.sha256(chunk).hexdigest(),'raw_sha3_256':hashlib.sha3_256(chunk).hexdigest(),'raw_file':prefix+'.raw'}
    (r/(prefix+'.json')).write_text(json.dumps(d,indent=2)+'\n');print(prefix,start,list(struct.unpack('<7Q',row)),flush=True)

