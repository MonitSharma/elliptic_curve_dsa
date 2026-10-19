import ctypes,ctypes.util,struct,json
from pathlib import Path
p=Path('/home/hclau/ecdsa_research/product-pareto-20261019/parent/ops.bin')
b=p.read_bytes();n=struct.unpack_from('<Q',b,8)[0]
z=ctypes.CDLL(ctypes.util.find_library('zstd'))
z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t]
z.ZSTD_decompress.restype=ctypes.c_size_t
r=ctypes.create_string_buffer(n*56)
assert z.ZSTD_decompress(r,n*56,b[16:],len(b)-16)==n*56
registered=set();resets=[]
for i in range(n):
    a=struct.unpack_from('<7Q',r,i*56)
    if a[0]==2 and a[3]!=(1<<64)-1:registered.add(a[3])
for i in range(n):
    a=struct.unpack_from('<7Q',r,i*56)
    if a[0] in (11,12) and a[3] in registered:resets.append({'op':i,'kind':a[0],'q':a[3],'condition':a[5]})
d={'registered_qubits':len(registered),'registered_reset_count':len(resets),'registered_reset_wires':len({v['q'] for v in resets}),'first_twenty':resets[:20]}
Path(__file__).with_name('REGISTERED-RESETS.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps(d,indent=2))
