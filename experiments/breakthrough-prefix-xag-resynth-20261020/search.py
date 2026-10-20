"""Exact reachable-domain XOR/AND synthesis with complete truth verification."""
import hashlib,itertools,json,time
from pathlib import Path
import z3
r=Path(__file__).resolve().parent;dag=json.loads((r/'PREFIX-DAG.json').read_bytes());f={k:int(v,16)for k,v in json.loads((r/'FUNCTIONS.json').read_bytes()).items()};one=f['one'];values=[one]+[f['input'+str(i)]for i in range(14)]
def combine(mask,columns):
 result=0
 while mask:
  bit=mask&-mask;result^=columns[bit.bit_length()-1];mask^=bit
 return result
for _,a,b in dag['gates']:values.append(combine(a,values)&combine(b,values))
cases=json.loads((r/'WINDOWS.json').read_text())['cases'][:3];reports=[]
for index,case in enumerate(cases):
 begin=time.time();columns=[one]+[values[i]for i in case['boundary_columns']];targets=[combine(mask,values)for mask in case['output_forms']];samples=sorted({0,16383}|{(i*257)%16384 for i in range(1,33)});history=[];status='TIME_LIMIT';solution=None
 while time.time()-begin<300:
  n=len(samples);solver=z3.Solver();solver.set(timeout=min(45000,max(1000,int((300-time.time()+begin)*1000))),threads=1);vals=[z3.BitVecVal(sum(((v>>row)&1)<<j for j,row in enumerate(samples)),n)for v in columns];selectors=[]
  def choose(name,available):
   select=z3.BitVec(name,len(available));value=z3.BitVecVal(0,n)
   for j,v in enumerate(available):value=value^z3.If(z3.Extract(j,j,select)==1,v,z3.BitVecVal(0,n))
   return select,value
  for j in range(case['new_gate_budget']):
   sa,a=choose('a'+str(j),vals);sb,b=choose('b'+str(j),vals);solver.add(sa!=0,sb!=0,z3.ULT(sa,sb));g=z3.BitVec('gate'+str(j),n);solver.add(g==a&b);vals.append(g);selectors.append((sa,sb))
  out=[]
  for j,target in enumerate(targets):
   select,v=choose('out'+str(j),vals);solver.add(v==z3.BitVecVal(sum(((target>>row)&1)<<i for i,row in enumerate(samples)),n));out.append(select)
  tick=time.time();answer=solver.check();step={'samples':n,'status':str(answer),'seconds':time.time()-tick};history.append(step)
  if answer==z3.unsat:status='UNSAT_RESTRICTED_INTERFACE_AND_BUDGET';break
  if answer==z3.unknown:status='UNKNOWN_INCOMPLETE_SEARCH';step['reason']=solver.reason_unknown();break
  model=solver.model();gates=[[model.eval(a).as_long(),model.eval(b).as_long()]for a,b in selectors];outputs=[model.eval(s).as_long()for s in out];actual=columns.copy()
  for a,b in gates:actual.append(combine(a,actual)&combine(b,actual))
  wrong=0
  for mask,target in zip(outputs,targets):wrong|=combine(mask,actual)^target
  if not wrong:
   status='SAT_ALL16384_ASSIGNMENTS_VERIFIED_NOT_NATIVE';solution={'gates':gates,'outputs':outputs,'boundary_columns':case['boundary_columns'],'implicit_constant_column':True};break
  counterexamples=[]
  while wrong and len(counterexamples)<32:
   bit=wrong&-wrong;counterexamples.append(bit.bit_length()-1);wrong^=bit
  assert not(set(counterexamples)&set(samples));samples=sorted(set(samples)|set(counterexamples));step['counterexamples']=counterexamples
  (r/('progress'+str(index)+'.json')).write_text(json.dumps({'case':case,'history':history},indent=2)+'\n')
 report={'case':case,'status':status,'solution':solution,'history':history,'seconds':time.time()-begin,'solver_version':z3.get_version_string(),'scope':'Fixed structural windows and full14-input reachable-domain truth functions, no curve or nonce samples. SAT witness independently checked on all16384 assignments. Native phase/workspace and complete point-add tests remain mandatory; UNSAT is limited to this interface, gate budget and candidate language.'};reports.append(report);(r/('case'+str(index)+'.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'case':index,'status':status,'seconds':report['seconds']}),flush=True)
 if solution:break
(r/'RESULT.json').write_text(json.dumps({'status':'FINITE_EXACT_RESYNTHESIS_RESEARCH','cases':reports,'source_hashes':{name:hashlib.sha256((r/name).read_bytes()).hexdigest()for name in['PREFIX-DAG.json','FUNCTIONS.json','WINDOWS.json','search.py']}},indent=2)+'\n')
