from pathlib import Path
import ctypes as c,hashlib,time,json,statistics
r=Path(__file__).parent;oldroot=r.parents[1]/'scalar-fast-20261015'
lib=c.CDLL(str(r/'libscalar_split.so'));old=c.CDLL(str(oldroot/'libscalar_fast_batch.so'))
for dll in[lib,old]:
 dll.scalar_fast_fixed_init.argtypes=[c.c_uint];dll.scalar_fast_fixed_init.restype=c.c_int
 dll.scalar_fast_pairs.argtypes=[c.c_uint,c.c_void_p,c.c_void_p];dll.scalar_fast_pairs.restype=c.c_int
for name in['scalar_fast_inputs','scalar_fast_add_pairs']:
 fn=getattr(lib,name);fn.argtypes=[c.c_uint,c.c_void_p,c.c_void_p];fn.restype=c.c_int
inp,add=lib.scalar_fast_inputs,lib.scalar_fast_add_pairs
checks=0
assert inp(0,None,None)==add(0,None,None)==1;checks+=2
assert inp(1,None,None)==0 and add(1,None,None)==0;checks+=2
assert inp(65,None,None)==0 and add(65,None,None)==0;checks+=2
z=c.create_string_buffer(64);out=c.create_string_buffer(b'\xa5'*192)
assert inp(1,z,out)==0 and out.raw[:192]==b'\xa5'*192;checks+=1
st=time.monotonic();assert lib.scalar_fast_fixed_init(20)==1;initnew=time.monotonic()-st
st=time.monotonic();assert old.scalar_fast_fixed_init(20)==1;initold=time.monotonic()-st
assert lib.scalar_fast_fixed_init(20)==0;checks+=1
p=oldroot/'validation-vectors.tsv';assert hashlib.sha256(p.read_bytes()).hexdigest()=='ce17d7cdbbdbea6838462cf09d02cb56ae98c532671486fa3aa499fc7a95237d'
fields=[tuple(bytes.fromhex(w.zfill(64))for w in line.split())for line in p.read_text().splitlines()];assert len(fields)==4096 and all(len(row)==8 and all(len(w)==32 for w in row)for row in fields);rows=[(b''.join(row[:2]),b''.join(row[2:]))for row in fields]
def guarded(fn,count,data,outsize):
 src=c.create_string_buffer(data);dst=c.create_string_buffer(b'\xa5'*(outsize+32));assert fn(count,src,c.byref(dst,16))==1
 assert dst.raw[:16]==b'\xa5'*16 and dst.raw[16+outsize:16+outsize+16]==b'\xa5'*16
 return dst.raw[16:16+outsize]
coords=0
for at in range(0,len(rows),64):
 b=rows[at:at+64];n=len(b);tr=guarded(inp,n,b''.join(x for x,_ in b),n*192)
 pairs=[]
 for i,(_,expected)in enumerate(b):
  row=tr[192*i:192*(i+1)];assert row[:128]==expected[:128] and row[128:]==bytes(64);coords+=4;pairs.append(row[:128])
 sums=guarded(add,n,b''.join(pairs),n*64)
 for i,(_,expected)in enumerate(b):assert sums[64*i:64*(i+1)]==expected[128:];coords+=2
# All partial counts, guard regions, and differently placed source blocks.
for count in[0,1,2,3,7,31,63,64]:
 b=rows[67:67+count];tr=guarded(inp,count,b''.join(x for x,_ in b),count*192)
 assert all(tr[192*i:192*i+128]==v[:128]and tr[192*i+128:192*i+192]==bytes(64)for i,(_,v)in enumerate(b));checks+=1
 sums=guarded(add,count,b''.join(v[:128]for _,v in b),count*64);assert sums==b''.join(v[128:]for _,v in b);checks+=1
# Independent straightforward Python curve edges; includes opposites/infinity.
P=2**256-2**32-977;N=int('fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141',16)
G=(int('79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798',16),int('483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8',16))
def plus(a,b):
 if a is None:return b
 if b is None:return a
 if a[0]==b[0] and(a[1]+b[1])%P==0:return None
 slope=((3*a[0]*a[0])*pow(2*a[1],-1,P)if a==b else(b[1]-a[1])*pow(b[0]-a[0],-1,P))%P
 x=(slope*slope-a[0]-b[0])%P;return(x,(slope*(a[0]-x)-a[1])%P)
def mul(k):
 k%=N;a=None;b=G
 while k:
  if k&1:a=plus(a,b)
  b=plus(b,b);k>>=1
 return a
