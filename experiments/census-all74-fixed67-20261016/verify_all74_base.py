"""Native bytes must equal pre-census bytes with only the70 reductions applied."""
from pathlib import Path
import ctypes as c,hashlib,json,struct,subprocess
r=Path(__file__).resolve().parent;b=r.parent;d=r/'all74-cache67-20261016';tree=r/'candidate-all74-base';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();lib=c.CDLL('libzstd.so.1');lib.ZSTD_decompress.argtypes=[c.c_void_p,c.c_size_t,c.c_void_p,c.c_size_t];lib.ZSTD_decompress.restype=c.c_size_t
def load(p):
 data=p.read_bytes();assert data[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',data,8)[0];out=c.create_string_buffer(n*56);assert lib.ZSTD_decompress(out,len(out),data[16:],len(data)-16)==len(out);return out.raw
before_path=b/'payload-model-20261016/before-census.bin';parent_path=b/'product-exact-20261015/tip/ops.bin';candidate=tree/'ops.bin';rows_path=b/'census-control-review-20261016/ALL144.json';pins={str(p):sha(p)for p in[before_path,parent_path,candidate,rows_path]};assert pins[str(before_path)]=='4b603d502456f8db2145ac5f7c36c9b44f496acfd0c3c5cc3149006cbc51a310';assert pins[str(parent_path)]=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
raw=load(before_path);actual=load(candidate);old=load(parent_path);assert len(raw)==len(actual)==(len(old)//56+74)*56;rows=json.loads(rows_path.read_text());cursor=0;nd=nr=0;previous=0
for e in rows:
 at=e['raw_index'];assert struct.unpack_from('<7Q',raw,at*56)==tuple(e['old']);assert raw[cursor*56:at*56]==actual[cursor*56:at*56]
 if e['new']is None:assert actual[at*56:(at+1)*56]==struct.pack('<7Q',*e['old']);nd+=1
 else:assert actual[at*56:(at+1)*56]==struct.pack('<7Q',*e['new']);nr+=1
 cursor=at+1
assert raw[cursor*56:]==actual[cursor*56:] and(nd,nr)==(74,70);assert actual[-96*56:]==old[-96*56:]
# Independent complete direct diff against final original, with explicit inserted74 original CCXs.
pos=cur=0
for e in rows:
 at=e['raw_index'];actual_at=e['actual_index'];assert actual[pos*56:at*56]==old[cur*56:actual_at*56]
 if e['new']is None:assert actual[at*56:(at+1)*56]==struct.pack('<7Q',*e['old']);cur=actual_at
 else:assert actual[at*56:(at+1)*56]==old[actual_at*56:(actual_at+1)*56];cur=actual_at+1
 pos=at+1
assert actual[pos*56:]==old[cur*56:]
files={p.relative_to(tree/'src/point_add').as_posix():sha(p)for p in(tree/'src/point_add').rglob('*')if p.is_file()};assert files==json.loads((d/'base-source-files.json').read_text());paths=subprocess.check_output(['git','-C',str(tree),'diff','--name-only','HEAD'],text=True).splitlines();assert paths==['src/point_add/census_cut.rs'];protected={}
for rel in subprocess.check_output(['git','-C',str(tree),'ls-files'],text=True).splitlines():
 if rel.startswith('src/point_add/'):continue
 data=(tree/rel).read_bytes();assert data==subprocess.check_output(['git','-C',str(tree),'show','HEAD:'+rel]);protected[rel]=hashlib.sha256(data).hexdigest()
N=2**64-1;qmax=bmax=mr=0
for k,c2,c1,t,bt,cc,reg in struct.iter_unpack('<7Q',actual):
 for v in [c2,c1,t]:
  if v!=N:qmax=max(qmax,v+1)
 for v in [bt,cc]:
  if v!=N:bmax=max(bmax,v+1)
 mr+=k in(11,12)
assert(qmax,bmax,mr)==(1234,45701,906156);assert pins=={p:sha(Path(p))for p in pins}
receipt=dict(status='FULL_NATIVE_ONLY_ALL74_ORIGINAL_DELETED_CCX_RESTORED_PASS',source_sha256=sha(candidate),ops=len(actual)//56,parent_sha256=sha(parent_path),restored=74,all70_reductions_retained=True,every_other_original_Op_identical=True,MR_classical_ABI_order_and_physical_ids_preserved=True,old_MR_draw_ordinals_unchanged=True,physical_Op_offsets_shift_by_insertions=True,Q=qmax,B=bmax,MR=mr,pre_tail_sha3_256=hashlib.sha3_256(actual[:-96*56]).hexdigest(),pre_tail_ops=len(actual)//56-96,canonical_sha256=hashlib.sha256(actual).hexdigest(),source_files_sha256=files,protected_files_sha256=protected,diff_paths=paths,before_after_pins=pins)
(d/'BASE_NATIVE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
