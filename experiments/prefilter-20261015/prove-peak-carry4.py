from pathlib import Path
import itertools,json,hashlib
r=Path(__file__).parent
# Five data bits A,B,C,D,E; original clean scratch Z, old MR classical bit M.
old=[('ccx',0,1,5),('cx',2,0),('cx',2,5),('cx',2,1),('cx',5,3),('cx',5,0),('ccx',0,3,4),('cx',5,0),('cx',5,4),('cx',5,3),('cx',0,4),('cx',0,3),('cx',5,3),('cx',2,5),('cx',2,1),('cx',2,0),('hmr',5),('czm',0,1)]
new=[('cx',2,3),('x',3),('ccx',2,3,4),('x',1),('ccx',0,1,2),('ccx',2,3,4),('cx',2,3),('x',3),('ccx',0,1,2),('x',1)]
def simulate(ops,data,m,base,oldm,phase,dirtyz=0):
 q=list(data)+[dirtyz];cl=oldm;p=phase
 for row in ops:
  if not base:continue
  kind,*w=row
  if kind=='x':q[w[0]]^=1
  elif kind=='cx':q[w[1]]^=q[w[0]]
  elif kind=='ccx':q[w[2]]^=q[w[0]]&q[w[1]]
  elif kind=='hmr':cl=m;p^=q[w[0]]&m;q[w[0]]=0
  elif kind=='czm':p^=cl&q[w[0]]&q[w[1]]
  else:raise AssertionError(kind)
 return q,cl,p
cases=0;dirty_counterexamples=0;phase_faults=0;new_faults=0
for data in itertools.product(range(2),repeat=5):
 for m,base,oldm,phase in itertools.product(range(2),repeat=4):
  a,am,ap=simulate(old,data,m,base,oldm,phase);b,bm,bp=simulate(new,data,m,base,oldm,phase)
  assert a[:5]==b[:5] and a[5]==b[5]==0 and ap==bp==phase
  A,B,C,D,E=data;f=A&(1^B);expected=list(data)
  if base:expected[3]^=f;expected[4]^=f&(D^C^1)
  assert a[:5]==expected
  dz,_,_=simulate(old,data,m,base,oldm,phase,dirtyz=1);dirty_counterexamples+=dz[:5]!=b[:5]
  _,_,fp=simulate(old[:-1],data,m,base,oldm,phase);phase_faults+=fp!=ap
  fault=new[:4]+new[5:];fq,_,_=simulate(fault,data,m,base,oldm,phase);new_faults+=fq[:5]!=b[:5]
  cases+=1
assert cases==512 and dirty_counterexamples and phase_faults and new_faults
report=dict(status='EXACT_ALL_BOOLEAN_INPUT_AND_MEASUREMENT_VALUE_PHASE_IDENTITY_WITH_CLEAN_Z',data_inputs=32,measurement_outcomes=2,incoming_base_masks=2,incoming_classical_m_values=2,incoming_phases=2,total_cases=cases,source_toffoli_per_active=2,replacement_toffoli_per_active=4,delta_toffoli_per_active=2,original=old,replacement=new,formula='f=A & !B; A,B,C unchanged; Dnew=D^f; Enew=E^(f&(D^C^1))',dirty_scratch_negative_cases=dirty_counterexamples,missing_phase_correction_fault_cases=phase_faults,missing_replacement_toffoli_fault_cases=new_faults,required_preconditions=['five data wires distinct','removed scratch initially0','common unchanged classical scope/base for whole region','originalMRclassicaloutput has no downstream live use before overwrite'],not_proved=['actual4b source matching','downstream classical-M death','complete circuit width1233','scored product improvement'])
(r/'evidence/peak-carry4-boolean-proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['original','replacement']}))
