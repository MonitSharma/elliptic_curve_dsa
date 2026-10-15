from pathlib import Path
import ctypes as C,struct,json,hashlib
r=Path(__file__).parent
report=json.loads((r/'evidence/global-anf-inputanf16-tip32.json').read_text())
p=Path(report['stream_path']);raw=p.read_bytes();assert raw[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',raw,8)[0];assert n<20000000
z=C.CDLL('libzstd.so.1');z.ZSTD_decompress.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t];z.ZSTD_decompress.restype=C.c_size_t;z.ZSTD_isError.argtypes=[C.c_size_t];z.ZSTD_isError.restype=C.c_uint
out=C.create_string_buffer(n*56);compressed=raw[16:];result=z.ZSTD_decompress(out,n*56,compressed,len(compressed));assert not z.ZSTD_isError(result) and result==n*56,result
kinds=['Neg','Register','AppendToRegister','BitInvert','BitStore0','BitStore1','X','Z','CX','CZ','Swap','R','Hmr','CCX','CCZ','PushCondition','PopCondition','DebugPrint'];fields=['q_control2','q_control1','q_target','c_target','c_condition','r_target']

start=688341
local=json.loads((r/'evidence/first-macro-688341-arbitrary.json').read_text());wanted=set(local['reset_target_qubits'])
q=[0]*1234;b=[0]*45701;last=[None]*1234
for i in range(1200):
 op=struct.unpack_from('<7Q',out,i*56)
 if op[0]==2:
  if op[3]!=2**64-1:q[op[3]]=-1
  if op[4]!=2**64-1:b[op[4]]=-1
base=1;stack=[]
def land(a,b):return 0 if a==0 or b==0 else 1 if a==b==1 else -1
def lxor(a,b):return a^b if a>=0 and b>=0 else -1
for i in range(start):
 op=struct.unpack_from('<7Q',out,i*56);k=op[0];a,c1,t,bt,cond=op[1:6]
 if k==16:base=stack.pop();continue
 c=base if cond==2**64-1 else land(base,b[cond]);unconditional=not stack and cond==2**64-1
 if k==15:stack.append(base);base=c;continue
 targets=[]
 if k==6:q[t]=lxor(q[t],c);targets=[t]
 elif k==8:q[t]=lxor(q[t],land(q[c1],c));targets=[t]
 elif k==13:q[t]=lxor(q[t],land(land(q[a],q[c1]),c));targets=[t]
 elif k==10:
  olda,oldb=q[c1],q[t]
  if c==1:q[c1],q[t]=oldb,olda
  elif c!=0 and olda!=oldb:q[c1]=q[t]=-1
  targets=[c1,t]
 elif k in [11,12]:
  if c==1 or q[t]==0:q[t]=0
  elif c!=0:q[t]=-1
  if k==12 and c!=0:b[bt]=-1
  targets=[t]
 elif k in [3,4,5] and c!=0:
  new=lxor(b[bt],1) if k==3 else k-4
  b[bt]=new if c==1 or new==b[bt] else -1
 for target in targets:
  last[target]=dict(index=i,kind=kinds[k],scope_depth=len(stack),unconditional_syntactic=unconditional,abstract_condition_value=c,abstract_q_after=q[target],condition_bit=cond if cond!=2**64-1 else None)
rows=[dict(qubit=w,entry_abstract_value=q[w],last_value_operation=last[w])for w in sorted(wanted)]
record=dict(source_stream=str(p),source_sha256=hashlib.sha256(raw).hexdigest(),macro_start=start,initial_all_registered_inputs_arbitrary=True,aux_initial_zero=True,proved_zero_entry_wires=[w for w in sorted(wanted)if q[w]==0],unknown_entry_wires=[w for w in sorted(wanted)if q[w]!=0],details=rows,status='SOUND_TERNARY_PREFIX_CONSTANT_CERTIFICATE_ONLY')
(r/'evidence/first-macro-entry-zero.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
