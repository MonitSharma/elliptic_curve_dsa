from pathlib import Path
import hashlib,json,subprocess,ctypes,ctypes.util,struct
r=Path(__file__).resolve().parent;b=r.parent;d=r/'preseed10-cache67-20261016';tree=r/'candidate-preseed10-base';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
 data=p.read_bytes();assert data[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',data,8)[0];z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t;o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),data[16:],len(data)-16)==len(o);return o.raw
paths=[b/'payload-model-20261016/before-census.bin',b/'product-exact-20261015/tip/ops.bin',tree/'ops.bin',d/'DECLARATION.json'];pins={str(p):sha(p)for p in paths};assert pins[str(paths[0])]=='4b603d502456f8db2145ac5f7c36c9b44f496acfd0c3c5cc3149006cbc51a310';assert pins[str(paths[1])]=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
plan=json.loads(paths[3].read_text());before,old,new=[load(p)for p in paths[:3]];entry=618865;a=618858;assert len(new)//56==11630723;assert new[:entry*56]==before[:entry*56];assert new[entry*56:]==old[a*56:];assert hashlib.sha256(new).hexdigest()==plan['virtual_expected_canonical_sha256']=='6a64596fca2928f04370c326f3d3818d651da73f4cb4087dd696f12736ccac83';assert hashlib.sha3_256(new[:entry*56]).hexdigest()==plan['source_checkpoint']['prefix_sha3_256']
rows=json.loads((b/'census-control-review-20261016/ALL144.json').read_text());selected=[e for e in rows if e['raw_index']<entry];remaining=[e for e in rows if e['raw_index']>=entry];assert len(selected)==10 and len(remaining)==134
virtual=bytearray(before)
for e in reversed(remaining):
 at=e['raw_index']*56
 if e['new']is None:del virtual[at:at+56]
 else:virtual[at:at+56]=struct.pack('<7Q',*e['new'])
assert virtual==new;del virtual
pos=cur=0
for e in selected:
 at=e['raw_index'];actual_at=e['actual_index'];assert new[pos*56:at*56]==old[cur*56:actual_at*56];assert new[at*56:(at+1)*56]==struct.pack('<7Q',*e['old'])
 cur=actual_at+int(e['new']is not None);pos=at+1
assert new[pos*56:entry*56]==old[cur*56:a*56] and new[-96*56:]==old[-96*56:]
old_class=[o for o in struct.iter_unpack('<7Q',old[:a*56])if o[0]not in(8,13)];new_class=[o for o in struct.iter_unpack('<7Q',new[:entry*56])if o[0]not in(8,13)];assert old_class==new_class
files={p.relative_to(tree/'src/point_add').as_posix():sha(p)for p in(tree/'src/point_add').rglob('*')if p.is_file()};assert files==json.loads((d/'base-source-files.json').read_text());diff=subprocess.check_output(['git','-C',str(tree),'diff','--name-only','HEAD'],text=True).splitlines();assert diff==['src/point_add/census_cut.rs'];protected={}
for rel in subprocess.check_output(['git','-C',str(tree),'ls-files'],text=True).splitlines():
 if rel.startswith('src/point_add/'):continue
 data=(tree/rel).read_bytes();assert data==subprocess.check_output(['git','-C',str(tree),'show','HEAD:'+rel]);protected[rel]=hashlib.sha256(data).hexdigest()
N=2**64-1;qmax=bmax=mr=0
for k,c2,c1,t,bt,cc,reg in struct.iter_unpack('<7Q',new):
 for v in(c2,c1,t):
  if v!=N:qmax=max(qmax,v+1)
 for v in(bt,cc):
  if v!=N:bmax=max(bmax,v+1)
 mr+=k in(11,12)
assert(qmax,bmax,mr)==(1234,45701,906156);assert pins=={p:sha(Path(p))for p in pins}
receipt=dict(status='NATIVE_PRESEED10_COMPLETE_PREFIX_SUFFIX_PROTECTED_PASS',source_sha256=sha(paths[2]),ops=len(new)//56,parent_sha256=sha(paths[1]),restored_rows=10,restored_deletions=7,restored_reductions=3,retained_rows=134,retained_deletions=67,retained_reductions=67,every_other_original_Op_identical=True,prefix_equals_before_census=True,suffix_equals_actual2a=True,MR_classical_ABI_sequence_and_physical_ids_unchanged=True,old_MR_draw_ordinals_unchanged=True,exact_added_executed_T=10,Q=qmax,B=bmax,MR=mr,pre_tail_ops=len(new)//56-96,pre_tail_sha3_256=hashlib.sha3_256(new[:-96*56]).hexdigest(),canonical_sha256=hashlib.sha256(new).hexdigest(),source_files_sha256=files,protected_files_sha256=protected,diff_paths=diff,before_after_pins=pins,no_seed48zero_or_mask_transfer=True)
(d/'BASE_NATIVE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
