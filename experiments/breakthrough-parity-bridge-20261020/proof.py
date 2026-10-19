"""Local Boolean lemmas for the mixed-ladder induction, separate from native tests.

These prove gate identities on all one-bit inputs. They are not a formal proof
that the complete point-add source or every arbitrary-width emitted stream is
correct. Native source selection and call admission remain separately audited.
"""
import hashlib,json
from pathlib import Path
import z3
r=Path(__file__).resolve().parent;(r/'smt').mkdir(exist_ok=True)
a,b,p,m=z3.Bools('a b incoming_carry measurement_outcome')
xor=lambda *args:z3.Xor(*args)if len(args)==2 else z3.Xor(args[0],xor(*args[1:]))
maj=z3.Or(z3.And(a,b),z3.And(a,p),z3.And(b,p))
bb=xor(b,a);pp=xor(p,a);aa=xor(a,z3.And(bb,pp))
restored_a=xor(aa,z3.And(bb,pp))
restored_p=xor(pp,restored_a)
sum_b=xor(bb,restored_p)
queries={
 'borrowed_maj_contains_exact_carry':aa!=maj,
 'borrowed_uma_restores_source_and_carry_and_writes_sum':z3.Or(restored_a!=a,restored_p!=p,sum_b!=xor(a,b,p)),
 'measured_gidney_carry_contains_exact_majority':xor(z3.And(xor(a,p),xor(b,p)),p)!=maj,
 'measured_and_phase_correction_cancels_for_every_outcome':xor(z3.And(m,z3.And(xor(a,p),xor(b,p))),z3.And(m,xor(a,p),xor(b,p)))
}
rows=[]
for name,counterexample in queries.items():
    solver=z3.Solver();solver.add(counterexample)
    smt=solver.to_smt2();path=r/'smt'/(name+'.smt2');path.write_text(smt,encoding='utf8')
    outcome=solver.check();assert outcome==z3.unsat,(name,outcome)
    rows.append({'name':name,'result':str(outcome),'query_sha256':hashlib.sha256(smt.encode()).hexdigest()})
# The phase lemma must detect removing its correcting CZ.
negative=z3.Solver();negative.add(z3.And(m,xor(a,p),xor(b,p)))
(r/'smt/negative_missing_cz.smt2').write_text(negative.to_smt2(),encoding='utf8')
assert negative.check()==z3.sat
result={'status':'FOUR_LOCAL_BOOLEAN_LEMMAS_UNSAT_AND_MISSING_CZ_CONTROL_SAT','solver':z3.get_version_string(),
    'queries':rows,'negative_missing_cz':str(negative.model()),
    'induction_argument':['Exclusive pivot materialization is an invertible CNOT basis change, because no selected pivot appears in another row or aliases target/carry-in.',
        'Every borrowed MAJ stores the exact next carry. Every ordinary measured stage stores the same carry on a fresh wire.',
        'Reverse order restores the following carry before its predecessor is processed. The borrowed UMA restores both source and incoming carry while writing the correct sum.',
        'A measured AND is cleared only after removing its incoming-carry XOR. Its CZ applies the identical measurement phase and cancels it.',
        'Final inverse basis change restores every source/control wire. The top sum uses the existing direct CCX identity.'],
    'scope':'Local gate lemmas and a written induction argument, not a machine-checked proof of arbitrary Rust control flow or complete point addition.'}
(r/'LOCAL-LEMMAS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
