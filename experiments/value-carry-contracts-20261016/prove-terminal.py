"""Exact, uncapped Boolean-ring theorem and independent integer arithmetic checks.

This is a local primitive proof, NOT a source-bound circuit certificate.
Every variable denotes an arbitrary Boolean value; square-free ANF is canonical.
"""
from pathlib import Path
import hashlib,itertools,json,random

ROOT=Path(__file__).resolve().parent
ZERO=frozenset();ONE=frozenset([frozenset()])
def var(s):return frozenset([frozenset([s])])
def xor(a,b):return a.symmetric_difference(b)
def add(*xs):
 out=ZERO
 for x in xs:out=xor(out,x)
 return out
def mul(a,b):
 out=set()
 for x in a:
  for y in b:
   z=x|y
   if z in out:out.remove(z)
   else:out.add(z)
 return frozenset(out)
def prod(*xs):
 out=ONE
 for x in xs:out=mul(out,x)
 return out
def inv(x):return xor(x,ONE)

def primitive(clean,alias_c=None,omit_cz=False):
 q={s:var(s) for s in ['A','B','C','T','U','D']}
 if clean:q['D']=ZERO
 initial=q.copy();g=var('guard');m=var('new_MR');phase=var('initial_phase')
 oldb=var('old_newbit')
 # original logical C after affine hosting; source must establish this frame.
 c=q['C'] if alias_c is None else add(q['B'],ONE if alias_c else ZERO)
 def cx(x,t):q[t]=add(q[t],prod(g,x))
 def ccx(x,y,t):q[t]=add(q[t],prod(g,x,y))
 if clean:
  ccx(q['A'],q['B'],'D')
  cx(q['B'],'D')
  cx(add(q['B'],c),'T')
  ccx(q['D'],q['T'],'U')
  cx(add(q['B'],c),'T')
  cx(q['B'],'D')
  cx(q['D'],'T')
  phase=add(phase,prod(g,q['D'],m))
  q['D']=prod(q['D'],inv(g))
  newb=add(prod(oldb,inv(g)),prod(m,g))
  if not omit_cz:phase=add(phase,prod(g,newb,q['A'],q['B']))
 else:
  # A->!A and T->T^s are affine conjugations, each guarded as the old CCX.
  cx(ONE,'A');cx(add(q['B'],c),'T')
  for _ in range(2):
   ccx(q['A'],q['B'],'D');ccx(q['D'],q['T'],'U')
  cx(add(q['B'],c),'T');cx(ONE,'A')
  ccx(q['A'],q['B'],'T')
  newb=oldb
 expected=initial.copy()
 expected['T']=add(initial['T'],prod(g,initial['A'],initial['B']))
 delta=prod(add(prod(initial['A'],initial['B']),initial['B']),add(initial['T'],initial['B'],c))
 expected['U']=add(initial['U'],prod(g,delta))
 value=all(q[k]==expected[k] for k in q)
 phase_ok=phase==var('initial_phase')
 return dict(clean_donor=clean,logical_c_alias_b=alias_c,value=value,phase=phase_ok,
             all_old_classical_framed=True,donor_restored=q['D']==initial['D'],
             terms=sum(map(len,q.values())),new_MR_draws=int(clean),
             added_CCX=1 if clean else 4,added_Q=0)

def signed_delta(a,t,c,s):
 A=a^c;B=s^c
 candidate=((A&B)^B)&(t^B^c)
 carry1=(a&s)^(a&c)^(s&c)
 carry2=(t&s)^(t&carry1)^(s&carry1)
 return candidate,carry2^s

