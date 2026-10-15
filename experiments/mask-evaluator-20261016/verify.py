from pathlib import Path
import ctypes as c,hashlib,json,random,struct,time
root=Path(__file__).resolve().parent
class Node(c.Structure):_fields_=[(n,c.c_uint32) for n in ['kind','a','b','aux']]
assert c.sizeof(Node)==16
fn=c.CDLL(str(root/'libmask8.so')).mask8_eval
fn.argtypes=[c.POINTER(Node),c.c_size_t,c.POINTER(c.c_uint64),c.c_size_t,c.POINTER(c.c_uint64),c.c_size_t,c.POINTER(c.c_uint32),c.c_size_t,c.POINTER(c.c_uint64)];fn.restype=c.c_int
mask=(1<<512)-1;rng=random.Random(20261016);comparisons=0
def check(rows,ports,roots):
 global comparisons
 expected=[]
 for kind,a,b,aux in rows:
  assert aux==0
  expected.append(0 if kind==0 else mask if kind==1 else ports[a] if kind==2 else expected[a]^expected[b] if kind==3 else expected[a]&expected[b] if kind==4 else expected[a]|expected[b])
 nodes=(Node*len(rows))(*[Node(*row) for row in rows]);raw=b''.join(v.to_bytes(64,'little') for v in ports);inp=(c.c_uint64*(1024*8)).from_buffer_copy(raw);values=(c.c_uint64*(len(rows)*8))();rr=(c.c_uint32*512)(*roots);out=(c.c_uint64*(512*8))()
 assert fn(nodes,len(rows),inp,1024,values,len(rows),rr,512,out)==0
 assert bytes(values)==b''.join(v.to_bytes(64,'little') for v in expected)
 assert bytes(out)==b''.join(expected[i].to_bytes(64,'little') for i in roots);comparisons+=len(rows)*512
 return nodes,inp,values,rr,out
for trial in range(100):
 ports=[rng.getrandbits(512) for _ in range(1024)];ports[:4]=[0,mask,int('aa'*64,16),int('55'*64,16)]
 rows=[(0,0,0,0),(1,0,0,0)]+[(2,i,0,0) for i in range(1024)]
 for i in range(2000):rows.append((rng.randrange(3,6),rng.randrange(len(rows)),rng.randrange(len(rows)),0))
 roots=[rng.randrange(len(rows)) for _ in range(512)];objects=check(rows,ports,roots)
# Exhaustive first9 input variables simultaneously span all512 assignments.
ports=[sum(((lane>>bit)&1)<<lane for lane in range(512)) if bit<9 else 0 for bit in range(1024)]
rows=[(0,0,0,0),(1,0,0,0)]+[(2,i,0,0) for i in range(9)]
rows.extend([(4,2,3,0),(3,11,1,0),(4,11,12,0),(5,11,12,0),(3,2,2,0),(4,0,3,0)])
objects=check(rows,ports,[i%len(rows) for i in range(512)])
nodes,inp,values,rr,out=objects
def result():return fn(nodes,len(nodes),inp,1024,values,len(nodes),rr,512,out)
old=nodes[2].a;nodes[2].a=1024;assert result()==3;nodes[2].a=old
old=nodes[11].a;nodes[11].a=11;assert result()==4;nodes[11].a=old
old=nodes[0].kind;nodes[0].kind=6;assert result()==5;nodes[0].kind=old
nodes[0].aux=1;assert result()==2;nodes[0].aux=0
old=rr[0];rr[0]=len(nodes);assert result()==6;rr[0]=old
assert fn(nodes,len(nodes),inp,1023,values,len(nodes),rr,512,out)==1
assert fn(nodes,len(nodes),inp,1024,values,len(nodes)-1,rr,512,out)==1
assert result()==0
report={'status':'AVX512_BOOLEAN_DAG_EVALUATOR_PASS','random_dag_fixtures':100,'exhaustive_assignments':512,'node_lane_values_compared':comparisons,'all_node_and_output_words_equal_independent_python':True,'invalid_port_forward_child_unknown_kind_aux_root_capacity_rejected':True,'library_sha256':hashlib.sha256((root/'libmask8.so').read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((root/'mask8.c').read_bytes()).hexdigest(),'actual_circuit_mask_export_test':'pending','nonce_rejection':'disabled_pending_source_bound_export_and_integration'}
(root/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
