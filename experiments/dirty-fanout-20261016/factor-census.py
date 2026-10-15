from pathlib import Path
import ctypes as C,ctypes.util,hashlib,json,struct,time
root=Path(__file__).resolve().parent;base=root.parent;nil=2**64-1
sources=[('original4b','product-exact-20261015/tip/ops.bin','2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'),('product25','product-exact-20261015/candidate-product-final25/ops.bin','180af069679ffa33b099b200d3337d6fc6c20a451a72508a40dea6617150dc64'),('product67','product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin','268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d'),('public5a','nonce-screen-20261015/final-census/ops.bin','01aad987cfe03e7ca97df6f3dcd26085a21a5836aa6e661ec8fbd9c9c1b63740')]
lib=C.CDLL(ctypes.util.find_library('zstd'));lib.ZSTD_decompress.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t];lib.ZSTD_decompress.restype=C.c_size_t;lib.ZSTD_isError.argtypes=[C.c_size_t];lib.ZSTD_isError.restype=C.c_uint
results=[]
for name,relative,sha in sources:
 path=base/relative;t=time.monotonic();raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==sha and raw[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',raw,8)[0];assert n<20000000
 data=C.create_string_buffer(n*56);compressed=raw[16:];size=lib.ZSTD_decompress(data,n*56,compressed,len(compressed));assert not lib.ZSTD_isError(size) and size==n*56;del raw,compressed
 writes=[-1]*16384;reads=[-1]*16384;bitwrites={};active={};pairs=[];disjoint=[];lastend=-1;depth=0
 for i,(kind,a,b,target,bt,condition,reg) in enumerate(struct.iter_unpack('<7Q',data)):
  if kind==13 and depth==0:
   candidates=[]
   for shared,other in [(a,b),(b,a)]:
    key=(target,shared,condition);previous=active.get(key)
    if previous:
     p,oldother,version=previous
     if writes[shared]<=p and writes[oldother]<=p and reads[target]<=p and version==bitwrites.get(condition,-1):
      candidates.append({'first_op':p,'last_op':i,'target':target,'shared':shared,'old_other':oldother,'new_other':other,'guard':condition,'T_saved_if_active':2 if oldother==other else 1,'fair_guard_saving_diagnostic':(2 if oldother==other else 1)*(1 if condition==nil else .5)})
    active[key]=(i,other,bitwrites.get(condition,-1))
   if candidates:
    chosen=min(candidates,key=lambda r:(r['first_op'],r['shared']));pairs.append(chosen)
    if chosen['first_op']>lastend:disjoint.append(chosen);lastend=i
  # Explicit controls are reads. XOR targets commute with a deferred toggle;
  # reset/measurement/swap targets and phase targets do not.
  if kind in [8,9,10,13,14]:
   for q in [a,b]:
    if q!=nil:reads[q]=i
  if kind in [7,9,14,11,12,10]:
   if target!=nil:reads[target]=i
  if kind in [6,8,10,11,12,13]:
   if target!=nil:writes[target]=i
  if kind==10:writes[b]=i
  if kind in [3,4,5,12]:bitwrites[bt]=i
  if kind==15:depth+=1
  elif kind==16:depth-=1;assert depth>=0
 assert depth==0
 row={'source':name,'source_sha256':sha,'ops':n,'potential_pairs':len(pairs),'greedy_disjoint_pairs':len(disjoint),'greedy_fair_guard_saving_diagnostic':sum(p['fair_guard_saving_diagnostic'] for p in disjoint),'greedy_pairs':disjoint,'first100_potential_pairs':pairs[:100],'seconds':time.monotonic()-t,'status':'SOURCE_ONLY_NOT_TRANSFORMED'}
 results.append(row);print(json.dumps({k:v for k,v in row.items() if k not in ['greedy_pairs','first100_potential_pairs']}),flush=True);del data,active,pairs
(root/'FACTOR-RESULT.json').write_text(json.dumps({'status':'READ_ONLY_FACTOR_PAIR_CENSUS_COMPLETE','sources':results,'candidate_changed':False,'nonce_selected':None},indent=2)+'\n')
