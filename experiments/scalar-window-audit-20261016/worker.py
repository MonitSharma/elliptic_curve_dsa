import ctypes, hashlib, json, os, resource, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'scalar-fast-20261015'
LIB=BASE/'libscalar_fast_batch.so'
CORPUS=BASE/'validation-vectors.tsv'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(LIB)=='3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f'
assert sha(CORPUS)=='ce17d7cdbbdbea6838462cf09d02cb56ae98c532671486fa3aa499fc7a95237d'
window,trial=map(int,sys.argv[1:])
assert window in (13,16,18,20) and 0<=trial<3
rows=[list(map(bytes.fromhex,line.split())) for line in CORPUS.read_text().splitlines()]
assert len(rows)==4096 and all(len(r)==8 and all(len(v)==32 for v in r) for r in rows)
inputs=b''.join(b''.join(r[:2]) for r in rows)
expected=b''.join(b''.join(r[2:]) for r in rows)
source=ctypes.create_string_buffer(inputs)
out=ctypes.create_string_buffer(len(expected))
lib=ctypes.CDLL(str(LIB))
lib.scalar_fast_fixed_init.argtypes=[ctypes.c_uint]
lib.scalar_fast_fixed_init.restype=ctypes.c_int
lib.scalar_fast_pairs.argtypes=[ctypes.c_uint,ctypes.c_void_p,ctypes.c_void_p]
lib.scalar_fast_pairs.restype=ctypes.c_int
def rss():
 return int(next(x.split()[1] for x in Path('/proc/self/status').read_text().splitlines() if x.startswith('VmRSS:')))*1024
rss_before=rss(); start=time.perf_counter_ns()
assert lib.scalar_fast_fixed_init(window)==1
init_ns=time.perf_counter_ns()-start; rss_after=rss()
assert lib.scalar_fast_fixed_init(window)==0, 'second initialization must reject'
calls=[(ctypes.addressof(source)+i*64,ctypes.addressof(out)+i*192) for i in range(0,4096,64)]
def run():
 for src,dst in calls: assert lib.scalar_fast_pairs(64,src,dst)==1
run(); assert out.raw[:len(expected)]==expected
controls=[]
for count in (0,1,7,63,64):
 for start in (0,4096-64):
  small=ctypes.create_string_buffer(64*192+16); ctypes.memset(small,0xa5,len(small))
  assert lib.scalar_fast_pairs(count,ctypes.addressof(source)+start*64,small)==1
  assert small.raw[:count*192]==expected[start*192:(start+count)*192]
  assert small.raw[count*192:]==bytes([0xa5])*(len(small)-count*192)
  controls.append([start,count])
small=ctypes.create_string_buffer(bytes([0xa5])*(64*192+16))
before=small.raw
assert lib.scalar_fast_pairs(65,source,small)==0 and small.raw==before
assert lib.scalar_fast_pairs(2**32-1,source,small)==0 and small.raw==before
passes=[]
for repeat in range(32):
 start=time.perf_counter_ns(); run(); passes.append(time.perf_counter_ns()-start)
 # Complete equality is checked outside every measured loop, not a checksum substitute.
 assert out.raw[:len(expected)]==expected, (window,trial,repeat)
data=out.raw[:len(expected)]
output=ROOT/f'output-{trial}-{window}.bin'; output.write_bytes(data)
result={'window':window,'trial':trial,'pairs':4096*32,'passes':32,'batch':64,
 'call_loop_ns':sum(passes),'pass_ns':passes,'us_per_pair':sum(passes)/1000/(4096*32),
 'init_ns':init_ns,'rss_before_bytes':rss_before,'rss_after_init_bytes':rss_after,
 'max_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
 'nominal_table_bytes':((256+window-1)//window)*(1<<window)*64,
 'coordinate_checks':4096*6*33,'partial_empty_controls':controls,'invalid_count_controls':[65,2**32-1],
 'output_sha256':hashlib.sha256(data).hexdigest(),'lib_sha256':sha(LIB),'corpus_sha256':sha(CORPUS),
 'timing_scope':'32 fixed corpus call loops; excludes equality checks, parsing, allocation and initialization; includes Python C-call loop overhead',
 'authority':False}
(ROOT/f'trial-{trial}-{window}.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
