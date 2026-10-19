import ctypes,ctypes.util,struct,json,sys
from pathlib import Path
root=Path(__file__).resolve().parent
cut=int(sys.argv[1]); prefix=sys.argv[2] if len(sys.argv)>2 else 'borrow'
d=json.loads((root/(f'{prefix}-width-{cut}.json' if prefix!='borrow' else f'width-{cut}.json')).read_text()); at=d['first_peak_op']
b=(root/f'{prefix}-{cut}.ops.bin').read_bytes(); n=struct.unpack_from('<Q',b,8)[0]
z=ctypes.CDLL(ctypes.util.find_library('zstd'))
z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t]
z.ZSTD_decompress.restype=ctypes.c_size_t
r=ctypes.create_string_buffer(n*56)
assert z.ZSTD_decompress(r,n*56,b[16:],len(b)-16)==n*56
kinds='Neg Register AppendToRegister BitInvert BitStore0 BitStore1 X Z CX CZ Swap R Hmr CCX CCZ PushCondition PopCondition DebugPrint'.split()
print({k:v for k,v in d.items() if k!='scratch_at_first_peak'})
for i in range(at-45,at+60):
    a=struct.unpack_from('<7Q',r,i*56)
    print(i,kinds[a[0]],*[x if x!=(1<<64)-1 else '-' for x in a[1:]])
