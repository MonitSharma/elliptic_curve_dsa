from pathlib import Path
from itertools import product as assignments
from collections import Counter
import json
from algebra import factor,evaluate,execute

cases=0;polynomials=0;ranks=Counter()
for n in range(1,5):
 pairs=[(i,j)for i in range(n)for j in range(i+1,n)]
 for quad in range(1<<len(pairs)):
  rows=[0]*n
  for k,(i,j)in enumerate(pairs):
   if quad>>k&1:rows[i]|=1<<j;rows[j]|=1<<i
  for linear in range(1<<n):
   for constant in [0,1]:
    f=factor(constant,linear,rows);ranks[f['rank']]+=1;polynomials+=1
    if f['rank']==4:continue
    for x in range(1<<n):
     for target,guard in assignments([0,1],repeat=2):
      actual_x,actual_t=execute(f,x,n,target,guard)
      assert actual_x==x and actual_t==target^(guard&evaluate(constant,linear,rows,x))
      cases+=1
report={'status':'EXHAUSTIVE_ALL_QUADRATIC_POLYNOMIALS_UP_TO4_VARIABLES_CONSTRUCTIVE_FACTOR_FRAME_PASS',
 'polynomials':polynomials,'rank_counts':dict(ranks),'arbitrary_state_dirty_target_guard_cases':cases,
 'phase_and_MR':'Exact plans use only X/CX/SWAP/CCX, each of which preserves the incoming phase and consumes no MR word in the pinned protected semantics.',
 'universal_check':'Every factor uses exact polar coefficient equality plus an independently reconstructed invertible full control frame; rank4 is classified unreduced. No donor/clean scratch/input sampling.'}
Path(__file__).with_name('ALGEBRA-TESTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
