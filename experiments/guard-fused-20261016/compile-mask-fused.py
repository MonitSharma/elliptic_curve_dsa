from pathlib import Path
import mmap,struct,array,hashlib,json,time,sys
root=Path(__file__).parent
src=Path(sys.argv[1]) if len(sys.argv)>1 else root/'evidence/mr-mask-tip-v3.bin'
prefix=Path(sys.argv[2]) if len(sys.argv)>2 else root/'evidence/mr-mask-tip-v3-fused'
t=time.monotonic()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
with src.open('rb') as f:
 mm=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
 assert mm[:8]==b'MRMASK01'
 n,np,nr=struct.unpack_from('<QQQ',mm,8);assert np==1024 and nr==512 and n<=40000000
 assert len(mm)==32+n*16+nr*4
 roots=struct.unpack_from('<'+'I'*nr,mm,32+n*16)
 live=bytearray(n);stack=list(roots)
 while stack:
  i=stack.pop();assert i<n
  if live[i]:continue
  live[i]=1;k,a,b,aux=struct.unpack_from('<IIII',mm,32+16*i);assert aux==0 and k<=5
  if k in [3,4,5]:assert a<i and b<i;stack.extend([a,b])
  if k==2:assert a<np
 counts=array.array('I',[0])*n
 for i in range(n):
  if live[i]:
   k,a,b,aux=struct.unpack_from('<IIII',mm,32+16*i)
   if k in [3,4,5]:counts[a]+=1;counts[b]+=1
 for i in roots:counts[i]+=1
 absorbed=bytearray(n);fused=array.array('I',[0xffffffff])*n;fusion_counts={}
 for i in range(n-1,-1,-1):
  if not live[i] or absorbed[i]:continue
  k,a,b,_=struct.unpack_from('<IIII',mm,32+16*i)
  if k not in [3,4,5]:continue
  for child in [a,b]:
   ck=struct.unpack_from('<I',mm,32+16*child)[0]
   if counts[child]==1 and ck in [3,4,5]:
    fused[i]=child;absorbed[child]=1;key=str(ck)+'->'+str(k);fusion_counts[key]=fusion_counts.get(key,0)+1;break
 def children(i):
  k,a,b,_=struct.unpack_from('<IIII',mm,32+16*i)
  if k not in [3,4,5]:return []
  if fused[i]==0xffffffff:return [a,b]
  child=fused[i];ck,ca,cb,_=struct.unpack_from('<IIII',mm,32+16*child)
  return [ca,cb,b if a==child else a]
 counts=array.array('I',[0])*n
 for i in range(n):
  if live[i] and not absorbed[i]:
   for child in children(i):counts[child]+=1
 for i in roots:counts[i]+=1
 mapping=array.array('I',[0xffffffff])*n;free=[];slots=0;kept=0
 source_sha=sha(src)
 with prefix.with_suffix('.bin').open('w+b',buffering=4*1024*1024) as out,prefix.with_suffix('.nodeids-u32le.bin').open('wb',buffering=4*1024*1024) as ids:
  out.write(bytes(72))
  for i in range(n):
   if not live[i] or absorbed[i]:continue
   k,a,b,aux=struct.unpack_from('<IIII',mm,32+16*i)
   if free:d=free.pop()
   else:d=slots;slots+=1
   mapping[i]=d
   inputs=children(i);child=fused[i]
   if child!=0xffffffff:
    ck=struct.unpack_from('<I',mm,32+16*child)[0];kind=6+3*(ck-3)+(k-3);aa,bb,cc=[mapping[x] for x in inputs];assert max(aa,bb,cc,d)<65536;dest=d|(cc<<16)
   elif k in [3,4,5]:kind=k;aa=mapping[a];bb=mapping[b];assert aa!=0xffffffff and bb!=0xffffffff;dest=d
   else:kind=k;aa=a if k==2 else 0;bb=0;dest=d
   out.write(struct.pack('<IIII',kind,aa,bb,dest));ids.write(struct.pack('<II',i,child));kept+=1
   for x in inputs:
    counts[x]-=1
    if counts[x]==0:free.append(mapping[x])
  root_slots=[mapping[i] for i in roots];assert all(i<slots for i in root_slots)
  out.write(struct.pack('<'+'I'*nr,*root_slots));out.seek(0)
  out.write(b'MRSLOT02'+bytes.fromhex(source_sha)+struct.pack('<QQQQ',kept,slots,np,nr))
 mm.close()
report=dict(status='FUSED_SLOT_PLAN_REQUIRES_INDEPENDENT_VALIDATION',fusion_counts=fusion_counts,original_nodes=n,instructions=kept,peak_live_slots=slots,source_program_sha256=source_sha,plan_sha256=sha(prefix.with_suffix('.bin')),nodeids_sha256=sha(prefix.with_suffix('.nodeids-u32le.bin')),workspace_bytes_full512=slots*64,workspace_bytes_full64=slots*8,original_workspace_bytes_full512=n*64,seconds=time.monotonic()-t,header='MRSLOT02 sourceSHA256raw32 u64LE nops,nslots,ninputs,noutputs (72bytes)',instruction_schema='u32LE kind,a,b,packed (16bytes); kind6..14 packed=dest16|c16<<16; kind=6+3*(childkind-3)+(parentkind-3)',root_slots=root_slots)
prefix.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='root_slots'}))
