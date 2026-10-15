from pathlib import Path
import ctypes,ctypes.util,struct,hashlib,json,collections,sys
from fractions import Fraction
r=Path('/home/hclau/ecdsa_research/value-carry-contracts-20261016');N=2**64-1
sys.path.insert(0,str(r.parent/'quantum-borrow-family-20261016'))
from classical_guards import ClassicalGuards
sys.setrecursionlimit(20000)
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 d=p.read_bytes();assert d[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',d,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),d[16:],len(d)-16)==n*56;return o.raw
def matches(hay,needle):
 out=[];p=0
 while True:
  p=hay.find(needle,p)
  if p<0:return out
  if p%56==0:out.append(p//56)
  p+=1
rawpath=r/'square-component/raw-builder.bin';assert hashlib.sha256(rawpath.read_bytes()).hexdigest()=='ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69'
raw=load(rawpath);final=load(r.parent/'product-exact-20261015/tip/ops.bin')
marks=[json.loads(line.split('VALUE_SQUARE_WINDOW ',1)[1])for line in(r/'square-observer.log').read_text().splitlines()if line.startswith('VALUE_SQUARE_WINDOW ')]
inventory=collections.Counter(x['high_width']for x in marks);selected=[x for x in marks if x['high_width']==130];rows=[]
for x in selected:
 a,t,u=x['out'][x['top']-2:x['top']+1];block=raw[x['begin']*56:x['end']*56];ops=list(struct.iter_unpack('<7Q',block))
 candidates=[]
 for i,o in enumerate(ops[:-1]):
  if o[0]==13 and o[3]==t and a in o[1:3]:
   p=next(q for q in o[1:3]if q!=a)
   if ops[i+1]==(8,N,p,a,N,N,N):candidates.append((i,p,o))
 row=dict(x,terminal_candidates=len(candidates),whole_window_matches=matches(final,block),old_window_sha256=hashlib.sha256(block).hexdigest(),next=u)
 if len(candidates)==1:
  i,p,o=candidates[0];row.update(raw_terminal=x['begin']+i,previous=p,penultimate=a,top_bit=t,terminal_op=list(o))
  if len(row['whole_window_matches'])==1:
   at=row['whole_window_matches'][0];row['actual_window']=[at,at+len(ops)];row['actual_terminal']=at+i
   used={q for op in ops for q in op[1:4]if q!=N}
   row['next_framed_by_entire_old_window']=u not in used
   row['old_entire_window_balanced']=sum(op[0]==15 for op in ops)==sum(op[0]==16 for op in ops)
 rows.append(row)
print('SQUARE_SOURCE_INVENTORY',dict(inventory),flush=True);print('C130_BINDING',[(x['shift'],x['terminal_candidates'],len(x['whole_window_matches']))for x in rows],flush=True)
queries=sorted({x['actual_terminal']for x in rows if'actual_terminal'in x});nq=1234;nb=45701
if queries:
 iq=(ctypes.c_int8*nq)();ib=(ctypes.c_int8*nb)();abi=set()
 for k,a,b,t,bt,bc,rt in struct.iter_unpack('<7Q',final):
  if k==2:
   if t!=N:iq[t]=-1
   if bt!=N:ib[bt]=-1;abi.add(bt)
 libpath=r.parent/'precision-family-20261016/constant_zero.so';lib=ctypes.CDLL(str(libpath));lib.constant_zeros.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t),ctypes.c_size_t,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p];lib.constant_zeros.restype=ctypes.c_int
 qq=(ctypes.c_size_t*len(queries))(*queries);out=ctypes.create_string_buffer(len(queries)*nq);assert lib.constant_zeros(final,len(final)//56,nq,nb,qq,len(queries),out,iq,ib)==0
 zz={at:[q for q in range(nq)if out.raw[i*nq+q]]for i,at in enumerate(queries)}
 s=ClassicalGuards(nb,abi);gg={};qs=set(queries)
 for at,(k,a,b,t,bt,bc,rt)in enumerate(struct.iter_unpack('<7Q',final)):
  if at in qs:assert bc==N;gg[at]=s.snapshot()
  s.step(k,None if bt==N else bt,None if bc==N else bc,at)
 for x in rows:
  if'actual_terminal'in x:
   at=x['actual_terminal'];excluded={x[k]for k in ['previous','penultimate','top_bit','next']}
   x['globally_zero_short_donors']=[q for q in zz[at]if q not in excluded];x['guard']=gg[at]
   x['interface_admitted']=x['next_framed_by_entire_old_window']and x['old_entire_window_balanced']and bool(x['globally_zero_short_donors'])
report=dict(status='STRUCTURAL COST/ADMISSION DIAGNOSTIC; NO CANDIDATE',source_inventory=dict(inventory),selected_family='ALL wcin_windows high.len()==130 calls, every NAF term shift4/6/10/32',rows=rows,
 generated_sites=len(rows),admitted_sites=sum(x.get('interface_admitted',False)for x in rows),
 projected_clean_cost_upper=str(sum((Fraction(x['guard']['upper'])for x in rows if'guard'in x),Fraction())),
 raw_sha256=hashlib.sha256(rawpath.read_bytes()).hexdigest(),original_stream_sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e')
(r/'square-interfaces.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
