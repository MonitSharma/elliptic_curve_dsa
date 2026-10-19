"""Unbounded-integer SMT checks for the cofactor decoder's admitted domain."""
import hashlib,json
from pathlib import Path
import z3
r=Path(__file__).resolve().parent;out=r/'smt';out.mkdir(exist_ok=False)
results=[]
def check(name,conditions,counterexample,expected):
 s=z3.Solver();s.set(timeout=10000);s.add(*conditions,counterexample)
 text=s.to_smt2();(out/(name+'.smt2')).write_text(text,encoding='utf-8')
 verdict=s.check();assert str(verdict)==expected,(name,str(verdict))
 row={'name':name,'verdict':str(verdict),'smt_sha256':hashlib.sha256(text.encode()).hexdigest()}
 if verdict==z3.sat:row['witness']=str(s.model())
 results.append(row)

k,j=z3.Ints('k j');c=8*k;d=2*j+1
for s0 in range(2):
 for s1 in range(2):
  for s3 in range(2):
   q=7-2*s0-4*s1-8*s3;newc=c+q*d
   ds0=(1+newc/2+d/2)%2;ds1=(1+newc/4+d/4)%2
   check(f'forced-{s0}{s1}{s3}',[],z3.Or(ds0!=s0,ds1!=s1),'unsat')
for e in range(3,7):
 newd=(1<<e)*d
 b3=(newd/8)%2;b4=(newd/16)%2;b5=(newd/32)%2
 k2=z3.If(z3.And(b3==0,b4==0),1,0)
 k1=z3.If(z3.And(b3==0,z3.Or(b4==1,b5==0)),1,0)
 check(f'exponent-{e}',[],z3.Or(k1!=(e-3)%2,k2!=(e-3)//2),'unsat')
q=z3.Int('q');e=z3.Int('e')
check('odd-cofactor-after-update',[q%2==1],(c+q*d)%2!=1,'unsat')
check('first-step-admission-is-necessary',[],(1+(2+7*d)/2+d/2)%2!=0,'sat')
result={'status':'UNBOUNDED_INTEGER_DECODER_PROOFS_PASS','solver_version':z3.get_version_string(),
 'queries':results,'positive_queries_unsat':13,'negative_control_sat':True,
 'scope':'C divisible8, D odd, e3..6; supports the native codec admission. No allocation bound, complete circuit, endpoint, normalization or phase theorem for surrounding arithmetic.'}
(r/'SMT-PROOF-RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
