from pathlib import Path
import ctypes as c,hashlib,json,random
root=Path(__file__).resolve().parent
class Step(c.Structure):_fields_=[(s,c.c_uint32) for s in ['w','n0','n1','n2','nb','anchor']]
def bind(name):
 lib=c.CDLL(str(root/name));fn=lib.rail8_test_suffix;fn.argtypes=[c.POINTER(Step),c.c_size_t,c.c_size_t,c.POINTER(c.c_uint64),c.POINTER(c.c_uint64),c.c_int,c.c_int];fn.restype=c.c_int;return fn
good=bind('librail8_tail64.so');bad=bind('librail8_tail64_wrongshift.so');rng=random.Random(0x6172626974726172);mask=(1<<64)-1;checks=0;negative_mismatches=0
for w in range(1,62):
 for anchor in [0,61,319]:
  # Every suffix row is safe, with the widest possible legal narrow bounds.
  steps=(Step*4)(*(Step(w,max(w,2),max(w,2),max(w,2),max(w,4),anchor) for _ in range(4)))
  lo=-(1<<(w-1));hi=(1<<(w-1))-1
  vals=[lo,hi,-1,0]+[rng.randint(lo,hi) for _ in range(12)]
  ins=(c.c_uint64*16)(*(x&mask for x in vals));a=(c.c_uint64*16)();b=(c.c_uint64*16)();fault=(c.c_uint64*16)()
  for divide in [0,1]:
   ra=good(steps,4,1,ins,a,divide,0);rb=good(steps,4,1,ins,b,divide,1);assert (ra,bytes(a))==(rb,bytes(b)),(w,anchor,divide);checks+=1
   rf=bad(steps,4,1,ins,fault,divide,1)
   if (ra,bytes(a))!=(rf,bytes(fault)):negative_mismatches+=1
assert negative_mismatches>0
result={'status':'PASS_ALL_SIGNED_WIDTHS_AND_NEGATIVE_CONTROL','widths':[1,61],'synthetic_packed_cases':checks,'lanes':checks*8,'wrong_signed_shift_mismatches':negative_mismatches,'production_library_sha256':hashlib.sha256((root/'librail8_tail64.so').read_bytes()).hexdigest(),'negative_library_sha256':hashlib.sha256((root/'librail8_tail64_wrongshift.so').read_bytes()).hexdigest(),'advisory_only':True}
(root/'EXTRA_CONTROLS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
