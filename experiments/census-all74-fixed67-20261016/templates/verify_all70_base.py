"""Compare full native canonical stream to original with only ALL70 gates restored."""
from pathlib import Path
import ctypes as c,hashlib,json,struct,subprocess
r=Path(__file__).resolve().parent;d=r/'all70-cache67-20261016';lib=c.CDLL('libzstd.so.1')
lib.ZSTD_decompress.argtypes=[c.c_void_p,c.c_size_t,c.c_void_p,c.c_size_t];lib.ZSTD_decompress.restype=c.c_size_t
def load(p):
 b=p.read_bytes();assert b[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',b,8)[0];o=c.create_string_buffer(n*56);assert lib.ZSTD_decompress(o,len(o),b[16:],len(b)-16)==len(o);return b,memoryview(o).cast('B')
old,raw=load(r/'tip/ops.bin');new,actual=load(r/'candidate-all70-base/ops.bin');assert len(raw)==len(actual)
rows=json.loads((r.parent/'census-control-family-20261016/ALL70.json').read_text());cursor=0
for e in rows:
 at=e['actual_index'];assert raw[cursor*56:at*56]==actual[cursor*56:at*56]
 assert bytes(raw[at*56:(at+1)*56])==struct.pack('<7Q',*e['new'])
 assert bytes(actual[at*56:(at+1)*56])==struct.pack('<7Q',*e['old']);cursor=at+1
assert raw[cursor*56:]==actual[cursor*56:]
tree=r/'candidate-all70-base';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();files={p.relative_to(tree/'src/point_add').as_posix():sha(p)for p in(tree/'src/point_add').rglob('*')if p.is_file()};assert files==json.loads((d/'base-source-files.json').read_text())
paths=subprocess.check_output(['git','-C',str(tree),'diff','--name-only','HEAD'],text=True).splitlines();assert paths==['src/point_add/census_cut.rs'];protected={}
for rel in subprocess.check_output(['git','-C',str(tree),'ls-files'],text=True).splitlines():
 if rel.startswith('src/point_add/'):continue
 data=(tree/rel).read_bytes();assert data==subprocess.check_output(['git','-C',str(tree),'show','HEAD:'+rel]);protected[rel]=hashlib.sha256(data).hexdigest()
result={'status':'FULL_NATIVE_ONLY_ALL70_ORIGINAL_CONTROLS_RESTORED_PASS','source_sha256':hashlib.sha256(new).hexdigest(),'ops':len(actual)//56,'parent_sha256':hashlib.sha256(old).hexdigest(),'restored':70,'untouched_other_records':True,'MR_classical_order_and_physical_positions_unchanged':True,'all74_deletions_retained':True,'pre_tail_sha3_256':hashlib.sha3_256(actual[:-96*56]).hexdigest(),'pre_tail_ops':len(actual)//56-96,'canonical_sha256':hashlib.sha256(actual).hexdigest(),'source_files_sha256':files,'protected_files_sha256':protected,'diff_paths':paths}
(d/'BASE_NATIVE_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
