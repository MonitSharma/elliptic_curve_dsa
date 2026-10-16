from pathlib import Path
import ctypes as c,struct,time,json,hashlib,collections,array
r=Path(__file__).parent;e=r/'evidence';t0=time.monotonic()
class Op(c.Structure):_fields_=[('kind',c.c_uint32),('a',c.c_uint32),('b',c.c_uint32),('aux',c.c_uint32)]
U=c.c_uint64;I=c.c_uint32;S=c.c_size_t
p=e/'mr-mask-tip-v3.bin';source=bytearray(p.read_bytes());assert hashlib.sha256(source).hexdigest()=='560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d'
n,np,nr=struct.unpack_from('<QQQ',source,8);assert (np,nr)==(1024,512);nodes=(Op*n).from_buffer(source,32);roots=(I*nr).from_buffer(source,32+16*n);actual=[int(v)for v in roots if nodes[v].kind not in[0,1]];assert len(actual)==49
libpath=r.parent/'mask-evaluator-20261016/libmask8.so';assert hashlib.sha256(libpath.read_bytes()).hexdigest()=='641f8c1b6578c9878244650bd05cbbbd1fd452e9199c504bc76832cf72fd81e1'
lib=c.CDLL(str(libpath));lib.mask8_eval.argtypes=[c.POINTER(Op),S,c.POINTER(U),S,c.POINTER(U),S,c.POINTER(I),S,c.POINTER(U)];lib.mask8_eval.restype=c.c_int
ports=(U*(np*8))();values=(U*(n*8))();out=(U*(nr*8))();audit=struct.unpack('<1024Q',(e/'mr-mask-tip-v3.audit-input-u64le.bin').read_bytes());known=struct.unpack('<512Q',(e/'mr-mask-tip-v3.audit-known-u64le.bin').read_bytes())
for i,v in enumerate(audit):
 for w in range(8):ports[i*8+w]=v
assert lib.mask8_eval(nodes,n,ports,np,values,n,roots,nr,out)==0
for j in range(nr):assert out[j*8]==(~known[j]&((1<<64)-1))
active=(1<<32)-1
knownper=[sum((known[j]>>lane)&1 for j in range(nr))for lane in range(32)]
# Count actual lazy dependency evaluation with fresh per-input memoization.
# Oracle values only decide a sound absorbing branch after its first operand
# has been scheduled. This measures visit counts, not a new runtime or proof.
def traversal(mask,rightfirst):
 seen=bytearray(n);stack=array.array('I',actual);visits=0;skips=0;bykind=collections.Counter()
 while stack:
  i=stack.pop()
  if seen[i]:continue
  seen[i]=1;visits+=1;o=nodes[i];k=o.kind;bykind[k]+=1
  if k<3:continue
  a,b=(o.b,o.a)if rightfirst else(o.a,o.b);v=values[a*8]&mask
  skip=(k==4 and v==0)or(k==5 and v==mask)
  if not skip:stack.append(b)
  else:skips+=1
  stack.append(a)
 return dict(visited_nodes=visits,fraction_full=visits/n,absorbing_branches=skips,kinds=dict(bykind))
records=[]
for mode,mask in [('packed32',active)]+[(f'lane{i}',1<<i)for i in [0,1,2,3,24,25,30,31]]:
 for order in[False,True]:
  st=time.monotonic();v=traversal(mask,order);v.update(mode=mode,first_child='larger_id'if order else'smaller_id',seconds=time.monotonic()-st);records.append(v);print(json.dumps(v),flush=True)
  assert time.monotonic()-t0<570
# Two-valued absorbing identities, also checked on mixed packed masks.
truth=0
for mask in[1,0xff,active]:
 for a in[0,mask,mask&0xaaaaaaaa]:
  for b in[0,mask,mask&0x55555555]:
   assert a&b==(0 if a==0 else a&b)
   assert a|b==(mask if a==mask else a|b)
   truth+=2
report=dict(status='SOURCE_ONLY_LAZY_ABSORBING_TRAVERSAL_DIAGNOSTIC',source_sha256=hashlib.sha256(source).hexdigest(),reference_library_sha256=hashlib.sha256(libpath.read_bytes()).hexdigest(),fixture='frozen32auditinputs',fixture_input_sha256=hashlib.sha256((e/'mr-mask-tip-v3.audit-input-u64le.bin').read_bytes()).hexdigest(),scored_outputs=512,nonconstant_outputs=49,actual_input_count=32,known_bit_density=sum(knownper)/(32*49),known_bits=sum(knownper),known_per_input=knownper,full_nodes=n,records=records,absorbing_truth_cases=truth,total_s=time.monotonic()-t0,not_claimed=['runtime speedup','source independence theorem change','production change','validated lazy evaluator'])
(e/'mask-lazy-analysis-v1.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='records'}))
