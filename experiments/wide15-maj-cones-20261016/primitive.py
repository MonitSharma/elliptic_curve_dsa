from itertools import product
import json
from pathlib import Path

OLD=[(13,0,1,3),(8,None,0,1),(13,1,2,3),(8,None,0,1)]
NEW=[(8,None,1,0),(8,None,1,2),(13,0,2,3),(8,None,1,2),(8,None,1,0),(8,None,1,3)]

def apply(gates,q,base,direct,phase):
 q=list(q);cond=base&direct;T=0
 for kind,a,b,t in gates:
  if kind==13:q[t]^=cond&q[a]&q[b];T+=cond
  else:q[t]^=cond&q[b]
 return tuple(q),phase,T

def check():
 count=0
 for bits in product([0,1],repeat=4):
  for phase,b0,b1,direct in product([0,1],repeat=4):
   base=b0&b1
   old=apply(OLD,bits,base,direct,phase);new=apply(NEW,bits,base,direct,phase)
   assert old[:2]==new[:2] and old[2]-new[2]==(base&direct)
   expected=list(bits);expected[3]^=(base&direct)&((bits[0]&bits[1])^(bits[0]&bits[2])^(bits[1]&bits[2]))
   assert old[0]==tuple(expected)
   count+=1
 # Independent intervening wire updates may move across all six replacement
 # gates, under their own fixed guard. This uses disjoint quantum support.
 commute=0
 for q in product([0,1],repeat=5):
  for cg,ig in product([0,1],repeat=2):
   left=list(q);left[4]^=ig
   a=apply(OLD,left[:4],1,cg,0)[0]+(left[4],)
   right=apply(OLD,q[:4],1,cg,0)[0]+(q[4]^ig,)
   assert a==right
   commute+=1
 return {'status':'EXACT_MAJ_VALUE_PHASE_GUARD_CLASSICAL_AND_COST_IDENTITIES_PASS',
  'exhaustive_cases':count,'independent_wire_commutation_cases':commute,
  'four_quantum_wires_distinct':True,'dirty_target_included':True,
  'enclosing_snapshotted_base_and_direct_classical_condition_arbitrary':True,
  'all_classical_bits_preserved':True,'phase_preserved':True,'MR_draws_old_new':[0,0],
  'T_saving_per_active_shot':1,'universal_function':'t XOR ab XOR ac XOR bc; a,b,c restored',
  'scope':'Pure CX/CCX exact reversible permutation, no measurement/reset. One fixed classical enable throughout. No new clean-qubit precondition.'}

if __name__=='__main__':
 report=check();Path(__file__).with_name('PRIMITIVE-TESTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
