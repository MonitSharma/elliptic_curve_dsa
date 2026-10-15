from pathlib import Path
import ctypes as c,hashlib,json,mmap,random,struct,time
root=Path(__file__).resolve().parent
class Node(c.Structure):_fields_=[(n,c.c_uint32) for n in ['kind','a','b','aux']]
args=[c.POINTER(Node),c.c_size_t,c.POINTER(c.c_uint64),c.c_size_t,c.POINTER(c.c_uint64),c.c_size_t,c.POINTER(c.c_uint32),c.c_size_t,c.POINTER(c.c_uint64)]
ref=c.CDLL(str(root.parent/'mask-evaluator-20261016/libmask8.so')).mask8_eval;ref.argtypes=args;ref.restype=c.c_int
fn=c.CDLL(str(root/'libmask_width.so')).mask8_eval_width;fn.argtypes=args+[c.c_size_t];fn.restype=c.c_int
rng=random.Random(2026101603);comparisons=0
for trial in range(100):
 rows=[(0,0,0,0),(1,0,0,0)]+[(2,i,0,0) for i in range(1024)]
 for i in range(2000):rows.append((rng.randrange(3,6),rng.randrange(len(rows)),rng.randrange(len(rows)),0))
 nodes=(Node*len(rows))(*[Node(*r) for r in rows]);ports=(c.c_uint64*(1024*8))(*[rng.getrandbits(64) for _ in range(1024*8)]);roots=(c.c_uint32*512)(*[rng.randrange(len(rows)) for _ in range(512)])
 values=(c.c_uint64*(len(rows)*8))();expected=(c.c_uint64*(512*8))();assert ref(nodes,len(rows),ports,1024,values,len(rows),roots,512,expected)==0
 for width in [1,2,4,8]:
  workspace=(c.c_uint64*(len(rows)*width))();out=(c.c_uint64*(512*8))()
  assert fn(nodes,len(rows),ports,1024,workspace,len(rows),roots,512,out,width)==0
  for i in range(len(rows)):
   for j in range(width):assert workspace[i*width+j]==values[i*8+j];comparisons+=64
  for i in range(512):
   for j in range(width):assert out[i*8+j]==expected[i*8+j]
  for field,bad in [('a',1024),('kind',6),('aux',1)]:
   old=getattr(nodes[2],field);setattr(nodes[2],field,bad);assert fn(nodes,len(rows),ports,1024,workspace,len(rows),roots,512,out,width)!=0;setattr(nodes[2],field,old)
  old=nodes[1026].a;nodes[1026].a=1026;assert fn(nodes,len(rows),ports,1024,workspace,len(rows),roots,512,out,width)==4;nodes[1026].a=old
  old=roots[0];roots[0]=len(rows);assert fn(nodes,len(rows),ports,1024,workspace,len(rows),roots,512,out,width)==6;roots[0]=old
  assert fn(nodes,len(rows),ports,1024,workspace,len(rows)-1,roots,512,out,width)==1
 assert fn(nodes,len(rows),ports,1024,values,len(rows),roots,512,expected,3)==7
binary=root.parent/'prefilter-20261015/evidence/mr-mask-tip-v3.bin'
assert hashlib.sha256(binary.read_bytes()).hexdigest()=='560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d'
handle=binary.open('rb');mapping=mmap.mmap(handle.fileno(),0,access=mmap.ACCESS_COPY);n,np,nr=struct.unpack_from('<3Q',mapping,8);nodes=(Node*n).from_buffer(mapping,32);roots=(c.c_uint32*512).from_buffer(mapping,32+n*16)
ports=(c.c_uint64*(1024*8))(*[rng.getrandbits(64) for _ in range(1024*8)]);values=(c.c_uint64*(n*8))();expected=(c.c_uint64*(512*8))();assert ref(nodes,n,ports,np,values,n,roots,nr,expected)==0
timings={}
for width in [1,2,4,8]:
 workspace=(c.c_uint64*(n*width))();out=(c.c_uint64*(512*8))();timings[width]=[]
 for trial in range(3):
  start=time.perf_counter();assert fn(nodes,n,ports,np,workspace,n,roots,nr,out,width)==0;timings[width].append(time.perf_counter()-start)
  for i in range(512):
   for j in range(width):assert out[i*8+j]==expected[i*8+j]
 del workspace
report={'status':'ALL_WIDTHS_EXACT_REFERENCE_PASS','random_dags':100,'node_lane_values_compared':comparisons,'frozen_v3_nodes':n,'actual_v3_seconds':timings,'malformed_inputs_rejected':True,'library_sha256':hashlib.sha256((root/'libmask_width.so').read_bytes()).hexdigest(),'nonce_search':False}
(root/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
