from pathlib import Path
import ctypes,struct,json,hashlib
r=Path(__file__).resolve().parents[1];d=r/'a29-conditional-family-v1';f=json.loads((d/'PREDECLARED-FAMILY.json').read_text());N=(1<<64)-1
z=ctypes.CDLL('libzstd.so.1');z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p):
 b=p.read_bytes();n=struct.unpack_from('<Q',b,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),b[16:],len(b)-16)==len(o);return o.raw
ONE=frozenset([frozenset()]);ZERO=frozenset()
def var(k):return frozenset([frozenset([k])])
def xor(a,b):return a^b
def mul(a,b):
 out=set()
 for x in a:
  for y in b:
   m=x|y
   if m in out:out.remove(m)
   else:out.add(m)
   assert len(out)<=200000,'UNKNOWN_CLASSICAL_RESOURCE_LIMIT'
 return frozenset(out)
def symbolic(ops,cp,cs,side):
 bits={};base=ONE;stack=[]
 get=lambda q:bits.get(q,var(('entry',q)))
 for i,(k,a,b,t,bt,cc,rt)in enumerate(ops):
  c=base if cc==N else mul(base,get(cc))
  if k==15:stack.append(base);base=c
  elif k==16:assert stack;base=stack.pop()
  elif k in[3,4,5,12]:
   old=get(bt)
   if k==3:bits[bt]=xor(old,c)
   else:
    value=ZERO if k==4 else ONE if k==5 else var(('prefix',i)if i<cp else('suffix',len(ops)-1-i)if i>=len(ops)-cs else('independent-middle',side,i))
    bits[bt]=xor(old,mul(c,xor(old,value)))
 assert not stack
 return bits
def fixture(k,bt=N,cc=N):return(k,N,N,0,bt,cc,N)
seq=[fixture(15,cc=0),fixture(12,bt=0),fixture(5,bt=1),fixture(16)]
b=symbolic(seq,0,0,'x');expected=xor(var(('entry',1)),mul(var(('entry',0)),xor(var(('entry',1)),ONE)));assert b[1]==expected
assert symbolic([fixture(12,bt=0)],0,0,'old')[0]!=symbolic([fixture(12,bt=0)],0,0,'new')[0]
assert symbolic([fixture(12,bt=0)],0,1,'old')[0]==symbolic([fixture(12,bt=0)],0,1,'new')[0]
oldpath=r.parent/'product-exact-20261015/tip/ops.bin';assert hashlib.sha256(oldpath.read_bytes()).hexdigest()==f['source_old'];full=load(oldpath)
frames=[]
for x in f['frames']:
 t=x['tick'];a=list(struct.iter_unpack('<7Q',load(d/f'tick-{t}.old.bin')));b=list(struct.iter_unpack('<7Q',load(d/f'tick-{t}.new.bin')));cp=next((i for i,(u,v)in enumerate(zip(a,b))if u!=v),min(len(a),len(b)));cs=0
 for u,v in zip(reversed(a),reversed(b)):
  if u!=v:break
  cs+=1
 cs=min(cs,len(a)-cp);frames.append(dict(**x,old=a,new=b,cp=cp,cs=cs))
regions=[(x['old_begin'],x['old_end'],x['cp'])for x in frames]
def stable(i):
 for a,b,cp in regions:
  if a<=i<b:assert i-a<cp,('external read or kill inside a changed middle',i)
boundaries={x for a,b,_ in regions for x in[a,b]};depth=0
for i,o in enumerate(struct.iter_unpack('<7Q',full)):
 if i in boundaries:assert depth==0,('active boundary snapshot',i)
 depth+=int(o[0]==15)-int(o[0]==16);assert depth>=0
assert depth==0
results=[]
for x in frames:
 a,b=x['old'],x['new'];written=lambda o:{z[4]for z in o if z[0]in[3,4,5,12]};assert written(a)==written(b);pending=written(a);live={};depth=0
 for i in range(x['old_end'],len(full)//56):
  k,qa,qb,qt,bt,cc,rt=struct.unpack_from('<7Q',full,i*56);reads=({cc}if cc!=N else set())|({bt}if k==3 else set())
  for bit in pending&reads:stable(i);live[bit]=dict(live=True,first_read=i)
  pending-=reads
  if depth==0 and cc==N and k in[4,5,12]and bt in pending:stable(i);live[bt]=dict(live=False,unconditional_kill=i);pending.remove(bt)
  depth+=int(k==15)-int(k==16)
  if not pending:break
 for bit in pending:live[bit]=dict(live=False,never_read=True)
 aa=symbolic(a,x['cp'],x['cs'],'old');bb=symbolic(b,x['cp'],x['cs'],'new');checks={bit:dict(**info,equal=aa.get(bit,var(('entry',bit)))==bb.get(bit,var(('entry',bit))))for bit,info in live.items()};assert all(not z['live']or z['equal']for z in checks.values()),x['tick']
 results.append(dict(tick=x['tick'],prefix_ops=x['cp'],suffix_ops=x['cs'],checks=checks,status='EXACT_LIVE_CLASSICAL_PROJECTION_PASS'))
report=dict(status='ALL29_EXACT_LIVE_CLASSICAL_AND_DEAD_VERSION_KILL_THEOREMS_PASS',source_old=f['source_old'],source_new=f['source_new'],primitive_controls=3,arbitrary_entry_bits=True,all_changed_middle_draws_independent=True,identical_prefix_suffix_draw_roles_shared=True,all_region_boundaries_empty_scope=True,rows=results,no_sampled_acceptance=True)
(d/'live-classical-proof.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(results))
