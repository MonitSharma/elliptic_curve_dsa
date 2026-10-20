"""Local carry/phase Boolean lemmas; not a machine-checked Rust proof."""
import hashlib,json
from pathlib import Path
import z3
r=Path(__file__).resolve().parent;(r/'smt').mkdir(exist_ok=True)
a,b,p,comp=z3.Bools('source_parity target incoming_carry complement')
xor=lambda x,y:z3.Xor(x,y)
literal=xor(a,comp);majority=z3.Or(z3.And(literal,b),z3.And(literal,p),z3.And(b,p))
acc=xor(b,literal);prev=xor(p,literal);stored=xor(literal,z3.And(acc,prev))
restored_literal=xor(stored,z3.And(acc,prev));restored_p=xor(prev,restored_literal);restored_b=xor(acc,restored_literal)
top_phase=xor(z3.And(xor(b,p),xor(literal,p)),z3.Not(p))
queries={
 'borrowed_maj_is_exact_complemented_carry':stored!=majority,
 'inverse_maj_restores_every_data_operand':z3.Or(restored_literal!=literal,restored_p!=p,restored_b!=b),
 'ordinary_carry_matches_same_majority':xor(z3.And(xor(b,p),xor(literal,p)),p)!=majority,
 'top_phase_is_not_carry_including_its_sign':top_phase!=z3.Not(majority)}
rows=[]
for name,bad in queries.items():
    solver=z3.Solver();solver.add(bad);query=solver.to_smt2();assert solver.check()==z3.unsat
    (r/'smt'/(name+'.smt2')).write_text(query,encoding='utf8')
    rows.append({'name':name,'result':'unsat','sha256':hashlib.sha256(query.encode()).hexdigest()})
negative=z3.Solver();negative.add(top_phase!=majority);assert negative.check()==z3.sat
(r/'smt/negative_wrong_global_sign.smt2').write_text(negative.to_smt2(),encoding='utf8')
report={'status':'FOUR_LOCAL_CARRY_PHASE_LEMMAS_UNSAT_WRONG_SIGN_CONTROL_SAT','solver':z3.get_version_string(),'queries':rows,
    'wrong_sign_counterexample':str(negative.model()),
    'scope':'Local complemented-literal and phase identities plus source-exclusivity argument. Does not formally verify arbitrary-width Rust execution, allocator layout or full point addition.'}
(r/'LOCAL-LEMMAS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
