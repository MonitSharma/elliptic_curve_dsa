NONE=2**64-1
def prove_interface(rows,protected):
 """Exact XOR-normalized expression DAG; failed equalities are UNKNOWN.
 Each AND atom denotes the complete immutable operand expressions; no opacity
 is assigned zero and no dirty entry value or measurement is assumed clean.
 """
 atoms=1;ands={}
 def fresh():
  nonlocal atoms
  out=1<<atoms;atoms+=1;assert atoms<50000;return out
 def land(a,b):
  if a==0 or b==0:return 0
  if a==1:return b
  if b==1 or a==b:return a
  key=tuple(sorted((a,b)))
  if key not in ands:ands[key]=fresh()
  return ands[key]
 usedq=sorted({v for o in rows for v in o[1:4]if v!=NONE}|set(protected));usedb=sorted({v for o in rows for v in o[4:6]if v!=NONE})
 q={w:fresh()for w in usedq};b={w:fresh()for w in usedb};initial=q.copy();base=1;stack=[];mr=0
 for k,z,a,t,bt,bc,reg in rows:
  c=base if bc==NONE else land(base,b[bc])
  if k==6:q[t]^=c
  elif k==8:q[t]^=land(c,q[a])
  elif k==13:q[t]^=land(c,land(q[a],q[z]))
  elif k==10:
   delta=land(c,q[t]^q[a]);q[t]^=delta;q[a]^=delta
  elif k in[11,12]:
   random=fresh();mr+=1;q[t]^=land(c,q[t])
   if k==12:b[bt]^=land(c,b[bt]^random)
  elif k==3:b[bt]^=c
  elif k==4:b[bt]^=land(c,b[bt])
  elif k==5:b[bt]^=land(c,b[bt]^1)
  elif k==15:stack.append(base);base=c
  elif k==16:base=stack.pop()
  elif k in[0,7,9,14,17]:pass
  else:raise AssertionError(('unsupported interface op',k))
 assert not stack and base==1
 unresolved=[w for w in protected if q[w]!=initial[w]]
 return dict(all_entry_quantum_classical_arbitrary=True,all_physical_mr_fresh=True,phase_outside_contract=True,protected=protected,unresolved=unresolved,proved=not unresolved,expression_atoms=atoms,retained_exact_and_nodes=len(ands),mr=mr)

def tests():
 n=NONE
 def op(k,a=n,t=n,b=n,c=n,z=n):return(k,z,a,t,b,c,n)
 # Exact restoration survives arbitrary dirty data and irrelevant nonlinear gates.
 assert prove_interface([op(8,1,0),op(13,2,3,z=4),op(8,1,0)],[0])['proved']
 assert not prove_interface([op(8,1,0),op(6,t=1),op(8,1,0)],[0])['proved']
 # Push keeps the entry bit snapshot after HMR overwrites it.
 assert prove_interface([op(15,c=0),op(8,1,0),op(12,t=2,b=0),op(8,1,0),op(16)],[0])['proved']
 assert not prove_interface([op(8,1,0),op(12,t=1,b=0),op(8,1,0)],[0])['proved']
 # AND keys include both full current operands; measurement outcomes are fresh.
 assert not prove_interface([op(13,1,0,z=2),op(6,t=2),op(13,1,0,z=2)],[0])['proved']
 assert not prove_interface([op(12,t=1,b=0),op(6,t=0,c=0),op(12,t=1,b=0),op(6,t=0,c=0)],[0])['proved']
 return 6
if __name__=='__main__':print('VALUE_INTERFACE_TESTS',tests())
