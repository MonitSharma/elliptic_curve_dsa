"""WIDE95 native port: bind the frozen exact 95-stage wide cache output to the untouched 5a7c3902 pre-tail prefix."""
from pathlib import Path
import ctypes,ctypes.util,hashlib,json,shutil,struct,subprocess,time
root=Path('/home/hclau/ecdsa_research/wide95-native-20261017')
base='5a7c390233c72133df9b591c92e43422c5892142'
up=root.parent/'product-exact-20261015'
freeze=json.loads((up/'WIDE95_FREEZE.json').read_text())
parent=root.parent/'nonce-screen-20261015/final-census/ops.bin';final=up/freeze['external_stream']
assert hashlib.sha256(final.read_bytes()).hexdigest()==freeze['external_stream_sha256']
z=ctypes.CDLL(ctypes.util.find_library('zstd'))
z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
z.ZSTD_isError.argtypes=[ctypes.c_size_t];z.ZSTD_isError.restype=ctypes.c_uint
z.ZSTD_compressBound.argtypes=[ctypes.c_size_t];z.ZSTD_compressBound.restype=ctypes.c_size_t
z.ZSTD_createCCtx.restype=ctypes.c_void_p
z.ZSTD_CCtx_setParameter.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int];z.ZSTD_CCtx_setParameter.restype=ctypes.c_size_t
z.ZSTD_compress2.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_compress2.restype=ctypes.c_size_t
z.ZSTD_freeCCtx.argtypes=[ctypes.c_void_p]
def decode(path):
 data=path.read_bytes();assert data[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',data,8)[0];assert n<30_000_000
 out=ctypes.create_string_buffer(n*56);compressed=data[16:];size=z.ZSTD_decompress(out,len(out),compressed,len(compressed));assert not z.ZSTD_isError(size) and size==n*56
 raw=out.raw
 for i in range(n-96,n):
  row=struct.unpack_from('<7Q',raw,i*56);assert row[0]==6 and row[3] in [0,1] and all(row[j]==2**64-1 for j in [1,2,4,5,6])
  if (i-(n-96))%2:assert raw[(i-1)*56:i*56]==raw[i*56:(i+1)*56]
 return n,raw
pn,pr=decode(parent);input_hash=hashlib.sha3_256(pr[:-96*56]).hexdigest();del pr
assert pn-96==10517907 and input_hash=='fb4704b5f36d9c9d2544c14a46bd661deacf7349b4340c489df6f8809e0e645a'
fn,fr=decode(final);assert fn==freeze['resources']['ops']
assert fn-96==10548051 and hashlib.sha3_256(fr[:-96*56]).hexdigest()=='ec708207333b4a9574f16d2894269c8c1ec1d2c61a5b55e6adbfaf77770e6599'
context=z.ZSTD_createCCtx();assert context
for param,value in [(100,19),(101,27)]:assert not z.ZSTD_isError(z.ZSTD_CCtx_setParameter(context,param,value))
bound=z.ZSTD_compressBound(len(fr));out=ctypes.create_string_buffer(bound)
start=time.time();size=z.ZSTD_compress2(context,out,bound,fr,len(fr));assert not z.ZSTD_isError(size);z.ZSTD_freeCCtx(context)
blob=b'QECCOPSZ'+struct.pack('<Q',fn)+out.raw[:size]
compressed_path=root/'frozen_cache_wide95.bin';compressed_path.write_bytes(blob)
del fr,out,blob
tree=root/'candidate';assert not tree.exists()
subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','add','--detach',str(tree),base],check=True)
dest=tree/'src/point_add';shutil.copy2(compressed_path,dest/'frozen_cache_wide95.bin')
template=(root/'frozen_cache.rs.in').read_text()
for key,value in {'@INPUT_COUNT@':str(pn-96),'@OUTPUT_COUNT@':str(fn),'@INPUT_SHA3@':input_hash,'@BLOB_SHA3@':hashlib.sha3_256(compressed_path.read_bytes()).hexdigest()}.items():template=template.replace(key,value)
(dest/'frozen_cache_wide95.rs').write_text(template)
p=dest/'mod.rs';source=p.read_text();needle='    let nonce: u64 = required_env("TAIL_NONCE");';assert source.count(needle)==1
p.write_text(source.replace(needle,'    ops = frozen_cache_wide95::run(ops);\n'+needle)+'\nmod frozen_cache_wide95;\n')
subprocess.run(['git','-C',str(tree),'add','--intent-to-add','src/point_add/frozen_cache_wide95.rs','src/point_add/frozen_cache_wide95.bin'],check=True)
(root/'candidate-text.patch').write_bytes(subprocess.check_output(['git','-C',str(tree),'diff','HEAD','--','src/point_add']))
protected={}
for rel in subprocess.check_output(['git','-C',str(tree),'ls-files'],text=True).splitlines():
 if rel.startswith('src/point_add/'):continue
 data=(tree/rel).read_bytes();assert data==subprocess.check_output(['git','-C',str(tree),'show','HEAD:'+rel]);protected[rel]=hashlib.sha256(data).hexdigest()
(root/'protected.json').write_text(json.dumps(protected,indent=2)+'\n')
record={'status':'prepared_wide95_native_port_not_scored','base_revision':base,'exact_transform_source_freeze':freeze,'input_prefix_ops':pn-96,'input_prefix_sha3_256':input_hash,'frozen_full_ops':fn,'output_prefix_ops':fn-96,'blob_sha256':hashlib.sha256(compressed_path.read_bytes()).hexdigest(),'blob_sha3_256':hashlib.sha3_256(compressed_path.read_bytes()).hexdigest(),'compressed_blob_bytes':compressed_path.stat().st_size,'compression_seconds':time.time()-start,'expected_normal_generated_stream_sha256':freeze['external_stream_sha256'],'nonce_search_performed':False,'submission_mode':'queue','scope':'Store exact pre-tail cache output; bind original pre-cache input prefix; retain original nonce construction after table. No packet-dependent content or gates changed.'}
(root/'DECLARATION.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='exact_transform_source_freeze'},indent=2))
