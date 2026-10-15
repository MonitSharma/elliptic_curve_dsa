from pathlib import Path
import ctypes as c,hashlib,json,time
root=Path(__file__).resolve().parent;old=root.parent/'simd-rails-20261015'
class Step(c.Structure):_fields_=[(s,c.c_uint32) for s in ['w','n0','n1','n2','nb','anchor']]
sb=(old/'steps.bin').read_bytes();db=(old/'denominator-pairs.bin').read_bytes();expected=(old/'reference-flags.bin').read_bytes()
steps=(Step*138).from_buffer_copy(sb);data=(c.c_uint64*(len(db)//8)).from_buffer_copy(db);out=(c.c_uint8*len(expected))()
def bind(path):
 fn=c.CDLL(str(path)).rail8_population;fn.argtypes=[c.POINTER(Step),c.c_size_t,c.POINTER(c.c_uint64),c.c_size_t,c.POINTER(c.c_uint8)];fn.restype=c.c_int;return fn
original=bind(old/'librail8.so');new=bind(root/'librail8_unrolled.so');times={k:[] for k in ['original','specialized']}
for trial in range(3):
 for name,fn in [('original',original),('specialized',new)]:
  start=time.perf_counter();assert fn(steps,138,data,len(expected),out)==0;elapsed=time.perf_counter()-start;assert bytes(out)==expected;times[name].append(elapsed)
# Reject unsupported tables rather than silently applying the pinned constants.
bad=(Step*138).from_buffer_copy(sb);bad[0].anchor^=1;assert new(bad,138,data,1,out)==3;assert new(steps,137,data,1,out)==1
# Partial vectors and adversarial denominators match the original C reference.
words=[]
for bit in range(256):words.extend([(1<<bit),((1<<256)-(1<<bit))%((1<<256)-4294968273)])
for x in [0,1,2,3,((1<<256)-4294968273)-1]:words.append(x)
pairs=b''.join(x.to_bytes(32,'little')+((x*17+5)%((1<<256)-4294968273)).to_bytes(32,'little') for x in words)
ptr=(c.c_uint64*(len(pairs)//8)).from_buffer_copy(pairs)
for count in [1,3,7,8,9,len(words)]:
 a=(c.c_uint8*count)();b=(c.c_uint8*count)();assert original(steps,138,ptr,count,a)==new(steps,138,ptr,count,b)==0;assert bytes(a)==bytes(b)
result={'status':'EXACT_ADVISORY_FLAGS_MATCH_FIXED_POPULATION','shots':len(expected),'trials':times,'best_us_per_shot':{k:min(v)*1e6/len(expected) for k,v in times.items()},'edge_inputs':len(words),'table_mismatch_and_partial_vectors_tested':True,'advisory_only':True,'direct_rejection':False,'library_sha256':hashlib.sha256((root/'librail8_unrolled.so').read_bytes()).hexdigest()}
(root/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
