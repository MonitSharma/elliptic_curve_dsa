"""Boolean identities only; not a formal verification of Rust/point addition."""
import hashlib,json
from pathlib import Path
import z3
r=Path(__file__).resolve().parent;(r/'smt').mkdir(exist_ok=True)
a,d,b,e,c=z3.Bools('lower_add upper_add lower_target upper_target incoming_carry')
X=lambda *args: __import__('functools').reduce(z3.Xor,args)
A=lambda *args:z3.And(*args)
maj=lambda x,y,z:z3.Or(A(x,y),A(y,z),A(z,x))
actual=maj(d,e,maj(a,b,c))
generic=X(A(d,e),A(X(d,e),a,b),A(X(d,e),X(a,b),c))
forms={
 'generic_two_CCZ':(z3.BoolVal(True),generic),
 'same_literal_one_CCZ':(d==a,X(a,A(X(e,a),X(b,a),X(c,a)))),
 'opposite_literal_one_CCZ':(d==z3.Not(a),X(e,A(z3.Not(X(e,a)),X(b,a),X(c,a)))),
 'constant_lower_zero_one_CCZ':(a==False,X(A(d,e),A(X(d,e),b,c))),
 'constant_lower_one_one_CCZ':(a==True,X(A(d,e),A(X(d,e),b),A(X(d,e),c),A(X(d,e),b,c))),
 'constant_upper_zero_one_CCZ':(d==False,X(A(e,a),A(e,X(b,a),X(c,a)))),
 'constant_upper_one_one_CCZ':(d==True,X(e,a,A(e,a),A(z3.Not(e),X(b,a),X(c,a))))}
rows=[]
for name,(cond,formula)in forms.items():
 s=z3.Solver();s.add(cond,actual!=formula);query=s.to_smt2();assert s.check()==z3.unsat
 (r/'smt'/(name+'.smt2')).write_text(query,encoding='utf8');rows.append({'name':name,'result':'unsat','sha256':hashlib.sha256(query.encode()).hexdigest()})
s=z3.Solver();s.add(actual!=z3.Not(generic));assert s.check()==z3.sat
(r/'smt/negative_wrong_phase_sign.smt2').write_text(s.to_smt2(),encoding='utf8')
(r/'LOCAL-LEMMAS.json').write_text(json.dumps({'status':'SEVEN_BOOLEAN_IDENTITIES_UNSAT_WRONG_SIGN_CONTROL_SAT','solver':z3.get_version_string(),'queries':rows,'negative_control_model':str(s.model()),'scope':'Boolean phase polynomials only. Native tests separately check parity materialization, full ladder, measurements and workspace.'},indent=2)+'\n')
print('Seven identities UNSAT; negative control SAT.')
