import ctypes,ctypes.util,struct,json
from pathlib import Path
p=Path('/home/hclau/ecdsa_research/product-pareto-20261019/parent/ops.bin')
b=p.read_bytes(); n=struct.unpack_from('<Q',b,8)[0]
z=ctypes.CDLL(ctypes.util.find_library('zstd'))
z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t]
z.ZSTD_decompress.restype=ctypes.c_size_t
r=ctypes.create_string_buffer(n*56)
assert z.ZSTD_decompress(r,n*56,b[16:],len(b)-16)==n*56
kinds='Neg Register AppendToRegister BitInvert BitStore0 BitStore1 X Z CX CZ Swap R Hmr CCX CCZ PushCondition PopCondition DebugPrint'.split()
for lo,hi in [(1444960,1445040),(1443600,1443650)]:
    for i in range(lo,hi):
        a=struct.unpack_from('<7Q',r,i*56)
        print(i,kinds[a[0]],*[x if x!=(1<<64)-1 else '-' for x in a[1:]])
d=json.loads(Path('/home/hclau/ecdsa_research/product-width-tradeoff-20261019/parent-width.json').read_text())
print('LONGEST',sorted(d['scratch_at_first_peak'],key=lambda x:x['end']-x['start'])[-12:])
