"""Replay the published shared-library ABI against the frozen full population."""
from pathlib import Path
import ctypes as c,json,time,hashlib
p=Path(__file__).resolve().parent
flags=Path('/proc/cpuinfo').read_text().split('flags',1)[1].splitlines()[0]
assert 'avx512f' in flags and 'avx512dq' in flags
class Step(c.Structure):_fields_=[(s,c.c_uint32) for s in ['w','n0','n1','n2','nb','anchor']]
assert c.sizeof(Step)==24
sb=(p/'steps.bin').read_bytes();db=(p/'denominator-pairs.bin').read_bytes();expected=(p/'reference-flags.bin').read_bytes()
assert len(sb)%24==0 and len(db)==len(expected)*64
steps=(Step*(len(sb)//24)).from_buffer_copy(sb);data=(c.c_uint64*(len(db)//8)).from_buffer_copy(db);out=(c.c_uint8*len(expected))()
lib=c.CDLL(str(p/'librail8.so'));fn=lib.rail8_population
fn.argtypes=[c.POINTER(Step),c.c_size_t,c.POINTER(c.c_uint64),c.c_size_t,c.POINTER(c.c_uint8)];fn.restype=c.c_int
t=time.perf_counter();code=fn(steps,len(steps),data,len(expected),out);dt=time.perf_counter()-t
assert code==0;actual=bytes(out);assert actual==expected
print(json.dumps({'shared_library_full_flags_equal':True,'shots':len(expected),'seconds':dt,'us_per_shot':dt*1e6/len(expected),'library_sha256':hashlib.sha256((p/'librail8.so').read_bytes()).hexdigest(),'advisory_only':True,'direct_rejection':False}))
