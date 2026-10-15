from pathlib import Path
import ctypes as c,hashlib,json,time,random,statistics
root=Path(__file__).resolve().parent;old=root.parent/'rail-masks-20261016';corpus=root.parent/'simd-rails-20261015'
class Step(c.Structure):_fields_=[(s,c.c_uint32) for s in ['w','n0','n1','n2','nb','anchor']]
sb=(corpus/'steps.bin').read_bytes();db=(corpus/'denominator-pairs.bin').read_bytes();expected=(corpus/'reference-flags.bin').read_bytes()
steps=(Step*138).from_buffer_copy(sb);data=(c.c_uint64*(len(db)//8)).from_buffer_copy(db)
def bind(path):
 lib=c.CDLL(str(path));fn=lib.rail8_population;fn.argtypes=[c.POINTER(Step),c.c_size_t,c.POINTER(c.c_uint64),c.c_size_t,c.POINTER(c.c_uint8)];fn.restype=c.c_int;return lib,fn
base,original=bind(old/'librail8_masks.so');lib,new=bind(root/'librail8_tail64.so')
lib.rail8_tail_first.argtypes=[c.POINTER(Step),c.c_size_t];lib.rail8_tail_first.restype=c.c_int
first=lib.rail8_tail_first(steps,138);assert first==json.loads((root/'SOURCE_PLAN.json').read_text())['first_tick']
out=(c.c_uint8*len(expected))();times={k:[] for k in ['frozen046dd','tail64']}
for trial in range(3):
 for name,fn in [('frozen046dd',original),('tail64',new)]:
  start=time.perf_counter();assert fn(steps,138,data,len(expected),out)==0;elapsed=time.perf_counter()-start;assert bytes(out)==expected;times[name].append(elapsed)
words=[];p=(1<<256)-4294968273
for bit in range(256):words.extend([(1<<bit),((1<<256)-(1<<bit))%p])
words.extend([0,1,2,3,p-1]);assert len(words)==517
pairs=b''.join(x.to_bytes(32,'little')+((x*17+5)%p).to_bytes(32,'little') for x in words);ptr=(c.c_uint64*(len(pairs)//8)).from_buffer_copy(pairs)
checked=[]
def compare(tab,n,ptr,count,label):
 a=(c.c_uint8*count)();b=(c.c_uint8*count)();ra=original(tab,n,ptr,count,a);rb=new(tab,n,ptr,count,b);assert (ra,bytes(a))==(rb,bytes(b)),label;checked.append({'label':label,'count':count,'return_code':ra})
for count in [1,3,7,8,9,len(words)]:compare(steps,138,ptr,count,'edge-partial-'+str(count))
bad=(Step*138).from_buffer_copy(sb);bad[0].anchor^=1;compare(bad,138,data,1,'old-mutated-anchor')
# Valid nonmonotone widths exercise conservative transition/fallback decisions.
for index in [first,137]:
 tab=(Step*138).from_buffer_copy(sb);tab[index].n0=62;compare(tab,138,ptr,517,'wide-suffix-'+str(index));assert lib.rail8_tail_first(tab,138)>index
tab=(Step*138).from_buffer_copy(sb);tab[137].anchor=319;compare(tab,138,ptr,517,'large-anchor')
for n in [1,2,17,first,first+1,137]:compare(steps,n,ptr,517,'prefix-table-length-'+str(n))
for field,value in [('w',0),('w',320),('n0',1),('nb',3),('anchor',320)]:
 tab=(Step*138).from_buffer_copy(sb);setattr(tab[first],field,value);compare(tab,138,data,1,'invalid-'+field+'-'+str(value))
compare(steps,0,data,1,'empty-table')
# Direct arbitrary-sign state induction checks: every possible suffix start,
# both divide/fused and multiply branches, extremes at signed-width boundaries.
test=lib.rail8_test_suffix;test.argtypes=[c.POINTER(Step),c.c_size_t,c.c_size_t,c.POINTER(c.c_uint64),c.POINTER(c.c_uint64),c.c_int,c.c_int];test.restype=c.c_int
rng=random.Random(0x7261696c3634);suffix_cases=0;mask=(1<<64)-1
for tick in range(first,138):
 w=steps[tick].w;lo=-(1<<(w-1));hi=(1<<(w-1))-1
 for iteration in range(32):
  vals=[lo,hi,-1,0,1 if hi else 0]+[rng.randint(lo,hi) for _ in range(11)]
  rng.shuffle(vals);ins=(c.c_uint64*16)(*(x&mask for x in vals));a=(c.c_uint64*16)();b=(c.c_uint64*16)()
  for divide in [0,1]:
   ra=test(steps,138,tick,ins,a,divide,0);rb=test(steps,138,tick,ins,b,divide,1);assert (ra,bytes(a))==(rb,bytes(b)),('suffix-state',tick,iteration,divide);suffix_cases+=1
# Negative control: a deliberately incorrect flag must be detected by the
# exact same full-population equality comparison, without changing a circuit.
assert new(steps,138,data,len(expected),out)==0
wrong=bytearray(out);wrong[0]^=1;assert bytes(wrong)!=expected
result={'status':'EXACT_ADVISORY_FLAGS_AND_SUFFIX_STATE_PASS','shots':len(expected),'trials_seconds':times,'median_us_per_shot':{k:statistics.median(v)*1e6/len(expected) for k,v in times.items()},'relative_median_speedup':statistics.median(times['frozen046dd'])/statistics.median(times['tail64']),'edge_inputs':len(words),'control_checks':checked,'arbitrary_sign_packed_suffix_cases':suffix_cases,'arbitrary_sign_lanes':suffix_cases*8,'negative_flag_comparison_control':True,'first_narrow_tick':first,'advisory_only':True,'production_replacement':False,'baseline_library_sha256':hashlib.sha256((old/'librail8_masks.so').read_bytes()).hexdigest(),'library_sha256':hashlib.sha256((root/'librail8_tail64.so').read_bytes()).hexdigest(),'corpus_sha256':{s:hashlib.sha256((corpus/s).read_bytes()).hexdigest() for s in ['steps.bin','denominator-pairs.bin','reference-flags.bin']}}
(root/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
