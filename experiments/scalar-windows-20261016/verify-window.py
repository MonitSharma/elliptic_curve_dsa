from pathlib import Path
import concurrent.futures,ctypes as c,hashlib,json,sys,time
root=Path(__file__).resolve().parent;window=int(sys.argv[1]);lib=c.CDLL(str(root/'libscalar_windows.so'))
lib.scalar_fast_fixed_init.argtypes=[c.c_uint];lib.scalar_fast_fixed_init.restype=c.c_int
lib.scalar_fast_pairs.argtypes=[c.c_uint,c.c_void_p,c.c_void_p];lib.scalar_fast_pairs.restype=c.c_int
start=time.perf_counter();assert lib.scalar_fast_fixed_init(window)==1;startup=time.perf_counter()-start
fixture=root.parent/'scalar-fast-20261015/validation-vectors.tsv'
lines=[s.split() for s in fixture.read_text().splitlines()];assert len(lines)==4096 and all(len(r)==8 for r in lines)
for start in range(0,len(lines),64):
 rows=lines[start:start+64];inp=c.create_string_buffer(bytes.fromhex(''.join(''.join(r[:2]) for r in rows)));out=c.create_string_buffer(len(rows)*192)
 assert lib.scalar_fast_pairs(len(rows),inp,out)==1
 assert out.raw==bytes.fromhex(''.join(''.join(r[2:]) for r in rows))
def bench(worker):
 data=hashlib.shake_256(b'fixed-window-timing-20261016'+worker.to_bytes(4,'little')).digest(32768*64);out=c.create_string_buffer(64*192)
 start=time.perf_counter();checksum=0
 for pos in range(0,len(data),4096):
  inp=c.create_string_buffer(data[pos:pos+4096]);assert lib.scalar_fast_pairs(64,inp,out)==1;checksum+=out.raw[pos%len(out.raw)]
 return {'seconds':time.perf_counter()-start,'shots':32768,'checksum':checksum}
trials={}
for threads in [1,8]:
 rows=[]
 for trial in range(3):
  start=time.perf_counter()
  with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as pool:results=list(pool.map(bench,range(threads)))
  rows.append({'seconds':time.perf_counter()-start,'shots':32768*threads,'workers':results})
 trials[threads]=rows
report={'status':'EXACT_PROTECTED4096_PAIRS_PASS','window':window,'fixture_sha256':hashlib.sha256(fixture.read_bytes()).hexdigest(),'library_sha256':hashlib.sha256((root/'libscalar_windows.so').read_bytes()).hexdigest(),'startup_seconds':startup,'fresh_trials':trials,'nonce_search':False}
(root/f'window{window}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
