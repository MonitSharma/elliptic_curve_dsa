import hashlib,json
from pathlib import Path
import z3
r=Path(__file__).resolve().parent;(r/'smt').mkdir(exist_ok=True)
a,b,c=z3.Bools('addend original_target incoming_carry');majority=lambda x,y,z:z3.Or(z3.And(x,y),z3.And(x,z),z3.And(y,z));s=z3.Xor(z3.Xor(a,b),c)
solver=z3.Solver();solver.add(majority(a,b,c)!=majority(a,z3.Not(s),c));assert solver.check()==z3.unsat
query=solver.to_smt2();(r/'smt/carry_from_completed_sum.smt2').write_text(query)
(r/'LOCAL-LEMMA.json').write_text(json.dumps({'status':'COMPLETED_SUM_CARRY_IDENTITY_UNSAT','solver':z3.get_version_string(),'query_sha256':hashlib.sha256(query.encode()).hexdigest(),'scope':'Only the local carry identity. Whole Rust pebbling, all measurements and allocation require separate native tests; no formal point-add proof.'},indent=2)+'\n')
print('Completed-sum carry identity UNSAT.')
