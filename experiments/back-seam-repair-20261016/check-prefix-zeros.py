from pathlib import Path
import json,struct,ctypes,ctypes.util,hashlib,collections
r=Path('/home/hclau/ecdsa_research/back-seam-repair-20261016');sites=json.loads((r/'regions-C.json').read_text());NONE=2**64-1
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
p=r.parent/'product-exact-20261015/tip/ops.bin';d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];raw=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(raw,len(raw),d[16:],len(d)-16)==n*56;del d
queries=collections.defaultdict(list)
for j,s in enumerate(sites):
 begin=s['final_begin'];rs=begin+2*(len(s['r'])-257);re=begin+s['prefix_len'];r5=list(struct.iter_unpack('<7Q',raw[rs*56:re*56]));aux=sorted({w for o in r5 for w in o[1:4]if w!=NONE}-set(s['r'][:256]));component=list(struct.iter_unpack('<7Q',raw[s['final_hmr']*56:(begin+s['component_end'])*56]));scratch=sorted({o[3]for o in component if o[0]==13});queries[rs].append(dict(site=j,kind='R5 auxiliary',qubits=aux));queries[begin+s['tv_load_offset']].append(dict(site=j,kind='classical compare source loads',qubits=s['v']));queries[s['final_hmr']].append(dict(site=j,kind='comparator carries',qubits=scratch))
q=[0]*1234;b=[0]*45701
for i in range(512):q[i]=-1;b[i]=-1
def land(x,y):return 0 if x==0 or y==0 else 1 if x==y==1 else -1
def xor(x,y):return -1 if x<0 or y<0 else x^y
def store(old,c,new):return old if c==0 else new if c==1 or old==new else -1
base=1;stack=[];results=[]
for at,(k,z,a,t,bt,bc,reg)in enumerate(struct.iter_unpack('<7Q',raw)):
 for query in queries.get(at,[]):results.append(dict(at=at,**query,unresolved=[w for w in query['qubits']if q[w]!=0],scope_depth=len(stack),base=base))
 if at>max(queries):break
 c=base if bc==NONE else land(base,b[bc])
 if k==6:q[t]=xor(q[t],c)
 elif k==8:q[t]=xor(q[t],land(c,q[a]))
 elif k==13:q[t]=xor(q[t],land(c,land(q[a],q[z])))
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
out=dict(source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),all_declared_inputs_arbitrary=True,all_mr_arbitrary=True,constant_propagation_conservative=True,results=results,proved=all(not x['unresolved']and x['scope_depth']==0 and x['base']==1 for x in results));(r/'prefix-zero-receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));assert out['proved'],'required scratch zeros not proved'
