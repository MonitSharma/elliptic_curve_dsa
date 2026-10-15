from pathlib import Path
import ctypes as C,struct,json,hashlib
r=Path(__file__).parent
report=json.loads((r/'evidence/global-anf-inputanf16-tip32.json').read_text())
p=Path(report['stream_path']);raw=p.read_bytes();assert raw[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',raw,8)[0];assert n<20000000
z=C.CDLL('libzstd.so.1');z.ZSTD_decompress.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t];z.ZSTD_decompress.restype=C.c_size_t;z.ZSTD_isError.argtypes=[C.c_size_t];z.ZSTD_isError.restype=C.c_uint
out=C.create_string_buffer(n*56);compressed=raw[16:];result=z.ZSTD_decompress(out,n*56,compressed,len(compressed));assert not z.ZSTD_isError(result) and result==n*56,result
kinds=['Neg','Register','AppendToRegister','BitInvert','BitStore0','BitStore1','X','Z','CX','CZ','Swap','R','Hmr','CCX','CCZ','PushCondition','PopCondition','DebugPrint'];fields=['q_control2','q_control1','q_target','c_target','c_condition','r_target']

starts={688341,688342};stack=[];found=[]
for i in range(n):
 op=struct.unpack_from('<7Q',out,i*56)
 if op[0]==15:stack.append(i)
 if op[0]==16:
  start=stack.pop()
  if start in starts:
   rows=[struct.unpack_from('<7Q',out,j*56) for j in range(start,i+1)]
   from collections import Counter
   record=dict(start=start,end=i,operations=i-start+1,counts=dict(Counter(kinds[x[0]] for x in rows)),qubits=sorted(set(v for x in rows for v in x[1:4] if v!=2**64-1)),classical_targets=sorted(set(x[4] for x in rows if x[4]!=2**64-1)),conditions=sorted(set(x[5] for x in rows if x[5]!=2**64-1)))
   found.append(record)
  if len(found)==2:break
(r/'evidence/first-cap-macro-spans.json').write_text(json.dumps(found,indent=2)+'\n');print(json.dumps(found))
