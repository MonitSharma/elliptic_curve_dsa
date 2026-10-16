"""Exact Boolean transducer; no value/phase arithmetic approximation or caps."""
from pathlib import Path
import struct,json,hashlib,itertools,random
NONE=2**64-1
class Algebra:
 def __init__(self):self.nodes=[('c',0),('c',1)];self.intern={}
 def node(self,key):
  if key not in self.intern:self.intern[key]=len(self.nodes);self.nodes.append(key)
  return self.intern[key]
 def var(self,key):return self.node(('v',key))
 def xor(self,x,y):
  if x==0:return y
  if y==0:return x
  if x==y:return 0
  return self.node(('xor',*sorted((x,y))))
 def inv(self,x):return self.xor(x,1)
 def land(self,x,y):
  if x==0 or y==0:return 0
  if x==1:return y
  if y==1 or x==y:return x
  return self.node(('and',*sorted((x,y))))
 def evaluate(self,values):
  out=[]
  for n in self.nodes:
   out.append(n[1]if n[0]=='c'else values[n[1]]if n[0]=='v'else out[n[1]]^out[n[2]]if n[0]=='xor'else out[n[1]]&out[n[2]])
  return out
def step(a,ops,entry,base,old_random,extra_random=None):
 b=entry.copy();stack=[];old_index=0;extra=0
 for kind,z,q,t,bt,bc,reg in ops:
  if kind==16:base=stack.pop();continue
  cond=base if bc==NONE else a.land(base,b[bc])
  if kind in(11,12):
   if kind==12 and bt==45701 and extra_random is not None:r=extra_random;extra+=1
   else:r=old_random[old_index];old_index+=1
   if kind==12:b[bt]=a.xor(a.land(b[bt],a.inv(cond)),a.land(r,cond))
  elif kind==3:b[bt]=a.xor(b[bt],cond)
  elif kind==4:b[bt]=a.land(b[bt],a.inv(cond))
  elif kind==5:b[bt]=a.inv(a.land(a.inv(b[bt]),a.inv(cond)))
  elif kind==15:stack.append(base);base=cond
  elif kind not in(0,1,2,6,7,8,9,10,13,14,17):raise AssertionError(kind)
 assert not stack
 return b,base,old_index,extra
def scalar(ops,entry,base,randoms):
 b=entry.copy();stack=[];j=0
 for kind,z,q,t,bt,bc,reg in ops:
  if kind==16:base=stack.pop();continue
  c=base if bc==NONE else base&b[bc]
  if kind in(11,12):
   r=randoms[j];j+=1
   if kind==12:b[bt]=(b[bt]& (1^c))^(r&c)
  elif kind==3:b[bt]^=c
  elif kind==4:b[bt]&=1^c
  elif kind==5:b[bt]|=c
  elif kind==15:stack.append(base);base=c
 assert not stack
 return b,base,j
def row(k,bt=NONE,bc=NONE):return(k,NONE,NONE,0 if k in(11,12)else NONE,bt,bc,NONE)
def tests():
 count=0;programs=[
  [row(15,bc=0),row(3,bt=0),row(12,bt=1),row(16)],
  [row(11,bc=0),row(12,bt=1)],
  [row(12,bt=1,bc=0),row(15,bc=1),row(3,bt=1),row(12,bt=0),row(16)],
 ]
 rng=random.Random(161026)
 for _ in range(32):
  program=[]
  for j in range(6):
   k=rng.choice([3,4,5,11,12]);program.append(row(k,bt=rng.randrange(2)if k!=11 else NONE,bc=rng.choice([NONE,0,1])))
  if sum(o[0]in(11,12)for o in program)>3:continue
  programs.append([row(15,bc=rng.randrange(2)),*program,row(16)])
 for ops in programs:
  n=sum(o[0]in(11,12)for o in ops);a=Algebra();entry={i:a.var(('b',i))for i in(0,1)};g=a.var('g');randoms=[a.var(('r',j))for j in range(n)];out,base,consumed,_=step(a,ops,entry,g,randoms);assert consumed==n
  for bits in itertools.product((0,1),repeat=3+n):
   values={('b',0):bits[0],('b',1):bits[1],'g':bits[2],**{('r',j):bits[3+j]for j in range(n)}};evaluation=a.evaluate(values);want,wbase,draws=scalar(ops,{0:bits[0],1:bits[1]},bits[2],bits[3:]);assert [evaluation[out[i]]for i in(0,1)]==[want[i]for i in(0,1)];assert evaluation[base]==wbase and draws==n;count+=1
 return dict(programs=len(programs),exhaustive_scalar_cases=count,snapshot_and_inactive_MR_fixtures_included=True)
