"""Read-only complete stream audit while the frozen census runs separately."""
from pathlib import Path
import ctypes,ctypes.util,hashlib,json,resource,struct
resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3))
root=Path('/home/hclau/ecdsa_research');parent=root/'product-exact-20261015/tip/ops.bin';candidate=root/'seed-restore-20261016/candidate/ops.bin'
pins={parent:'2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e',candidate:'a996cf16d64b11a20cb9a56d0688d034153f843751f640ea7113f50739c20608'}
lib=ctypes.CDLL(ctypes.util.find_library('zstd'));lib.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];lib.ZSTD_decompress.restype=ctypes.c_size_t
def load(path):
 data=path.read_bytes();assert hashlib.sha256(data).hexdigest()==pins[path];n=struct.unpack_from('<Q',data,8)[0];assert n==11630716
 buf=ctypes.create_string_buffer(n*56);assert lib.ZSTD_decompress(buf,len(buf),data[16:],len(data)-16)==n*56;return buf.raw
a=load(parent);b=load(candidate);at=619000;none=2**64-1
assert struct.unpack_from('<7Q',a,at*56)==(8,none,1106,1134,none,none,none)
assert struct.unpack_from('<7Q',b,at*56)==(13,881,1106,1134,none,none,none)
assert a[:at*56]==b[:at*56] and a[(at+1)*56:]==b[(at+1)*56:]
depth=0
for op in struct.iter_unpack('<7Q',a[:at*56]):
 if op[0]==15:depth+=1
 elif op[0]==16:depth-=1
 assert depth>=0
assert depth==0
assert hashlib.sha256(b).hexdigest()=='e970dfabd655b2ff3dee1cd0121ffd88e2458f50097fd2487639e266976aec56'
for path,sha in pins.items():assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
out=dict(status='INDEPENDENT_EVERY_OPERATION_ONE_CONTROL_RESTORATION_PASS',source_sha256=pins[candidate],canonical_sha256=hashlib.sha256(b).hexdigest(),ops=11630716,changed_op=at,all_other_11630715_ops_byte_identical=True,changed_op_unconditional=True,exact_added_T_every_shot=1,all_physical_MR_classical_ABI_tail_positions_identical=True,no_census_or_candidate_changes=True)
(root/'seed-restore-20261016/ROOT_STREAM_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
