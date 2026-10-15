from pathlib import Path
import ctypes as C,struct,json,hashlib
r=Path(__file__).parent
report=json.loads((r/'evidence/global-anf-inputanf16-tip32.json').read_text())
p=Path(report['stream_path']);raw=p.read_bytes();assert raw[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',raw,8)[0];assert n<20000000
z=C.CDLL('libzstd.so.1');z.ZSTD_decompress.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t];z.ZSTD_decompress.restype=C.c_size_t;z.ZSTD_isError.argtypes=[C.c_size_t];z.ZSTD_isError.restype=C.c_uint
out=C.create_string_buffer(n*56);compressed=raw[16:];result=z.ZSTD_decompress(out,n*56,compressed,len(compressed));assert not z.ZSTD_isError(result) and result==n*56,result
kinds=['Neg','Register','AppendToRegister','BitInvert','BitStore0','BitStore1','X','Z','CX','CZ','Swap','R','Hmr','CCX','CCZ','PushCondition','PopCondition','DebugPrint'];fields=['q_control2','q_control1','q_target','c_target','c_condition','r_target']
indices=sorted(set(i for event in report['first_rng_cap_operation_events'][:3] for i in range(event[0]-8,event[0]+9)))
rows=[]
for i in indices:
 op=struct.unpack_from('<7Q',out,i*56);rows.append(dict(index=i,kind=kinds[op[0]],**{f:v for f,v in zip(fields,op[1:]) if v!=2**64-1}))
record=dict(source_stream=str(p),stream_sha256=hashlib.sha256(raw).hexdigest(),first_cap_events=report['first_rng_cap_operation_events'],nearby_operations=rows,status='LOSS_OF_ABSTRACT_PRECISION_NOT_PROVEN_TRUE_RNG_DEPENDENCE')
(r/'evidence/first-rng-cap-operations.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(rows))
