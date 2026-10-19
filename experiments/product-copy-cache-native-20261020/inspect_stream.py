"""Read-only source/identity-tail binding for the already completed prototype."""
import ctypes,ctypes.util,hashlib,json,struct
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;blob=(ws/'product-classical-closure-20261019/input.ops.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='17c767f514ca98ad02d4da9e5b1dbedf67189e5c70b7b15916adc0f0c2f0a7f7'
n=struct.unpack_from('<Q',blob,8)[0];assert blob[:8]==b'QECCOPSZ' and n==17889635
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
out=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(out,len(out),blob[16:],len(blob)-16)==len(out)
v=memoryview(out).cast('B');assert hashlib.sha3_256(v).hexdigest()=='2ef31475f03b40a72d5522d830717aef4c1675d0e1a061bf0bfed78ab7d2f265'
fields=lambda i:list(struct.unpack_from('<7Q',v,i*56))
tail=[fields(i) for i in range(n-96,n)]
assert all(tail[i]==tail[i+1] for i in range(0,96,2))
result={'status':'FROZEN_PARENT_FULL_AND_PRETAIL_SOURCE_INSPECTION_PASS','full_ops':n,'pre_tail_ops':n-96,'pre_tail_sha3_256':hashlib.sha3_256(v[:-96*56]).hexdigest(),'first':14241681,'last':14245297,'first_fields':fields(14241681),'last_fields':fields(14245297),'storage':558,'storage_untouched_closed_interval':all(558 not in fields(i)[1:4] for i in range(14241681,14245298)),'identity_tail96_unchanged':True,'expected_output_full_sha3_256':'d343ca717c726c9136505edb1ba3602a58f7bfe063151d8a9e82b4f39d71a6a5','expected_output_ops':17889637}
assert result['storage_untouched_closed_interval'];(r/'INSPECTION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
