import ctypes,ctypes.util,hashlib,json,struct
from pathlib import Path
R=Path(__file__).resolve().parent;B=R.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=B/'product-exact-20261015/tip/ops.bin';new=B/'product-exact-20261015/candidate-all70-base/ops.bin'
assert sha(old)=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
expected='06cdc5de3dadbe23a2ff306466ec2ef27514bed53be1145ec83bdf490cb99a7a';assert sha(new)==expected
inventory=B/'all70-value-transfer-20261016/provenance/ALL70.json';assert sha(inventory)=='453e32f606d5dfaabbf12b4c7714c1cc986c5a6bdd534de3c76b123837d977d7'
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 b=p.read_bytes();assert b[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',b,8)[0];assert n==11630716
 out=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(out,len(out),b[16:],len(b)-16)==len(out);return out
a=load(old);b=load(new);rows=json.loads(inventory.read_text());assert len(rows)==70
for row in rows:
 at=row['actual_index']*56;assert list(struct.unpack('<7Q',ctypes.string_at(ctypes.addressof(a)+at,56)))==row['new']
 ctypes.memmove(ctypes.addressof(a)+at,struct.pack('<7Q',*row['old']),56)
libc=ctypes.CDLL(None);libc.memcmp.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t];libc.memcmp.restype=ctypes.c_int
assert libc.memcmp(a,b,len(a))==0, 'complete canonical stream differs outside70specifiedrestorations'
parent=B/'product-exact-20261015/all70-cache67-20261016/BASE_NATIVE_RECEIPT.json'
assert(B/'product-exact-20261015/all70-cache67-20261016/base-launcher.exit').read_text().strip()=='0'
(R/'BASE_NATIVE_RECEIPT.json').write_bytes(parent.read_bytes())
assert sha(new)==expected and sha(old)=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
binding={'status':'INDEPENDENT_FULL_CANONICAL_ALL70_BASE_BINDING_PASS','stream_path':str(new),'stream_sha256':expected,'operation_count':11630716,
 'original_stream_sha256':sha(old),'all70_inventory_sha256':sha(inventory),'native_receipt_sha256':sha(parent),
 'full_canonical_bytes_checked':11630716*56,'only70specifiedrestorations':True,'other_all_records_identical':True,
 'native_source_receipt_path':str(parent),'authority':False}
(R/'BASE-BINDING.json').write_text(json.dumps(binding,indent=2)+'\n');print(json.dumps(binding),flush=True)
