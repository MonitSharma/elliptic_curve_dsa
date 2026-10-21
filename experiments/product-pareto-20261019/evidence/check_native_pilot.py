import ctypes,ctypes.util,hashlib,json,struct
from pathlib import Path
root=Path(__file__).resolve().parent
receipt=json.loads((root/'parent4-native.json').read_text())
candidate=Path(receipt['candidate']);data=(candidate/'ops.bin').read_bytes()
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
n=struct.unpack_from('<Q',data,8)[0];buf=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(buf,n*56,data[16:],len(data)-16)==n*56
raw=buf.raw;digest=hashlib.sha3_256(raw).hexdigest();assert digest==receipt['expected_output_sha3_256']
no=(1<<64)-1;nq=0
for row in struct.iter_unpack('<7Q',raw):nq=max(nq,max((q+1 for q in row[1:4] if q!=no),default=0))
assert nq==1234
result={'status':'NATIVE_PILOT_BYTE_IDENTITY_PASS','peak_qubits':nq,'operations':n,'raw_sha3_256':digest,'stream_sha256':hashlib.sha256(data).hexdigest(),'not_a_scored_result':True}
(root/'NATIVE-PILOT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
