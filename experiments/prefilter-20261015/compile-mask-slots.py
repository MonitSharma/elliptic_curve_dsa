from pathlib import Path
import mmap,struct,array,hashlib,json,time,sys
root=Path(__file__).parent
src=Path(sys.argv[1]) if len(sys.argv)>1 else root/'evidence/mr-mask-tip-v3.bin'
prefix=Path(sys.argv[2]) if len(sys.argv)>2 else root/'evidence/mr-mask-tip-v3-slots'
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
 mapping=array.array('I',[0xffffffff])*n;free=[];slots=0;kept=0
 source_sha=sha(src)
 with prefix.with_suffix('.bin').open('w+b',buffering=4*1024*1024) as out,prefix.with_suffix('.nodeids-u32le.bin').open('wb',buffering=4*1024*1024) as ids:
  out.write(bytes(72))
  for i in range(n):
   if not live[i]:continue
   k,a,b,aux=struct.unpack_from('<IIII',mm,32+16*i)
   if free:d=free.pop()
   else:d=slots;slots+=1
   mapping[i]=d
   if k in [3,4,5]:aa=mapping[a];bb=mapping[b];assert aa!=0xffffffff and bb!=0xffffffff
   else:aa=a if k==2 else 0;bb=0
   out.write(struct.pack('<IIII',k,aa,bb,d));ids.write(struct.pack('<I',i));kept+=1
   if k in [3,4,5]:
    for child in [a,b]:
     counts[child]-=1
     if counts[child]==0:free.append(mapping[child])
  root_slots=[mapping[i] for i in roots];assert all(i<slots for i in root_slots)
  out.write(struct.pack('<'+'I'*nr,*root_slots));out.seek(0)
  out.write(b'MRSLOT01'+bytes.fromhex(source_sha)+struct.pack('<QQQQ',kept,slots,np,nr))
 mm.close()
report=dict(status='SLOT_PLAN_REQUIRES_INDEPENDENT_VALIDATION',original_nodes=n,instructions=kept,peak_live_slots=slots,source_program_sha256=source_sha,plan_sha256=sha(prefix.with_suffix('.bin')),nodeids_sha256=sha(prefix.with_suffix('.nodeids-u32le.bin')),workspace_bytes_full512=slots*64,workspace_bytes_full64=slots*8,original_workspace_bytes_full512=n*64,seconds=time.monotonic()-t,header='MRSLOT01 sourceSHA256raw32 u64LE nops,nslots,ninputs,noutputs (72bytes)',instruction_schema='u32LE kind,a,b,dest (16bytes)',root_slots=root_slots)
prefix.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='root_slots'}))
