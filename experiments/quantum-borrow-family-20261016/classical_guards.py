"""Source-exact classical guard identities; unresolved correlations stay UNKNOWN.

Each bit definition and Push snapshot is immutable. Every physical R/HMR gets
its own MR ordinal even when inactive. Only conjunctions of distinct independent
MR literals receive an exact constant expectation. Data and opaque conditions
produce explicit bounds, never an assumed independent probability.
"""
from fractions import Fraction
FALSE=None
TRUE=frozenset()

def conjunction(a,b):
 if a is None or b is None:return FALSE
 if any((tag,i,not sign)in b for tag,i,sign in a):return FALSE
 return a|b

class ClassicalGuards:
 def __init__(self,nb,inputs):
  self.defs=[('C',False),('C',True)];self.bits=[0]*nb;self.last=[(-1,'initial_zero')]*nb;self.base=TRUE;self.stack=[];self.mr=0;self.cache={};self.neg_nodes=[];self.neg_index={};self.opaque_dep={}
  for bit in inputs:self.bits[bit]=len(self.defs);self.defs.append(('I',bit));self.last[bit]=(-1,'ABI')
 def mr_dependent(self,e):
  return e is not None and any(tag=='M'or tag.startswith('O')and self.opaque_dep[(tag,i)]for tag,i,sign in e)
 def negate(self,e):
  if e is None:return TRUE
  if not e:return FALSE
  if len(e)==1:
   tag,i,s=next(iter(e));return frozenset([(tag,i,not s)])
  key=tuple(sorted(e));ident=self.neg_index.get(key)
  if ident is None:ident=len(self.neg_nodes);self.neg_nodes.append(e);self.neg_index[key]=ident;self.opaque_dep[('ON',ident)]=self.mr_dependent(e)
  return frozenset([('ON',ident,True)])
 def opaque(self,ident):
  d=self.defs[ident];self.opaque_dep[('OD',ident)]=d[-1];return frozenset([('OD',ident,True)])
 def resolve(self,ident,g):
  if g is None:return FALSE
  key=(ident,g)
  if key in self.cache:return self.cache[key]
  d=self.defs[ident]
  if d[0]=='C':out=TRUE if d[1]else FALSE
  elif d[0]=='I':out=frozenset([('I',d[1],True)])
  else:
   kind,old,c,mr,at,dep=d
   if c is None or conjunction(c,g)is None:out=self.resolve(old,g)
   elif c<=g:
    if kind=='H':out=frozenset([('M',mr,True)])
    elif kind=='0':out=FALSE
    elif kind=='1':out=TRUE
    else:out=self.negate(self.resolve(old,g))
   else:
    prior=self.resolve(old,g);remaining=c-g
    if kind=='H':
     if prior is None:out=conjunction(remaining,frozenset([('M',mr,True)]))
     elif not prior:out=self.negate(conjunction(remaining,frozenset([('M',mr,False)])))
     else:out=self.opaque(ident)
    elif kind=='0':
     if prior is None:out=FALSE
     elif not prior:out=self.negate(remaining)
     else:out=self.opaque(ident)
    elif kind=='1':
     if prior is None:out=remaining
     elif not prior:out=TRUE
     else:out=self.opaque(ident)
    elif kind=='X':
     if prior is None:out=remaining
     elif not prior:out=self.negate(remaining)
     else:out=self.opaque(ident)
    else:raise AssertionError(kind)
  self.cache[key]=out;return out
 def write(self,kind,bit,c,at,mr=None):
  old=self.bits[bit];self.last[bit]=(at,kind)
  if c is None:return
  if kind in['0','1']and not c:self.bits[bit]=int(kind);return
  if kind=='0'and old==0 or kind=='1'and old==1:return
  dep=kind=='H'or self.mr_dependent(c)or(self.defs[old][-1]if self.defs[old][0]not in['C','I']else False)
  self.bits[bit]=len(self.defs);self.defs.append((kind,old,c,mr,at,dep))
 def step(self,k,bt,bc,at):
  if k==16:self.base=self.stack.pop()[0];return
  c=self.base if bc is None else conjunction(self.base,self.resolve(self.bits[bc],self.base))
  if k==15:
   self.stack.append((self.base,dict(push_op=at,bit=bc,value_definition=self.bits[bc],last_physical_write=self.last[bc])));self.base=c
  elif k in[11,12]:
   ordinal=self.mr;self.mr+=1
   if k==12:self.write('H',bt,c,at,ordinal)
  elif k in[3,4,5]:self.write({3:'X',4:'0',5:'1'}[k],bt,c,at)
  if len(self.cache)>200000:self.cache.clear()
 def expectation(self):
  g=self.base
  if g is None:return dict(kind='exact',lower=Fraction(0),upper=Fraction(0),mr_literals=0,predicate=[])
  n=sum(tag=='M'for tag,i,s in g);upper=Fraction(1,2**n);other=[x for x in g if x[0]!='M'];kind='exact'if not other else 'data_dependent'if not any(tag.startswith('O')and self.opaque_dep[(tag,i)]for tag,i,s in other)else 'opaque_mr_correlation'
  return dict(kind=kind,lower=upper if kind=='exact'else Fraction(0),upper=upper,mr_literals=n,predicate=sorted(g))
 def snapshot(self):
  out=self.expectation();out['lower']=str(out['lower']);out['upper']=str(out['upper']);out['scope_depth']=len(self.stack);out['physical_snapshots']=[s[1]for s in self.stack];return out

def tests():
 def op(s,k,bt=None,bc=None):s.step(k,bt,bc,len(s.defs))
 def fresh():return ClassicalGuards(4,[3])
 s=fresh();op(s,12,0);op(s,15,bc=0);op(s,15,bc=0);assert s.expectation()['lower']==Fraction(1,2)
 s=fresh();op(s,12,0);op(s,15,bc=0);op(s,12,1);op(s,16);op(s,15,bc=1);assert s.expectation()['lower']==Fraction(1,4)
 s=fresh();op(s,12,0);op(s,15,bc=0);op(s,3,0);op(s,15,bc=0);assert s.expectation()['upper']==0
 s=fresh();op(s,12,0);op(s,15,bc=0);op(s,3,1);op(s,16);op(s,15,bc=1);assert s.expectation()['lower']==Fraction(1,2)
 s=fresh();op(s,12,0);op(s,15,bc=0);op(s,12,0);op(s,15,bc=0);assert s.expectation()['lower']==Fraction(1,4)
 s=fresh();op(s,12,0);op(s,5,1);op(s,15,bc=0);op(s,12,1);op(s,16);op(s,15,bc=1);assert s.expectation()['kind']=='opaque_mr_correlation'
 s=fresh();op(s,11);op(s,12,0);op(s,15,bc=0);assert s.expectation()['predicate']==[('M',1,True)]
 s=fresh();op(s,15,bc=3);assert s.expectation()['kind']=='data_dependent'
 return 8
if __name__=='__main__':print('CLASSICAL_GUARD_TESTS',tests())
