import ctypes as c, hashlib, random, struct, time
from pathlib import Path
lib=c.CDLL(str(Path('libshake8.so').resolve()))
lib.shake8_create.restype=c.c_void_p
lib.shake8_clone.argtypes=[c.c_void_p];lib.shake8_clone.restype=c.c_void_p
lib.shake8_free.argtypes=[c.c_void_p]
lib.shake8_absorb_same.argtypes=[c.c_void_p,c.c_void_p,c.c_size_t]
lib.shake8_absorb8.argtypes=[c.c_void_p,c.c_void_p,c.c_size_t,c.c_size_t]
lib.shake8_finalize.argtypes=[c.c_void_p]
lib.shake8_squeeze8.argtypes=[c.c_void_p,c.c_void_p,c.c_size_t,c.c_size_t]
lib.shake8_words8.argtypes=[c.c_void_p,c.c_void_p,c.c_size_t]
lib.shake8_select_words8.argtypes=[c.c_void_p,c.c_void_p,c.c_void_p,c.c_size_t]
r=random.Random(20261015);checks=0
for prefix_n in [0,1,7,8,135,136,137,271,272,273,4096,65536]:
 for tail_n in [0,1,7,8,135,136,137,4704]:
  prefix=r.randbytes(prefix_n);tails=[r.randbytes(tail_n) for _ in range(8)]
  p=lib.shake8_create();assert p
  assert lib.shake8_absorb_same(p,prefix,len(prefix))==0
  q=lib.shake8_clone(p);lib.shake8_free(p);p=q
  assert lib.shake8_absorb8(p,b''.join(tails),tail_n,tail_n)==0
  assert lib.shake8_finalize(p)==0
  expected=[hashlib.shake_256(prefix+t).digest(8192) for t in tails]
  selected=lib.shake8_clone(p)
  offsets=[0,1,7,16,17,18,135,271];offs=(c.c_size_t*8)(*offsets)
  selected_out=(c.c_uint64*(8*500))()
  assert lib.shake8_select_words8(selected,offs,selected_out,500)==0
  for i in range(8):
   raw=b''.join(struct.pack('<Q',selected_out[j*8+i]) for j in range(500))
   assert raw==expected[i][offsets[i]*8:(offsets[i]+500)*8]
  checks+=8;lib.shake8_free(selected)
  at=0
  for n in [1,7,127,1,136,272,8]:
   out=c.create_string_buffer(n*8)
   assert lib.shake8_squeeze8(p,out,n,n)==0
   for i in range(8):assert out.raw[i*n:(i+1)*n]==expected[i][at:at+n],(prefix_n,tail_n,i,at)
   at+=n;checks+=8
  assert at%8==0
  out=(c.c_uint64*(8*700))();assert lib.shake8_words8(p,out,700)==0
  for i in range(8):
   raw=b''.join(struct.pack('<Q',out[j*8+i]) for j in range(700))
   assert raw==expected[i][at:at+5600]
  checks+=8;lib.shake8_free(p)
print(f'HASHLIB_VERIFIED checks={checks} SHAKE256_24rounds=true partial_clone_boundary_interleaved=true')
p=lib.shake8_create();lib.shake8_absorb_same(p,b'benchmark',9);lib.shake8_finalize(p)
n=1000000;out=(c.c_uint64*(8*n))();start=time.perf_counter()
lib.shake8_words8(p,out,n);elapsed=time.perf_counter()-start
print(f'WORDS8 bytes={8*8*n} elapsed_s={elapsed:.6f} MBps={64*n/elapsed/1e6:.3f} per_nonce_ms={elapsed*1000/8:.3f}')
lib.shake8_free(p)
