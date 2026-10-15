from pathlib import Path
import struct,array,hashlib,json,time,sys,collections
r=Path(__file__).parent;e=r/'evidence';p=e/'mr-mask-tip-v3-nary8';t=time.monotonic()
source=(e/'mr-mask-tip-v3.bin').read_bytes();plan=p.with_suffix('.bin').read_bytes();ids=array.array('I');ids.frombytes(p.with_suffix('.nodeids-u32le.bin').read_bytes());termids=array.array('I');termids.frombytes(p.with_suffix('.termids-u32le.bin').read_bytes());assert sys.byteorder=='little'
def verify(plan,ids,termids):
 assert source[:8]==b'MRMASK01' and plan[:8]==b'MRSLOT03' and plan[8:40]==hashlib.sha256(source).digest()
 nn,np,nr=struct.unpack_from('<QQQ',source,8);n,ns,pp,rr,nt=struct.unpack_from('<QQQQQ',plan,40);assert pp==np==1024 and rr==nr==512 and ns<65535 and n<=nn and len(ids)==n*2 and len(termids)==nt
 assert len(plan)==80+n*16+nr*4+nt*4;pooloff=80+n*16+nr*4;slots=array.array('I',[0xffffffff])*ns;previous=-1;nf=nx=0
 for i in range(n):
  node,child=ids[2*i:2*i+2];assert previous<node<nn;previous=node
  k,a,b,packed=struct.unpack_from('<IIII',plan,80+i*16);sk,sa,sb,aux=struct.unpack_from('<IIII',source,32+node*16);assert aux==0
  if k in [15,16]:
   assert sk==3 and child==0xffffffff and packed<ns and 2<=b<=8 and a+b<=nt
   leaves=[];products=0
   for index in range(a,a+b):
    value=struct.unpack_from('<I',plan,pooloff+index*4)[0];aa=value&65535;bb=value>>16;leaf=termids[index];assert leaf<node and aa<ns
    if bb==65535:assert slots[aa]==leaf
    else:
     products+=1;lk,la,lb,laux=struct.unpack_from('<IIII',source,32+leaf*16);assert bb<ns and lk==4 and la==slots[aa] and lb==slots[bb] and laux==0
    leaves.append(leaf)
   assert (products==0 if k==15 else products>0)
   targets=set(leaves);pending=[node];expanded=[];budget=0
   while pending:
    x=pending.pop();budget+=1;assert budget<=32
    if x in targets:expanded.append(x)
    else:
     xk,xa,xb,xaux=struct.unpack_from('<IIII',source,32+x*16);assert xk==3 and xaux==0 and xa<x and xb<x;pending.extend([xa,xb])
   assert collections.Counter(expanded)==collections.Counter(leaves)
   slots[packed]=node;nx+=1;continue
  if k>=6:
   third=packed>>16;dest=packed&65535;assert 6<=k<=14 and third<ns and dest<ns and child<node and child in [sa,sb]
   ck,ca,cb,caux=struct.unpack_from('<IIII',source,32+child*16);assert ck in [3,4,5] and sk in [3,4,5] and caux==0 and k==6+3*(ck-3)+(sk-3)
   assert a<ns and b<ns and slots[a]==ca and slots[b]==cb and slots[third]==(sb if sa==child else sa)
   slots[dest]=node;nf+=1;continue
  assert k==sk and child==0xffffffff and packed<ns
  if k in [3,4,5]:assert a<ns and b<ns and slots[a]==sa and slots[b]==sb
  elif k==2:assert a==sa and a<np and b==0
  else:assert k in [0,1] and a==b==0
  slots[packed]=node
 for i in range(nr):
  root=struct.unpack_from('<I',plan,80+n*16+i*4)[0];original=struct.unpack_from('<I',source,32+nn*16+i*4)[0];assert root<ns and slots[root]==original
 return dict(instructions=n,slots=ns,nary_instructions=nx,fused_binary_instructions=nf,pool_terms=nt)
positive=verify(plan,ids,termids);negative=0
for offset,value in [(8,plan[8]^1),(80,255),(92,255)]:
 bad=bytearray(plan);bad[offset]=value
 try:verify(bad,ids,termids)
 except AssertionError:negative+=1
 else:raise AssertionError('corrupted plan accepted')
badids=ids[:];badids[2]=badids[0]
try:verify(plan,badids,termids)
except AssertionError:negative+=1
else:raise AssertionError('bad originalnode mapping accepted')
n,ns,np,nr,nt=struct.unpack_from('<QQQQQ',plan,40)
for offset in [80+n*16,80+n*16+nr*4]:
 bad=bytearray(plan);struct.pack_into('<I',bad,offset,ns)
 try:verify(bad,ids,termids)
 except AssertionError:negative+=1
 else:raise AssertionError('bad root/pool accepted')
badterms=termids[:];badterms[0]=0xffffffff
try:verify(plan,ids,badterms)
except (AssertionError,struct.error):negative+=1
else:raise AssertionError('bad source term mapping accepted')
report=dict(status='ALL_NARY_SOP_INSTRUCTIONS_RECONSTRUCT_EXACT_ORIGINAL_DAG_AND_ROOTS',source_sha256=hashlib.sha256(source).hexdigest(),plan_sha256=hashlib.sha256(plan).hexdigest(),negative_controls=negative,seconds=time.monotonic()-t,**positive)
(e/'mask-nary8-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
