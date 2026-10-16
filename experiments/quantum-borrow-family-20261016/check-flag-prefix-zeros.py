from pathlib import Path
import json,struct,ctypes,ctypes.util,hashlib,collections
r=Path('/home/hclau/ecdsa_research/quantum-borrow-family-20261016');NONE=2**64-1
sites=json.loads((r/'flag-regions.json').read_text());p=r.parent/'product-exact-20261015/tip/ops.bin'
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];raw=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(raw,len(raw),d[16:],len(d)-16)==n*56;del d
queries={s['final_start']:s for s in sites};q=[0]*1234;b=[0]*45701
for i in range(512):q[i]=-1;b[i]=-1
def land(x,y):return 0 if x==0 or y==0 else 1 if x==y==1 else -1
def xor(x,y):return -1 if x<0 or y<0 else x^y
def store(old,c,new):return old if c==0 else new if c==1 or old==new else -1
base=1;stack=[];results=[]
for at,(k,zq,a,t,bt,bc,reg)in enumerate(struct.iter_unpack('<7Q',raw)):
 if at in queries:
  s=queries[at];results.append(dict(site=s['site'],at=at,scratch=s['scratch'],unresolved=[w for w in s['scratch']if q[w]!=0],scope_depth=len(stack),base=base))
 if at>max(queries):break
 c=base if bc==NONE else land(base,b[bc])
 if k==6:q[t]=xor(q[t],c)
 elif k==8:q[t]=xor(q[t],land(c,q[a]))
 elif k==13:q[t]=xor(q[t],land(c,land(q[a],q[zq])))
 elif k==10:
  x,y=q[t],q[a];q[t]=store(x,c,y);q[a]=store(y,c,x)
 elif k in[11,12]:
  q[t]=store(q[t],c,0)
  if k==12:b[bt]=store(b[bt],c,-1)
 elif k==3:b[bt]=xor(b[bt],c)
 elif k==4:b[bt]=store(b[bt],c,0)
 elif k==5:b[bt]=store(b[bt],c,1)
 elif k==15:stack.append(base);base=c
 elif k==16:base=stack.pop()
out=dict(source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),all_declared_inputs_arbitrary=True,all_MR_arbitrary=True,constant_propagation_conservative=True,results=results,proved=len(results)==12 and all(not x['unresolved']for x in results));(r/'flag-prefix-zero-receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));assert out['proved'],'required scratch zero proof unresolved; no candidate build permitted'
