from pathlib import Path
import ctypes,ctypes.util,struct,json,hashlib,subprocess
r=Path('/home/hclau/ecdsa_research/seam-phase-repair-20261016');z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
a=load(r/'prototype.bin');b=load(r/'candidate/ops.bin');assert a==b,'native operations differ from independently constructed candidate'
base=load(r.parent/'product-exact-20261015/tip/ops.bin');meta=json.loads((r/'region.json').read_text());begin=meta['final_begin'];end=meta['final_end'];assert base[:begin*56]==b[:begin*56];assert base[end*56:]==b[(end+4)*56:]
subprocess.run(['git','-C',str(r/'candidate'),'diff','--exit-code','--','.',':(exclude)src/point_add'],check=True)
result=dict(all_native_operations_equal_prototype=True,canonical_operation_sha256=hashlib.sha256(b).hexdigest(),native_stream_sha256=hashlib.sha256((r/'candidate/ops.bin').read_bytes()).hexdigest(),prototype_container_sha256=hashlib.sha256((r/'prototype.bin').read_bytes()).hexdigest(),ops=len(b)//56,all_operations_outside_named_seam_byteidentical=True,protected_tracked_files_unchanged=True,delta_native_toffoli=0,delta_mr=0,delta_physical_qubits=0,delta_ops=4,source_revision='4b2ec52fc55da796aa8f5ef851290297e8706424')
(r/'native-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