def arithmetic():
 cases=0
 for w in range(2,9):
  mask=(1<<w)-1
  for x in range(1<<w):
   for low in range(1<<(w-2)):
    for s,cin,u in itertools.product(range(2),repeat=3):
     b=low|(s<<(w-2))|(s<<(w-1))
     c=((x&((1<<(w-2))-1))+low+cin)>>(w-2)
     a=(x>>(w-2))&1;t=x>>(w-1)
     d,oracle=signed_delta(a,t,c,s);assert d==oracle
     candidate=((x+b+cin)&mask)|((u^d)<<w)
     oracle=((x|(u<<w))+(b|(s<<w))+cin)&((1<<(w+1))-1)
     assert candidate==oracle
     # Explicit frame: bits >=w+1 are NOT propagated; this is an intentional
     # precision-(w+1) truncation, identical to the defined widened function.
     for upper in (0,1,3):
      assert (candidate|(upper<<(w+1)))>>(w+1)==upper
     cases+=1
 rng=random.Random(0x15c411)
 for w in (13,14,16,18,19,20,56,57,60,61):
  for _ in range(2048):
   x=rng.getrandbits(w);low=rng.getrandbits(w-2);s=rng.getrandbits(1)
   cin=rng.getrandbits(1);u=rng.getrandbits(1)
   b=low|(s<<(w-2))|(s<<(w-1));c=((x&((1<<(w-2))-1))+low+cin)>>(w-2)
   d,_=signed_delta((x>>(w-2))&1,x>>(w-1),c,s)
   assert (((x+b+cin)&((1<<w)-1))|((u^d)<<w))==((x|(u<<w))+(b|(s<<w))+cin)&((1<<(w+1))-1)
 return dict(exhaustive_small_integer_cases=cases,wide_integer_cases=20480,
             operation='modulo 2^(w+1) signed-tail addition; bits above w framed unchanged',
             not_full_upper_payload_propagation=True)

def square_specialization():
 # Padded zero addend: initial p,a,T,U arbitrary. A zero donor contains p*a;
 # outgoing carry to U is p*a*T, old T becomes T^p*a, and HMR/CZ cancels.
 p,a,t,u,g,m=map(var,['p','a','T','U','g','m']);d=prod(g,p,a)
 outu=add(u,prod(g,d,t));outt=add(t,prod(g,d));phase=add(prod(g,d,m),prod(g,m,p,a))
 assert outu==add(u,prod(g,p,a,t)) and outt==add(t,prod(g,p,a)) and phase==ZERO
 # Separate no-measurement implementation: a dirty donor is restored by two
 # product toggles; its unknown initial value cancels from the two U toggles.
 dirty=var('dirty_donor');dd=dirty;uu=u
 for _ in range(2):
  dd=add(dd,prod(g,p,a));uu=add(uu,prod(g,dd,t))
 assert dd==dirty and uu==add(u,prod(g,p,a,t))
 cases=0
 for w in range(2,9):
  for x in range(1<<w):
   for value in range(1<<(w-2)):
    for cin,u,complement in itertools.product(range(2),repeat=3):
     original=x|(u<<w);work=x^((1<<w)-1)if complement else x
     carry=(work+value+cin)>>w
     low=(work+value+cin)&((1<<w)-1)
     if complement:low^=(1<<w)-1
     candidate=low|((u^carry)<<w)
     expected=(original+(-1 if complement else 1)*(value+cin))&((1<<(w+1))-1)
     assert candidate==expected;cases+=1
 return dict(value=True,phase=True,added_CCX=1,added_MR=1,added_Q=0,
             arbitrary_dirty_donor_four_CCX_variant=True,dirty_added_CCX=4,dirty_added_MR=0,
             exhaustive_add_sub_complement_integer_cases=cases,
             source_precondition='last two addend positions and new bit are zero')

def main():
 contracts=[primitive(clean,alias) for clean in (False,True) for alias in (None,False,True)]
 assert all(c['value']and c['phase']and c['donor_restored']for c in contracts)
 negative=primitive(True,None,True)
 assert negative['value'] and not negative['phase']
 for a,t,c,s in itertools.product(range(2),repeat=4):assert signed_delta(a,t,c,s)[0]==signed_delta(a,t,c,s)[1]
 result=dict(status='LOCAL THEOREM PASS; NO SOURCE OR GLOBAL CERTIFICATE',
  proof='canonical square-free Boolean ANF, no node/term caps',contracts=contracts,
  missing_cleanup_negative=negative,arithmetic=arithmetic(),square=square_specialization(),
  source_obligations=['actual sign extension in final two old bits and new bit',
   'logical incoming C frame through affine control hosting',
   'new U not used by any other operation in complete old fold',
   'donor distinct from all live local controls and U; clean version exact zero at entry',
   'guard snapshot same for every inserted gate; every HMR draw consumed inactive too',
   'all inherited table anchors retained and actual complete interfaces checked'],
  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (ROOT/'terminal-proof.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result))
if __name__=='__main__':main()
