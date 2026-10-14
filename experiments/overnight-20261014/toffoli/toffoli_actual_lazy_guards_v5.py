"""Exact source-order/guard truth proof for lazy c4 and TT cleanup."""
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

here = Path(__file__).parent
proof = json.loads((here / 'actual-lean-direct-v3.json').read_bytes())
assert proof['domain_rows'] == 16384 and all(proof['exact_phase_checks'].values())
rows = []
for m6, m3, m5, my in itertools.product(range(2), repeat=4):
    need4 = m6 | m3
    assert (not m6 or need4) and (not m3 or need4)
    need_tt = 0
    builds = []
    for measured in [m3, m5, my]:
        builds.append(measured & (1 ^ need_tt))
        need_tt |= measured
        assert not measured or need_tt
    assert sum(builds) == (m3 | m5 | my)
    old = 4 + 2 * m6  # c1/c2,c3,TT plus conditionalc4/c5.
    new = 2 + need4 + sum(builds) + m6
    rows.append(dict(m6=m6, m3=m3, m5=m5, my=my, need_c4=need4,
                     TT_builds=builds, TT_erase_guard=need_tt, old_ANDs=old, new_ANDs=new))
mean_delta = Fraction(sum(row['new_ANDs'] - row['old_ANDs'] for row in rows), 16)
assert mean_delta == Fraction(-7, 8)
record = {
    'status': 'exact_all16_guardpatterns_and_sourceorder_verified_native_pending',
    'direct_phase_proof_sha256': hashlib.sha256((here / 'actual-lean-direct-v3.json').read_bytes()).hexdigest(),
    'phase_domain_rows': 16384, 'guard_rows': rows,
    'measurement_scope': 'm6(C6),m3(T3),m5(Y5),my(Y3loan) are independent HMR outcomes; no outcome selection.',
    'source_order': ['erase14tables; c1/c2 rebuilt, zeroTT/C4targets allocated',
                     'measureC6 and retainm6 without immediatephase correction',
                     'erase sign,T5,T4 whileT3/Y5/Y4/Y3loan/R3 held',
                     'measureT3 andretainm3; allits operands stillheld',
                     'buildC4 underOR(m6,m3), usingheld final3/Y3loan',
                     'm6: oneconditionalfactor AND andquadraticC6 repair',
                     'm3: lazyTTbuild ifneeded, exactquadraticT3 repair',
                     'eraseC4 underitsORguard beforeY3loan measured',
                     'measureY5, lazyTTbuild underitsMR ifneeded, CZ(TT,final5)',
                     'eraseY4; measureY3loan, lazyTTbuild ifneeded, majority+g*final3 phase',
                     'eraseR3/R2/R1; eraseTT underpersistentneed; ordinarylowwrites/carrycleanup'],
    'lifetime': 'Only C6 repair moves past sign/T5/T4/T3 erasures; C6 repair reads final4/final5,a4/a5,C4 and temporaryfactor, all unchanged. T3 correction reads R3,Y3loan,C4,k1/k2/TT, all held. C4 erases beforeY3loan. TT held afterfirstbuild throughlastTT phase use.',
    'expected_rebuild_ANDs': {'old': '5', 'new': '33/8', 'new_minus_old': '-7/8',
                              'C4_build_probability': '3/4', 'TT_build_probability': '7/8', 'C6_factor_probability': '1/2'},
    'emitted_rebuild_AND_delta': 1,
    'limits': 'Native wire mapping, allMR composition, classicalmutableguard handling and caller applicability remainpending. Fin3 only initially; fin4/top1 all18 producer domain must be tested separately. No whole record.',
    'qualified_score': None,
}
(here / 'actual-lazy-guards-v5.json').write_bytes((json.dumps(record, indent=2) + '\n').encode())
print(json.dumps({'status': record['status'], 'guardpatterns': 16, 'prospective_mean_delta': str(mean_delta)}))
