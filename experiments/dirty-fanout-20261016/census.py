from pathlib import Path
import ctypes as C,ctypes.util,hashlib,json,struct,collections,time
root=Path(__file__).resolve().parent;base=root.parent
sources=[
 ('original4b',base/'product-exact-20261015/tip/ops.bin','2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'),
 ('product25',base/'product-exact-20261015/candidate-product-final25/ops.bin','180af069679ffa33b099b200d3337d6fc6c20a451a72508a40dea6617150dc64'),
 ('product67',base/'product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin','268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d'),
 ('public5a',base/'nonce-screen-20261015/final-census/ops.bin','01aad987cfe03e7ca97df6f3dcd26085a21a5836aa6e661ec8fbd9c9c1b63740')]
lib=C.CDLL(ctypes.util.find_library('zstd'));lib.ZSTD_decompress.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t];lib.ZSTD_decompress.restype=C.c_size_t;lib.ZSTD_isError.argtypes=[C.c_size_t];lib.ZSTD_isError.restype=C.c_uint
result=[]
for name,path,expected in sources:
 if not path.exists():
  result.append({'source':name,'status':'SOURCE_PATH_MISSING_NOT_SCANNED','path':str(path)});continue
 t=time.monotonic();raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
 assert raw[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',raw,8)[0];assert n<20000000
 data=C.create_string_buffer(n*56);compressed=raw[16:];size=lib.ZSTD_decompress(data,n*56,compressed,len(compressed));assert not lib.ZSTD_isError(size) and size==n*56
 del raw,compressed
 groups=[];current=[];key=None;depth=0;hist=collections.Counter();ccx=0
 def finish():
  global current,key
  if len(current)>=3:
   controls=set(key[:2]);targets={target for _,target in current}
   assert not controls&targets
   # Existing donor0..1233 is enough for every original/product circuit;
   # public5a may have a larger register but cannot need a new qubit here.
   donor=next((q for q in range(1234) if q not in controls|targets),None)
   if donor is not None:groups.append({'first_op':current[0][0],'last_op':current[-1][0],'ccx_count':len(current),'controls':list(key[:2]),'classical_guard':key[2],'depth':key[3],'targets':[target for _,target in current],'dirty_donor':donor,'unconditional_T_delta':2-len(current),'fair_guard_expected_saving':(len(current)-2)*2.0**(-key[3]-(key[2]!=(2**64-1)))})
  current=[];key=None
 for index,(kind,a,b,target,bt,condition,reg) in enumerate(struct.iter_unpack('<7Q',data)):
  assert kind<=17
  if kind==13:
   ccx+=1;new=(*sorted((a,b)),condition,depth)
   if key!=new:finish();key=new
   current.append((index,target))
  else:
   finish()
   if kind==15:depth+=1
   elif kind==16:depth-=1;assert depth>=0
 finish();assert depth==0
 for group in groups:hist[group['ccx_count']]+=1
 row={'source':name,'path':str(path),'sha256':expected,'ops':n,'ccx':ccx,'groups':groups,'group_count':len(groups),'histogram':dict(hist),'total_unconditional_saving_upper_bound':sum(-g['unconditional_T_delta'] for g in groups),'fair_guard_saving_diagnostic':sum(g['fair_guard_expected_saving'] for g in groups),'seconds':time.monotonic()-t,'status':'SOURCE_CENSUS_ONLY_NO_TRANSFORM'}
 result.append(row);print(json.dumps({k:v for k,v in row.items() if k!='groups'}),flush=True);del data
(root/'RESULT.json').write_text(json.dumps({'status':'TERMINAL_READ_ONLY_SOURCE_CENSUS','sources':result,'nonce_selected':None,'candidate_changed':False},indent=2)+'\n')
