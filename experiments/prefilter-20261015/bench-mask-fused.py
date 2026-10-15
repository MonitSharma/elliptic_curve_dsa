from pathlib import Path
import ctypes as c,mmap,struct,random,time,json,hashlib
r=Path(__file__).parent;e=r/'evidence';rng=random.Random(753670)
class Op(c.Structure):_fields_=[('kind',c.c_uint32),('a',c.c_uint32),('b',c.c_uint32),('d',c.c_uint32)]
U=c.c_uint64;I=c.c_uint32;S=c.c_size_t
original=c.CDLL(str(r.parent/'mask-evaluator-20261016/libmask8.so'));original.mask8_eval.argtypes=[c.POINTER(Op),S,c.POINTER(U),S,c.POINTER(U),S,c.POINTER(I),S,c.POINTER(U)];original.mask8_eval.restype=c.c_int
slot=c.CDLL(str(r/'libmask_fused.so'));slot.mask_fused_eval.argtypes=[c.POINTER(Op),S,S,c.POINTER(U),S,c.POINTER(U),S,c.POINTER(I),S,c.c_uint,c.POINTER(U)];slot.mask_fused_eval.restype=c.c_int
source=bytearray((e/'mr-mask-tip-v3.bin').read_bytes());plan=bytearray((e/'mr-mask-tip-v3-fused.bin').read_bytes())
assert source[:8]==b'MRMASK01' and plan[:8]==b'MRSLOT02';assert plan[8:40]==hashlib.sha256(source).digest()
n,np,nr=struct.unpack_from('<QQQ',source,8);ni,ns,pp,rr=struct.unpack_from('<QQQQ',plan,40);assert np==pp==1024 and nr==rr==512
nodes=(Op*n).from_buffer(source,32);ops=(Op*ni).from_buffer(plan,72);roots=(I*nr).from_buffer(source,32+n*16);slotroots=(I*nr).from_buffer(plan,72+ni*16)
values=(U*(n*8))();small=(U*(ns*8))();out=(U*(nr*8))();ref=(U*(nr*8))();ports=(U*(np*8))()
audit=struct.unpack('<'+'Q'*1024,(e/'mr-mask-tip-v3.audit-input-u64le.bin').read_bytes());auditknown=struct.unpack('<'+'Q'*512,(e/'mr-mask-tip-v3.audit-known-u64le.bin').read_bytes())
truth_cases=0
for childk in [3,4,5]:
 for parentk in [3,4,5]:
  kind=6+3*(childk-3)+(parentk-3);tiny=(Op*4)(Op(2,0,0,0),Op(2,1,0,1),Op(2,2,0,2),Op(kind,0,1,3|(2<<16)));tr=(I*512)(*[3]*512)
  for p,v in enumerate([0xf0,0xcc,0xaa]):
   for word in range(8):ports[p*8+word]=v
  expected=0
  for a in range(2):
   for b in range(2):
    for cc in range(2):
     first=(a^b) if childk==3 else (a&b) if childk==4 else (a|b)
     value=(first^cc) if parentk==3 else (first&cc) if parentk==4 else (first|cc)
     expected|=value<<(a*4+b*2+cc)
  for width in range(1,9):
   assert slot.mask_fused_eval(tiny,4,4,ports,np,small,len(small),tr,nr,width,out)==0
   for j in range(512):
    for word in range(8):assert (out[j*8+word]&255)==(expected if word<width else 0)
   truth_cases+=8*width*512
records=[];checked=0
for trial in range(12):
 for i in range(np*8):ports[i]=audit[i//8] if trial==0 else rng.getrandbits(64)
 t=time.perf_counter();assert original.mask8_eval(nodes,n,ports,np,values,n,roots,nr,ref)==0;reference_seconds=time.perf_counter()-t
 if trial==0:
  for i in range(nr):
   for w in range(8):assert ref[i*8+w]==(~auditknown[i]&((1<<64)-1))
 for width in range(1,9):
  t=time.perf_counter();assert slot.mask_fused_eval(ops,ni,ns,ports,np,small,len(small),slotroots,nr,width,out)==0;seconds=time.perf_counter()-t
  for i in range(nr):
   for w in range(8):assert out[i*8+w]==(ref[i*8+w] if w<width else 0)
  checked+=nr*8;records.append(dict(trial=trial,width=width,seconds=seconds,reference_full512_seconds=reference_seconds))
# Runtime rejection controls, separate from the complete symbolic plan verifier.
negative=0
for width,capacity in [(0,len(small)),(9,len(small)),(8,ns*8-1)]:
 assert slot.mask_fused_eval(ops,ni,ns,ports,np,small,capacity,slotroots,nr,width,out)!=0;negative+=1
first=ops[0].kind;ops[0].kind=99;assert slot.mask_fused_eval(ops,ni,ns,ports,np,small,len(small),slotroots,nr,8,out)!=0;ops[0].kind=first;negative+=1
first=slotroots[0];slotroots[0]=ns;assert slot.mask_fused_eval(ops,ni,ns,ports,np,small,len(small),slotroots,nr,8,out)!=0;slotroots[0]=first;negative+=1
med=lambda a:sorted(a)[len(a)//2]
report=dict(status='FUSED_RUNTIME_ALL_WORDS_MATCH_FROZEN_REFERENCE',source_sha256=hashlib.sha256(source).hexdigest(),plan_sha256=hashlib.sha256(plan).hexdigest(),library_sha256=hashlib.sha256((r/'libmask_fused.so').read_bytes()).hexdigest(),plan_instructions=ni,peak_slots=ns,compared_words=checked,randomized_512input_trials=11,audit_trials=1,widths=list(range(1,9)),negative_controls=negative,exhaustive_ternary_truth_cases=truth_cases,median_seconds_by_width={str(w):med([x['seconds'] for x in records if x['width']==w]) for w in range(1,9)},median_reference_full512_seconds=med([x['reference_full512_seconds'] for x in records if x['width']==1]),records=records)
(e/'mask-fused-runtime.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='records'}))
