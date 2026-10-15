from pathlib import Path
import mmap,struct,array,hashlib,json,time,sys
r=Path(__file__).parent;prefix=r/'guard-fused'
t=time.monotonic()
source=(r/'guard512.bin').read_bytes()
plan=prefix.with_suffix('.bin').read_bytes();ids=array.array('I');ids.frombytes(prefix.with_suffix('.nodeids-u32le.bin').read_bytes());assert sys.byteorder=='little'
def verify(plan,ids):
 assert source[:8]==b'MRMASK01' and plan[:8]==b'MRSLOT02'
 assert plan[8:40]==hashlib.sha256(source).digest()
 nn,np,nr=struct.unpack_from('<QQQ',source,8);n,ns,pp,rr=struct.unpack_from('<QQQQ',plan,40)
 assert pp==np==1024 and rr==nr==512 and ns<=nn and n<=nn
 assert len(plan)==72+n*16+nr*4 and len(ids)==n*2
 slots=array.array('I',[0xffffffff])*ns;previous=-1;arith=0
 for i in range(n):
  node,child=ids[2*i:2*i+2]
  assert previous<node<nn;previous=node
  k,a,b,d=struct.unpack_from('<IIII',plan,72+i*16);sk,sa,sb,aux=struct.unpack_from('<IIII',source,32+node*16)
  assert aux==0
  if k>=6:
   third=d>>16;d&=65535;assert third<ns and d<ns and child<node and child in [sa,sb]
   ck,ca,cb,caux=struct.unpack_from('<IIII',source,32+child*16);assert caux==0 and ck in [3,4,5] and sk in [3,4,5] and k==6+3*(ck-3)+(sk-3)
   assert a<ns and b<ns and slots[a]==ca and slots[b]==cb and slots[third]==(sb if sa==child else sa)
   slots[d]=node;arith+=1;continue
  assert child==0xffffffff and k==sk and d<ns
  if k in [3,4,5]:assert a<ns and b<ns and slots[a]==sa and slots[b]==sb;arith+=1
  elif k==2:assert a==sa and a<np and b==0
  else:assert k in [0,1] and a==b==0
  slots[d]=node
 for i in range(nr):
  root=struct.unpack_from('<I',plan,72+n*16+i*4)[0];original=struct.unpack_from('<I',source,32+nn*16+i*4)[0]
  assert root<ns and slots[root]==original
 return dict(instructions=n,slots=ns,arithmetic_instructions=arith)
positive=verify(plan,ids)
# Invalid header/source and length controls fail before scanning; invalid opcode,
# slot reference, original-node ordering and root changes exercise exact admission.
negative=0
for offset,value in [(8,plan[8]^1),(72,255),(84,255)]:
 bad=bytearray(plan);bad[offset]=value
 try:verify(bad,ids)
 except AssertionError:negative+=1
 else:raise AssertionError('negative plan accepted')
badids=ids[:];badids[2]=badids[0]
try:verify(plan,badids)
except AssertionError:negative+=1
else:raise AssertionError('nonmonotonic IDs accepted')
bad=bytearray(plan);n,ns,_,_=struct.unpack_from('<QQQQ',plan,40);struct.pack_into('<I',bad,72+n*16,ns)
try:verify(bad,ids)
except AssertionError:negative+=1
else:raise AssertionError('invalid root accepted')
report=dict(status='ALL_FUSED_INSTRUCTIONS_RECONSTRUCT_EXACT_ORIGINAL_DAG_AND_ROOTS',source_sha256=hashlib.sha256(source).hexdigest(),plan_sha256=hashlib.sha256(plan).hexdigest(),nodeids_sha256=hashlib.sha256(ids.tobytes()).hexdigest(),negative_controls=negative,seconds=time.monotonic()-t,**positive)
(r/'whole-plan-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
