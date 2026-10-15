from pathlib import Path
import json,ast,ctypes,ctypes.util,struct,hashlib,collections,time
r=Path('/home/hclau/ecdsa_research/free-borrow-family-20261016');assert(r/'raw-verification.exit').read_text().strip()=='0'
queries=collections.defaultdict(list)
def option(s):return None if s=='None'else int(s[5:-1])
for line in(r/'source-map.log').read_text().splitlines():
 f=line.split('\t')
 if f[0]=='FREE_BORROW_CHUNK':
  at,round,mul,lo=map(int,f[1:5]);aa,bb=map(ast.literal_eval,f[5:7]);seed=option(f[7]);kind='ordinary_chunk';meta=dict(round=round,multiply=bool(mul))
 elif f[0]=='FREE_BORROW_TOP1':
  at,lo=map(int,f[1:3]);aa,bb=map(ast.literal_eval,f[3:5]);seed=option(f[5]);kind='TOP1';meta={}
 else:continue
 queries[at].append(dict(kind=kind,at=at,lo=lo,a=aa,b=bb,seed=seed,**meta))
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
p=r/'raw-builder.bin';d=p.read_bytes();n=struct.unpack_from('<Q',d,8)[0];raw=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(raw,len(raw),d[16:],len(d)-16)==n*56;del d
NONE=2**64-1;q=[0]*1234;b=[0]*45701
for i in range(512):q[i]=1<<(i+1);b[i]=1<<(513+i)
def xor(a,b):return None if a is None or b is None else a^b
def land(a,b):
 if a==0 or b==0:return 0
 if a==1:return b
 if b==1 or a is not None and a==b:return a
 return None
def store(old,c,new):return old if c==0 else new if c==1 or old==new else None
def desc(e):
 if e is None:return dict(type='unknown')
 if e in[0,1]:return dict(type='constant',value=e)
 atoms=e&~1
 if atoms&(atoms-1)==0:
  ident=atoms.bit_length()-2
  return dict(type='input_quantum'if ident<512 else 'immutable_classical',id=ident if ident<512 else ident-512,inverted=bool(e&1))
 return dict(type='affine_input',terms=atoms.bit_count(),constant=bool(e&1))
base=1;stack=[];result=[];start=time.time()
for at,o in enumerate(struct.iter_unpack('<7Q',raw)):
 for query in queries.get(at,[]):
  item={k:v for k,v in query.items()if k not in['a','b']};lo=query['lo'];item['lower']=[dict(offset=j,a_q=query['a'][lo-j],b_q=query['b'][lo-j],a=desc(q[query['a'][lo-j]]),b=desc(q[query['b'][lo-j]]))for j in range(1,min(lo,4)+1)];item['seed_value']=None if query['seed']is None else desc(q[query['seed']]);result.append(item)
 k,z,a,t,bt,bc,reg=o;c=base if bc==NONE else land(base,b[bc])
 if k==6:q[t]=xor(q[t],c)
 elif k==8:q[t]=xor(q[t],land(c,q[a]))
 elif k==13:q[t]=xor(q[t],land(c,land(q[a],q[z])))
 elif k==10:
  x,y=q[t],q[a];q[t]=store(x,c,y);q[a]=store(y,c,x)
 elif k in[11,12]:
  q[t]=store(q[t],c,0)
  if k==12:b[bt]=store(b[bt],c,None)
 elif k==3:b[bt]=xor(b[bt],c)
 elif k==4:b[bt]=store(b[bt],c,0)
 elif k==5:b[bt]=store(b[bt],c,1)
 elif k==15:stack.append(base);base=c
 elif k==16:base=stack.pop()
assert not stack and len(result)==sum(map(len,queries.values()))
out=dict(status='DIAGNOSTIC_ONLY raw source prefix; inherited edits not yet modeled or admitted',raw_stream_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),queries=len(result),counts_by_family=dict(collections.Counter(x['kind']for x in result)),lower_source_types=dict(collections.Counter(x['lower'][0]['b']['type']for x in result if x['lower'])),elapsed_s=time.time()-start,rows=result)
(r/'affine-lower-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='rows'},indent=2))
