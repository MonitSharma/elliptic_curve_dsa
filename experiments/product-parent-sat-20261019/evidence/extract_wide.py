import ctypes,ctypes.util,hashlib,json,struct
from pathlib import Path
r=Path(__file__).resolve().parent
base=Path('/home/hclau/ecdsa_research/product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin')
b=base.read_bytes();n=struct.unpack_from('<Q',b,8)[0]
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
raw=ctypes.create_string_buffer(n*56)
assert z.ZSTD_decompress(raw,n*56,b[16:],len(b)-16)==n*56
bodyhash=hashlib.sha3_256(memoryview(raw)[:-96*56]).hexdigest()
assert bodyhash=='c143e90580bb0c6f6a12996a50147c179c4fdfe3a50d8af85350bf9e6d755e04'
meta=json.loads((r/'lease-02.json').read_text());first,last=meta['first'],meta['last']
depth=0;last_root=0;starts={};lookbacks=(16,64,256,1024,4096,16384,65536)
targets={first-k:k for k in lookbacks}
for i in range(first+1):
    if depth==0:last_root=i
    if i in targets:starts[targets[i]]=last_root
    kind=struct.unpack_from('<Q',raw,i*56)[0]
    if kind==15:depth+=1
    if kind==16:depth-=1
for k in lookbacks:
    start=starts[k];prefix=f'wide-02-{k}';chunk=bytes(memoryview(raw)[start*56:(last+1)*56]);(r/(prefix+'.raw')).write_bytes(chunk)
    m=dict(meta,start=start,raw_file=prefix+'.raw',raw_sha256=hashlib.sha256(chunk).hexdigest(),lookback=k,initial_depth=0)
    (r/(prefix+'.json')).write_text(json.dumps(m,indent=2)+'\n')
    print(prefix,'start',start,'actual lookback',first-start,flush=True)
