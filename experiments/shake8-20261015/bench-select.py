import ctypes as c,json,os,time
from pathlib import Path
lib=c.CDLL(str(Path(os.environ.get('SHAKE8_LIB','libshake8.so')).resolve()))
lib.shake8_create.restype=c.c_void_p
lib.shake8_finalize.argtypes=[c.c_void_p]
lib.shake8_clone.argtypes=[c.c_void_p];lib.shake8_clone.restype=c.c_void_p
lib.shake8_free.argtypes=[c.c_void_p]
lib.shake8_select_words8.argtypes=[c.c_void_p,c.c_void_p,c.c_void_p,c.c_size_t]
p=lib.shake8_create();lib.shake8_finalize(p)
n=906156;out=(c.c_uint64*(8*n))()
for case,indices in [('same',[10]*8),('mixed',[1,5,7,14,10,3,21,8])]:
 offsets=(c.c_size_t*8)(*[i*n for i in indices]);samples=[]
 for rep in range(5):
  q=lib.shake8_clone(p);start=time.perf_counter()
  assert lib.shake8_select_words8(q,offsets,out,n)==0
  samples.append(time.perf_counter()-start);lib.shake8_free(q)
 print(json.dumps({'library':os.environ.get('SHAKE8_LIB','libshake8.so'),'case':case,'indices':indices,'seconds':samples,'best_s':min(samples)}),flush=True)
lib.shake8_free(p)
