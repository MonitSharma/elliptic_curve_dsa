from pathlib import Path
import ctypes as C,struct,json,hashlib
r=Path(__file__).parent
report=json.loads((r/'evidence/global-anf-inputanf16-tip32.json').read_text())
p=Path(report['stream_path']);raw=p.read_bytes();assert raw[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',raw,8)[0];assert n<20000000
z=C.CDLL('libzstd.so.1');z.ZSTD_decompress.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t];z.ZSTD_decompress.restype=C.c_size_t;z.ZSTD_isError.argtypes=[C.c_size_t];z.ZSTD_isError.restype=C.c_uint
out=C.create_string_buffer(n*56);compressed=raw[16:];result=z.ZSTD_decompress(out,n*56,compressed,len(compressed));assert not z.ZSTD_isError(result) and result==n*56,result
kinds=['Neg','Register','AppendToRegister','BitInvert','BitStore0','BitStore1','X','Z','CX','CZ','Swap','R','Hmr','CCX','CCZ','PushCondition','PopCondition','DebugPrint'];fields=['q_control2','q_control1','q_target','c_target','c_condition','r_target']

limit=report['first_rng_cap_operation_events'][0][0]
value=[0]*45701;taint=[False]*45701;last=[None]*45701
for i in range(1200):
 op=struct.unpack_from('<7Q',out,i*56)
 if op[0]==2 and op[4]!=2**64-1:value[op[4]]=-1
base=(1,False);stack=[];active=[]
def land(x,y):
 if x[0]==0 or y[0]==0:return(0,False)
 return (1 if x[0]==y[0]==1 else -1,x[1] or y[1])
for i in range(limit+1):
 op=struct.unpack_from('<7Q',out,i*56);kind=op[0];bt=op[4];condition=op[5]
 if kind==16:base=stack.pop();active.pop();continue
 c=base if condition==2**64-1 else land(base,(value[condition],taint[condition]))
 if i==limit:
  record=dict(first_cap_index=i,active_scope_snapshots=active,current_condition_value=c[0],current_condition_structural_rng_taint=c[1],measurement_target_previous_value=value[bt],measurement_target_previous_rng_taint=taint[bt],measurement_target_previous_write=last[bt],status='STRUCTURAL_TAINT_OVERAPPROXIMATION_ONLY')
  (r/'evidence/first-rng-cap-scopes.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record));break
 if kind==15:
  stack.append(base);active.append(dict(push_index=i,condition_bit=condition,condition_value=c[0],condition_structural_rng_taint=c[1],condition_previous_write=last[condition] if condition!=2**64-1 else None));base=c;continue
 if kind not in [3,4,5,12]:continue
 if c[0]==0:continue
 if kind==12:new=(-1,True)
 elif kind==4:new=(0,False)
 elif kind==5:new=(1,False)
 else:new=(-1 if value[bt]<0 else 1-value[bt],taint[bt])
 if c[0]!=1:new=(new[0] if new[0]==value[bt] else -1,new[1] or taint[bt] or c[1])
 value[bt],taint[bt]=new;last[bt]=dict(index=i,kind=kinds[kind],value=new[0],structural_rng_taint=new[1],condition_bit=condition if condition!=2**64-1 else None)
