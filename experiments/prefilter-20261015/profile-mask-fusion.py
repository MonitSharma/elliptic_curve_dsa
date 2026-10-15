from pathlib import Path
import mmap,struct,array,json,time
r=Path(__file__).parent;t=time.monotonic()
with (r/'evidence/mr-mask-tip-v3.bin').open('rb') as f:
 m=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ);n,np,nr=struct.unpack_from('<QQQ',m,8);uses=array.array('I',[0])*n
 for k,a,b,aux in struct.iter_unpack('<IIII',memoryview(m)[32:32+n*16]):
  if k in (3,4,5):uses[a]+=1;uses[b]+=1
 for root in struct.unpack_from('<'+'I'*nr,m,32+n*16):uses[root]+=1
 counts={};eligible=0;absorbed=bytearray(n);pairs={};fused=0
 for i in range(n-1,-1,-1):
  k,a,b,_=struct.unpack_from('<IIII',m,32+16*i)
  if k not in (3,4,5):continue
  for child in (a,b):
   ck=struct.unpack_from('<I',m,32+16*child)[0]
   if uses[child]==1 and ck in (3,4,5):counts[str(ck)+'->'+str(k)]=counts.get(str(ck)+'->'+str(k),0)+1;eligible+=1
  if absorbed[i]:continue
  for child in (a,b):
   ck=struct.unpack_from('<I',m,32+16*child)[0]
   if uses[child]==1 and ck in (3,4,5):absorbed[child]=1;fused+=1;pairs[str(ck)+'->'+str(k)]=pairs.get(str(ck)+'->'+str(k),0)+1;break
report=dict(status='COMPILED_DAG_SINGLE_USE_FUSION_PROFILE',nodes=n,eligible_edges=eligible,eligible_by_kinds=counts,greedy_disjoint_pairs=fused,remaining_instructions=n-fused,greedy_by_kinds=pairs,seconds=time.monotonic()-t)
(r/'evidence/mask-fusion-profile.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