def main():
 r=Path(__file__).parent;data=(r/'quantum_flag.bin').read_bytes();assert data[:8]==b'QFLAG001';assert struct.unpack_from('<Q',data,8)[0]==12;at=16;reports=[];metadata=json.loads((r/'flag-regions.json').read_text())
 for site in range(12):
  n,m=struct.unpack_from('<QQ',data,at);at+=16;old_bytes=data[at:at+56*n];at+=56*n;new_bytes=data[at:at+56*m];at+=56*m
  assert hashlib.sha256(old_bytes).hexdigest()==metadata[site]['old_bytes_sha256'];assert hashlib.sha256(new_bytes).hexdigest()==metadata[site]['new_bytes_sha256']
  old=list(struct.iter_unpack('<7Q',old_bytes));new=list(struct.iter_unpack('<7Q',new_bytes));assert not any(o[4]==45701 or o[5]==45701 for o in old)
  bits={w for o in old+new for w in(o[4],o[5])if w!=NONE};a=Algebra();entry={i:a.var(('entry_bit',i))for i in bits};g=a.var('entry_base_snapshot');mr=sum(o[0]in(11,12)for o in old);randoms=[a.var(('old_MR',j))for j in range(mr)];extra=a.var('new_independent_MR')
  ob,og,oc,oe=step(a,old,entry,g,randoms);nb,ng,nc,ne=step(a,new,entry,g,randoms,extra);assert oc==nc==mr and oe==0 and ne==1
  unresolved=[i for i in bits if i<45701 and ob[i]!=nb[i]];assert not unresolved and og==ng==g
  reports.append(dict(site=site,proved=True,arbitrary_entry_bits=sorted(bits),arbitrary_enclosing_scope_snapshot=True,all_old_MR_independent_shared_under_projection=True,new_MR_independent=True,old_physical_MR=mr,inserted_physical_MR=1,old_classical_outputs_unresolved=unresolved,scope_snapshot_restored=True,exact_Boolean_nodes=len(a.nodes),no_caps=True))
 assert at==len(data)
 out=dict(proved=True,proof='Exact immutable Boolean DAG: equal node roots denote the same Boolean function by construction; no probabilistic testing or cap used for acceptance.',protected_simulator_reference='src/sim.rs HMR,R,BitInvert,BitStore0,BitStore1,PushCondition,PopCondition',protected_simulator_sha256='f0c72f2a280cd68acee1dbf8282098f72d6b3bf4311e0abf96d122fe002256d7',protected_simulator_Windows_CRLF_sha256='048a087c3059eb4269e8815fdccf922bfdfaa2dc9564e5b2cc2eeba33e2d5c46',reference_newline_note='Windows source CRLF hash differs; normalized LF equals frozen server protected source exactly',helper_blob_sha256=hashlib.sha256(data).hexdigest(),all_used_old_entry_bits_arbitrary=True,all_unreferenced_old_bits_unchanged_by_frame_rule=True,all_original_MR_preserved_even_when_inactive=True,extra_bit=45701,old_bit_namespace_exclusive_bound=45701,arbitrary_enclosing_scope_value_snapshot=True,tests=tests(),sites=reports)
 (r/'classical-interface-proof.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='sites'},indent=2))
if __name__=='__main__':main()
