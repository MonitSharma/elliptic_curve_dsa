from pathlib import Path
import mmap,struct,array,json,time
r=Path(__file__).parent;t=time.monotonic();results=[]
with (r/'evidence/mr-mask-tip-v3.bin').open('rb') as f:
 m=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ);n,np,nr=struct.unpack_from('<QQQ',m,8);uses=array.array('I',[0])*n
 kinds=bytearray(n)
 for i,(k,a,b,aux) in enumerate(struct.iter_unpack('<IIII',memoryview(m)[32:32+n*16])):
  kinds[i]=k
  if k in (3,4,5):uses[a]+=1;uses[b]+=1
 for root in struct.unpack_from('<'+'I'*nr,m,32+n*16):uses[root]+=1
 for cap in [8,16]:
  for sop in [False,True]:
   st=time.monotonic();absorbed=bytearray(n);nary=bytearray(n);hist={};nx=na=0
   for i in range(n-1,-1,-1):
    if absorbed[i] or kinds[i]!=3:continue
    _,a,b,_=struct.unpack_from('<IIII',m,32+i*16);leaves=[a,b];count=0
    while len(leaves)<cap:
     pos=next((j for j,x in enumerate(leaves) if uses[x]==1 and kinds[x]==3),None)
     if pos is None:break
     child=leaves[pos];_,aa,bb,_=struct.unpack_from('<IIII',m,32+child*16);absorbed[child]=1;leaves[pos:pos+1]=[aa,bb];nx+=1;count+=1
    ands=0
    if sop:
     for child in leaves:
      if uses[child]==1 and kinds[child]==4:absorbed[child]=1;na+=1;ands+=1
    if count or ands:nary[i]=1;key=str(len(leaves))+'terms/'+str(ands)+'ands';hist[key]=hist.get(key,0)+1
   pairs=0
   for i in range(n-1,-1,-1):
    if absorbed[i] or nary[i] or kinds[i] not in (3,4,5):continue
    _,a,b,_=struct.unpack_from('<IIII',m,32+i*16)
    for child in [a,b]:
     if uses[child]==1 and not nary[child] and kinds[child] in (3,4,5):absorbed[child]=1;pairs+=1;break
   results.append(dict(cap=cap,absorb_singleuse_AND_terms=sop,absorbed_xor_nodes=nx,absorbed_and_nodes=na,remaining_binary_pairs=pairs,total_removed=nx+na+pairs,remaining_instructions=n-nx-na-pairs,nary_histogram=hist,seconds=time.monotonic()-st))
report=dict(status='BOUNDED_NARY_XOR_AND_SOP_PROFILE_ONLY',original_nodes=n,results=results,total_seconds=time.monotonic()-t)
(r/'evidence/mask-nary-profile.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
