from classical_guards import ClassicalGuards,tests
from fractions import Fraction
import random,json
from pathlib import Path
rng=random.Random(20261016);checks=0;probability_checks=0;programs=[]
for trial in range(32):
 program=[];depth=0;mr=0
 for j in range(24):
  kinds=[3,4,5,15]+([16]if depth else[])+([11,12]if mr<7 else[])
  k=rng.choice(kinds)
  if k==15 and depth==3:k=3
  if k==15:depth+=1
  elif k==16:depth-=1
  if k in[11,12]:mr+=1
  bt=rng.randrange(4)if k in[3,4,5,12]else None;bc=rng.randrange(4)if k==15 or rng.randrange(4)==0 and k!=16 else None
  program.append((k,bt,bc))
 program.extend((16,None,None)for _ in range(depth));programs.append(program)
for program in programs:
 engine=ClassicalGuards(4,[0,1,2]);guards=[];bounds=[]
 for at,(k,bt,bc)in enumerate(program):engine.step(k,bt,bc,at);guards.append(engine.base);bounds.append(engine.expectation())
 def eval_expr(g,abi,mrs,cache):
  if g is None:return False
  for tag,i,positive in g:
   if tag=='M':v=bool(mrs>>i&1)
   elif tag=='I':v=bool(abi>>i&1)
   elif tag=='ON':v=not eval_expr(engine.neg_nodes[i],abi,mrs,cache)
   else:v=eval_def(i,abi,mrs,cache)
   if v!=positive:return False
  return True
 def eval_def(i,abi,mrs,cache):
  if i in cache:return cache[i]
  d=engine.defs[i]
  if d[0]=='C':v=d[1]
  elif d[0]=='I':v=bool(abi>>d[1]&1)
  else:
   kind,old,c,mr,at,dep=d;prior=eval_def(old,abi,mrs,cache);active=eval_expr(c,abi,mrs,cache)
   v=prior if not active else bool(mrs>>mr&1)if kind=='H'else not prior if kind=='X'else kind=='1'
  cache[i]=v;return v
 for abi in range(8):
  counts=[0]*len(program)
  for mrs in range(1<<engine.mr):
   bits=[bool(abi>>i&1)for i in range(3)]+[False];base=True;stack=[];ordinal=0;cache={}
   for at,(k,bt,bc)in enumerate(program):
    c=base if bc is None else base and bits[bc]
    if k==15:stack.append(base);base=c
    elif k==16:base=stack.pop()
    elif k in[11,12]:
     random_bit=bool(mrs>>ordinal&1);ordinal+=1
     if k==12 and c:bits[bt]=random_bit
    elif c:
     if k==3:bits[bt]=not bits[bt]
     elif k==4:bits[bt]=False
     elif k==5:bits[bt]=True
    assert base==eval_expr(guards[at],abi,mrs,cache),(program,at,abi,mrs);checks+=1;counts[at]+=base
   assert ordinal==engine.mr and not stack
  for count,bound in zip(counts,bounds):
   actual=Fraction(count,1<<engine.mr);assert bound['lower']<=actual<=bound['upper'];probability_checks+=1
out=dict(structural_unit_tests=tests(),exhaustive_programs=len(programs),scalar_state_checks=checks,conditional_probability_bound_checks=probability_checks,all_mr_assignments_enumerated_per_program=True,all_three_abi_bits_enumerated=True)
(Path(__file__).parent/'guard-tests.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