def enc(p):return bytes(64)if p is None else p[0].to_bytes(32,'big')+p[1].to_bytes(32,'big')
edge=[0,1,2,3,N-1,N,N+1,2**255,2**256-1];points={v:mul(v)for v in edge};edgepairs=[(a,b)for a in edge for b in edge]
for at in range(0,len(edgepairs),64):
 b=edgepairs[at:at+64];trip=guarded(inp,len(b),b''.join(a.to_bytes(32,'big')+bb.to_bytes(32,'big')for a,bb in b),192*len(b))
 wantpairs=b''.join(enc(points[a])+enc(points[bb])for a,bb in b);sums=guarded(add,len(b),wantpairs,64*len(b))
 for i,(a,bb)in enumerate(b):assert trip[i*192:i*192+128]==wantpairs[i*128:(i+1)*128]and trip[i*192+128:(i+1)*192]==bytes(64);assert sums[i*64:(i+1)*64]==enc(plus(points[a],points[bb]))
# Invalid coordinates/counts cannot write even if a later pair is invalid.
valid=enc(G)+enc(G)
for bad in[P.to_bytes(32,'big')+enc(G)[32:],bytes(63)+b'\1',b'\xff'*64]:
 data=valid+bad+enc(G);src=c.create_string_buffer(data);dst=c.create_string_buffer(b'\xa5'*128);assert add(2,src,dst)==0 and dst.raw[:128]==b'\xa5'*128;checks+=1
for fn in[inp,add]:
 dst=c.create_string_buffer(b'\xa5'*192);assert fn(65,None,dst)==0 and dst.raw[:192]==b'\xa5'*192;checks+=1
# Fresh unique input population per round, paired API timings, all tables initialized.
records=[];shots=32768;outbuf=c.create_string_buffer(64*192)
for trial in range(5):
 data=hashlib.shake_256(b'scalar-split-fresh-v1'+trial.to_bytes(4,'little')).digest(shots*64);src=c.create_string_buffer(data);base=c.addressof(src);order=['full','inputs']if trial%2==0 else['inputs','full'];rec=dict(trial=trial,shots=shots,order=order)
 for mode in order:
  fn=old.scalar_fast_pairs if mode=='full'else inp;st=time.monotonic()
  for at in range(0,shots,64):assert fn(64,base+at*64,outbuf)==1
  rec[mode+'_seconds']=time.monotonic()-st
 rec['inputs_ratio']=rec['inputs_seconds']/rec['full_seconds'];records.append(rec);print(json.dumps(rec),flush=True)
# Fresh public affine additions. Input prep is outside add API timings.
shots_add=16384;data=hashlib.shake_256(b'scalar-split-add-v1').digest(shots_add*64);src=c.create_string_buffer(data);base=c.addressof(src);pairs=bytearray()
for at in range(0,shots_add,64):
 assert inp(64,base+at*64,outbuf)==1
 raw=outbuf.raw
 for j in range(64):pairs.extend(raw[j*192:j*192+128])
psrc=c.create_string_buffer(bytes(pairs));pbase=c.addressof(psrc);sbuf=c.create_string_buffer(64*64);addbench=[]
for count in[1,2,8,64]:
 st=time.monotonic()
 for at in range(0,shots_add,count):assert add(count,pbase+at*128,sbuf)==1
 elapsed=time.monotonic()-st;addbench.append(dict(count=count,shots=shots_add,seconds=elapsed,us_per_selected_input=elapsed*1e6/shots_add))
result=dict(status='SPLIT_API_PROTECTED_REFERENCE_AND_EDGE_VALIDATION_PASS',protected_fixture_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),protected_pairs=len(rows),protected_coordinates=coords,independent_python_edge_pairs=len(edgepairs),partial_invalid_guard_controls=checks,window=20,original_init_s=initold,new_init_s=initnew,fresh_pair_rounds=records,median_full_us=statistics.median(v['full_seconds']*1e6/shots for v in records),median_inputs_us=statistics.median(v['inputs_seconds']*1e6/shots for v in records),median_paired_time_ratio=statistics.median(v['inputs_ratio']for v in records),deferred_add_api=addbench,new_source_sha256=hashlib.sha256((r/'scalar_split.c').read_bytes()).hexdigest(),new_library_sha256=hashlib.sha256((r/'libscalar_split.so').read_bytes()).hexdigest(),original_library_sha256=hashlib.sha256((oldroot/'libscalar_fast_batch.so').read_bytes()).hexdigest(),not_claimed=['productionintegration','fullnoncepipeline speedup'])
(r/'validation-benchmark.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
