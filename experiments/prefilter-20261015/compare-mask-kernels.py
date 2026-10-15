from pathlib import Path
import ctypes as c,struct,random,time,json,hashlib
r=Path(__file__).parent;e=r/'evidence';rng=random.Random(753670)
class Op(c.Structure):_fields_=[('kind',c.c_uint32),('a',c.c_uint32),('b',c.c_uint32),('d',c.c_uint32)]
U=c.c_uint64;I=c.c_uint32;S=c.c_size_t;signature=[c.POINTER(Op),S,S,c.POINTER(U),S,c.POINTER(U),S,c.POINTER(I),S,c.c_uint,c.POINTER(U)]
loaded={}
for name,filename,func,magic,header,haspool in [('fused','libmask_fused.so','mask_fused_eval','fused',72,False),('nary8','libmask_nary8.so','mask_nary8_eval','nary8',80,True),('nary8fast','libmask_nary8_fast.so','mask_nary8_fast_eval','nary8',80,True)]:
 data=bytearray((e/('mr-mask-tip-v3-'+magic+'.bin')).read_bytes());counts=struct.unpack_from('<'+'Q'*(5 if haspool else 4),data,40);n,ns,np,nr=counts[:4];lib=c.CDLL(str(r/filename));fn=getattr(lib,func);fn.argtypes=signature+([c.POINTER(I),S] if haspool else []);fn.restype=c.c_int
 ops=(Op*n).from_buffer(data,header);roots=(I*nr).from_buffer(data,header+n*16);workspace=(U*(ns*8))();out=(U*(nr*8))();extra=[]
 if haspool:extra=[(I*counts[4]).from_buffer(data,header+n*16+nr*4),counts[4]]
 loaded[name]=dict(data=data,lib=lib,fn=fn,ops=ops,n=n,ns=ns,roots=roots,v=workspace,out=out,extra=extra,library_sha256=hashlib.sha256((r/filename).read_bytes()).hexdigest())
ports=(U*(1024*8))();records=[];compared=0
for trial in range(16):
 for i in range(len(ports)):ports[i]=rng.getrandbits(64)
 for width in [1,8]:
  order=list(loaded);rng.shuffle(order);expected=None
  for name in order:
   k=loaded[name];t=time.perf_counter();assert k['fn'](k['ops'],k['n'],k['ns'],ports,1024,k['v'],len(k['v']),k['roots'],512,width,k['out'],*k['extra'])==0;seconds=time.perf_counter()-t
   output=bytes(k['out'])
   if expected is None:expected=output
   else:assert output==expected;compared+=4096
   records.append(dict(trial=trial,width=width,kernel=name,seconds=seconds))
fast=loaded['nary8fast'];first=fast['ops'][0].kind;fast['ops'][0].kind=0
assert fast['fn'](fast['ops'],fast['n'],fast['ns'],ports,1024,fast['v'],len(fast['v']),fast['roots'],512,8,fast['out'],*fast['extra'])!=0;fast['ops'][0].kind=first
old=fast['ops'][1].d;fast['ops'][1].d=0
assert fast['fn'](fast['ops'],fast['n'],fast['ns'],ports,1024,fast['v'],len(fast['v']),fast['roots'],512,8,fast['out'],*fast['extra'])!=0;fast['ops'][1].d=old
med=lambda a:sorted(a)[len(a)//2]
report=dict(status='INTERLEAVED_SAME_PROCESS_EXACT_KERNEL_COMPARISON',source_mask_sha256='560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d',compared_words=compared,randomized512input_trials=16,fast_constant_slot_negative_controls=2,libraries={name:k['library_sha256'] for name,k in loaded.items()},median_seconds={name:{str(w):med([x['seconds'] for x in records if x['kernel']==name and x['width']==w]) for w in [1,8]} for name in loaded},records=records)
(e/'mask-kernel-interleaved.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='records'}))
