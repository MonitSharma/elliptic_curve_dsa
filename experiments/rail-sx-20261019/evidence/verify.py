import ctypes as c,hashlib,json,statistics,time
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'rail-masks-20261016';data_root=r.parent/'simd-rails-20261015'
class Step(c.Structure):_fields_=[(name,c.c_uint32) for name in ['w','n0','n1','n2','nb','anchor']]
def bind(path,symbol,args):
    lib=c.CDLL(str(path));fn=getattr(lib,symbol);fn.argtypes=args;fn.restype=c.c_int;return fn
U64=c.c_uint64;P64=c.POINTER(U64);P8=c.POINTER(c.c_uint8)
base_sx=bind(r/'libbaseline.so','sx_population',[P64,c.c_size_t,c.c_uint32,P64]);new_sx=bind(r/'libspecialized.so','sx_population',[P64,c.c_size_t,c.c_uint32,P64])
mask=(1<<320)-1
values=[0,mask,int('aa'*40,16),int('55'*40,16)]+[1<<i for i in range(320)]+[mask^(1<<i) for i in range(320)]
h=hashlib.shake_256(b'rail-sx-public-synthetic-20261019-v1').digest(40*256)
values.extend(int.from_bytes(h[i:i+40],'little') for i in range(0,len(h),40))
packed=(U64*(5*len(values)))(*[v>>(64*k)&((1<<64)-1) for v in values for k in range(5)])
a=(U64*(5*len(values)))();b=(U64*(5*len(values)))()
for width in range(1,320):
    assert base_sx(packed,len(values),width,a)==new_sx(packed,len(values),width,b)==0
    assert bytes(a)==bytes(b),width
    for i,v in enumerate(values):
        low=v&((1<<width)-1);expected=low if not low>>(width-1)&1 else low|(((1<<320)-1)^((1<<width)-1))
        actual=sum(int(b[i*5+k])<<(64*k) for k in range(5));assert actual==expected,(width,i)
for width in [0,320,1000]:assert base_sx(packed,1,width,a)==new_sx(packed,1,width,b)==2
args=[c.POINTER(Step),c.c_size_t,P64,c.c_size_t,P8]
original=bind(old/'librail8_masks.so','rail8_population',args);special=bind(r/'libspecialized.so','rail8_population',args)
sb=(data_root/'steps.bin').read_bytes();db=(data_root/'denominator-pairs.bin').read_bytes();expected=(data_root/'reference-flags.bin').read_bytes()
assert len(sb)==138*c.sizeof(Step) and len(db)==len(expected)*64
steps=(Step*138).from_buffer_copy(sb);data=(U64*(len(db)//8)).from_buffer_copy(db);out=(c.c_uint8*len(expected))()
times={'frozen':[],'specialized':[]}
for trial in range(5):
    order=[('frozen',original),('specialized',special)] if trial%2==0 else [('specialized',special),('frozen',original)]
    for name,fn in order:
        start=time.perf_counter();assert fn(steps,138,data,len(expected),out)==0;elapsed=time.perf_counter()-start
        assert bytes(out)==expected,(trial,name);times[name].append(elapsed)
words=[0,1,2,3,((1<<256)-4294968273)-1]
for bit in range(256):words.extend([1<<bit,((1<<256)-(1<<bit))%((1<<256)-4294968273)])
pairs=b''.join(x.to_bytes(32,'little')+((x*17+5)%((1<<256)-4294968273)).to_bytes(32,'little') for x in words);ptr=(U64*(len(pairs)//8)).from_buffer_copy(pairs)
for count in [1,3,7,8,9,len(words)]:
    x=(c.c_uint8*count)();y=(c.c_uint8*count)();assert original(steps,138,ptr,count,x)==special(steps,138,ptr,count,y)==0;assert bytes(x)==bytes(y)
changed=(Step*138).from_buffer_copy(sb);changed[0].anchor^=1;x=(c.c_uint8*1)();y=(c.c_uint8*1)();assert original(changed,138,ptr,1,x)==special(changed,138,ptr,1,y)==0;assert bytes(x)==bytes(y)
med={k:statistics.median(v) for k,v in times.items()}
result={'status':'EXACT_SX_AND_ADVISORY_FLAGS_VERIFIED','primitive_cases':len(values)*319,'widths':'all1..319','invalid_widths_rejected':True,'reference_population':len(expected),'edge_inputs':len(words),'partial_vectors_and_changed_table_match':True,
 'times_seconds':times,'median_seconds':med,'advisory_only_speedup':med['frozen']/med['specialized'],'library_sha256':hashlib.sha256((r/'libspecialized.so').read_bytes()).hexdigest(),
 'scope':'Synthetic public-input kernel diagnostic. No circuit change, nonce, record, active runtime replacement or operational qualification.'}
(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
