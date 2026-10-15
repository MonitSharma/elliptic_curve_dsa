"""Require selected-source regeneration to change only the96-op nonce tail."""
from pathlib import Path
import ctypes,ctypes.util,hashlib,json,struct
root=Path(__file__).resolve().parent;e=root/'evidence';up=root.parent/'product-exact-20261015'
selected=json.loads((e/'selection.json').read_text())['nonce']
z=ctypes.CDLL(ctypes.util.find_library('zstd'))
z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
z.ZSTD_isError.argtypes=[ctypes.c_size_t];z.ZSTD_isError.restype=ctypes.c_uint
def inspect(path,nonce=None):
 data=path.read_bytes();assert data[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',data,8)[0];assert 96<n<30_000_000
 out=ctypes.create_string_buffer(n*56);body=data[16:];size=z.ZSTD_decompress(out,len(out),body,len(body));assert not z.ZSTD_isError(size) and size==n*56
 raw=out.raw;tail=raw[-96*56:]
 for i in range(96):
  row=struct.unpack_from('<7Q',tail,i*56);assert row[0]==6 and row[3]<=1 and all(row[j]==2**64-1 for j in [1,2,4,5,6])
  if i%2:assert row==struct.unpack_from('<7Q',tail,(i-1)*56)
  if nonce is not None:assert row[3]==(nonce>>(i//2)&1)
 return {'ops':n,'prefix_ops':n-96,'prefix_sha3_256':hashlib.sha3_256(raw[:-96*56]).hexdigest(),'stream_sha256':hashlib.sha256(data).hexdigest(),'tail_sha256':hashlib.sha256(tail).hexdigest()}
frozen=inspect(up/'wide-compound-20261016/wide-15-retained-512.bin')
final=inspect(up/'candidate-wide-compound/ops.bin',selected)
assert frozen['prefix_ops']==final['prefix_ops'] and frozen['prefix_sha3_256']==final['prefix_sha3_256']
assert frozen['stream_sha256']==json.loads((e/'FREEZE.json').read_text())['external_stream_sha256']
report={'status':'PASS_only_identity_tail_changed','nonce':selected,'frozen':frozen,'final':final,'raw_record_bytes':56}
(e/'prefix-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
