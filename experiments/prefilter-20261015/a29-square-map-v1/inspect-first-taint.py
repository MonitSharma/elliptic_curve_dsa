from pathlib import Path
import ctypes,struct,hashlib,json
r=Path(__file__).resolve().parents[1];p=r.parent/'product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin'
b=p.read_bytes();assert hashlib.sha256(b).hexdigest()=='1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522';assert b[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',b,8)[0]
z=ctypes.CDLL('libzstd.so.1');z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
out=ctypes.create_string_buffer(n*56);src=ctypes.create_string_buffer(b[16:]);size=z.ZSTD_decompress(out,len(out),src,len(b)-16);assert size==len(out)
def op(i):return struct.unpack_from('<7Q',out,i*56)
lo=5575678;at=5576535;hi=5598634
near=[dict(index=i,kind=o[0],q_control2=o[1],q_control1=o[2],q_target=o[3],c_target=o[4],c_condition=o[5],r_target=o[6])for i in range(at-24,at+25)for o in[op(i)]]
conds={x['c_condition']for x in near if x['c_condition']!=2**64-1};last={};stack=[];entry_stack=[]
for i in range(at):
 o=op(i)
 if i==lo:entry_stack=stack.copy()
 if o[0]in[3,4,5,12]and o[4]in conds:last[o[4]]=dict(index=i,fields=list(o),active_scopes=stack.copy())
 if o[0]==15:stack.append(dict(index=i,c_condition=o[5]))
 elif o[0]==16:stack.pop()
depth=0;minimum=0
for i in range(lo,hi):
 k=op(i)[0]
 depth+=int(k==15)-int(k==16);minimum=min(minimum,depth)
report=dict(source_sha256=hashlib.sha256(b).hexdigest(),start=lo,end_exclusive=hi,relative_scope_final=depth,relative_scope_min=minimum,entry_scopes=entry_stack,first_taint_scopes=stack,nearby_ops=near,last_condition_writers=last,status='SOURCE_ONLY_CONTEXT_NO_RELATION_ASSUMED')
(r/'a29-square-map-v1/first-taint-context.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(relative_scope_final=depth,relative_scope_min=minimum,entry_scopes=entry_stack,first_taint_scopes=stack,last_condition_writers=last)))
