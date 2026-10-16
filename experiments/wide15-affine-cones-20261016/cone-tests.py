from pathlib import Path
from collections import Counter
from itertools import product
import json
from algebra import execute
from cones import analyze,N
G=lambda k,a=N,b=N,t=N,c=N:(k,a,b,t,N,c,N)
A=G(13,0,1,4);B=G(13,1,2,4)
fixtures=[('cancel',[A,A],0),('shared',[A,B],2),('rank4',[A,G(13,2,3,4)],4),
 ('majority',[A,G(8,b=0,t=1),B,G(8,b=0,t=1)],2),
 ('affine_and_target',[A,G(6,t=1),G(8,b=2,t=4),G(6,t=4),B],2),
 ('swap',[A,G(10,b=1,t=2),B],2),
 ('32middle',[A,*([G(6,t=2)]*32),B],2)]
checks=[];states=0
def old_apply(ops,q,g):
 q=list(q)
 if g:
  for k,a,b,t,_,_,_ in ops:
   if k==13:q[t]^=q[a]&q[b]
   elif k==8:q[t]^=q[b]
   elif k==6:q[t]^=1
   elif k==10:q[b],q[t]=q[t],q[b]
 return q
for name,ops,expected in fixtures:
 c=analyze(ops.__getitem__,0,len(ops),Counter());assert c and c['rank']==expected,name
 end=c['end_exclusive'];assert end<=len(ops)
 if expected<4:
  wires=c['entry_control_wires'];target=c['target'];nv=len(wires)
  for q in product([0,1],repeat=5):
   for g in [0,1]:
    x=sum(q[w]<<i for i,w in enumerate(wires));_,t=execute(c['factorization_and_exact_frame'],x,nv,q[target],g)
    before=list(q);before[target]=t
    new=old_apply(ops[1:end-1],before,g);old=old_apply(ops[:end],q,g)
    assert old==new,(name,q,g,old,new)
    states+=1
 checks.append({'name':name,'rank':expected})
negative=[('33middle',[A,*([G(6,t=2)]*33),B]),('phase',[A,G(7,t=3),B]),
 ('targetcontrol',[A,G(8,b=4,t=0),B]),('targetswap',[A,G(10,b=4,t=0),B]),
 ('differentguard',[A,G(13,1,2,4,c=1)]),('classical',[A,G(3),B]),
 ('MR',[A,G(12,t=3),B]),('scope',[A,G(15,c=1),B]),
 ('othernonlinear',[A,G(13,0,1,3),B]),
 ('17support',[A,*[G(6,t=q)for q in range(5,20)],B])]
for name,ops in negative:
 assert analyze(ops.__getitem__,0,len(ops),Counter())is None,name
 checks.append({'name':name,'reject':True})
report={'status':'SHARED_ACTUAL_AFFINE_CONE_SCANNER_FULL_DIRTY_GUARD_TRUTH_AND_BOUNDARY_TESTS_PASS','checks':checks,'full_entry_states':states}
Path(__file__).with_name('CONE-TESTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'checks':len(checks),'full_entry_states':states}))
