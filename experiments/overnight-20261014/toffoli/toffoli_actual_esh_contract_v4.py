"""Exact top1/direct/nondeep ESh producer contract, before native admission."""
import hashlib
import itertools
import json
from pathlib import Path

root = Path(__file__).resolve().parents[3]
here = Path(__file__).parent
source = (root / 'agents/product/src/point_add/y15_onefold.rs').read_bytes().replace(b'\r\n', b'\n')
assert hashlib.sha256(source).hexdigest() == '879b85060f6a5cfa412561d64860f1cab697f7a334f180f5be9102070d5a23b9'
text = source.decode()
out = text[text.index('fn esh_out('):text.index('/// Build the six wires again')]
restore = text[text.index('fn esh_in('):text.index('/// y18-next, trace only')]
assert 'if st.top1 {' in out and 'if !st.top1 {' in restore and 'if !st.direct {' in restore
def maj(a, b, c):
    return (a & b) ^ (a & c) ^ (b & c)
counts = [0] * 8
states = []
for raw in range(128):
    x0, x1, top, b1, b2, b3, lowcarry = [(raw >> i) & 1 for i in range(7)]
    q2 = maj(top, b3, lowcarry)
    q1 = maj(x0, b2, q2)
    e2 = maj(x1, b1, q1)
    e0, e1 = x0 ^ b2 ^ q2, x1 ^ b1 ^ q1
    # Actual top1 esh_out undoes the sums before erasing each majority.
    u1, u0 = e1 ^ q1 ^ b1, e0 ^ q2 ^ b2
    assert (u0, u1) == (x0, x1)
    assert e2 == maj(u1, b1, q1)
    assert q1 == maj(u0, b2, q2)
    assert q2 == maj(top, b3, lowcarry)
    # All three HMR correction coefficients are their exact held functions.
    assert all((m0 * (e2 ^ maj(u1, b1, q1)) ^
                m1 * (q1 ^ maj(u0, b2, q2)) ^
                m2 * (q2 ^ maj(top, b3, lowcarry))) == 0
               for m0, m1, m2 in itertools.product(range(2), repeat=3))
    n2 = maj(top, b3, lowcarry)
    n1 = maj(u0, b2, n2)
    nE2 = maj(u1, b1, n1)
    assert (u0 ^ b2 ^ n2, u1 ^ b1 ^ n1, nE2) == (e0, e1, e2)
    counts[e0 | e1 << 1 | e2 << 2] += 1
    states.append([raw, e0, e1, e2, q1, q2])
assert all(counts)
record = {
    'status': 'exact_top1_direct_nondeep_producer_algebra_verified_native_pending',
    'source_lf_sha256': hashlib.sha256(source).hexdigest(),
    'esh_out_source_sha256': hashlib.sha256(out.encode()).hexdigest(),
    'esh_in_source_sha256': hashlib.sha256(restore.encode()).hexdigest(),
    'independent_input_order': ['x256_before_add2_sums', 'x257_before_add2_sums', 'tg255', 'b255', 'b254', 'b253', 'cq253'],
    'producer_rows': 128, 'all_E_output_counts': counts,
    'producer_state_sha256': hashlib.sha256(json.dumps(states, separators=(',', ':')).encode()).hexdigest(),
    'all_out_measurement_patterns': 8,
    'domain': 'direct=true,top1=true,deep_c empty; seven retained independent producer inputs, three derived majority carries; fold window excludes tg255 and source upper bits',
    'reconstruction': 'esh_out first removes E0/E1 sums, then erases x258,cq1,cq2. esh_in restores cq2,cq1,x258 and rewrites E0/E1 sums, reproducing all original E bits.',
    'prospective_schedule': 'Erase14 Y16 table helpers using source-proved c3/E-free operands; restore three ESh majority targets; rebuild c1/c2,TT,c4; then use the independently verified fin3 remainder.',
    'postladder_space_ledger': {'table_helpers_freed': 14, 'ESH_targets_rebuilt': 3,
                              'c1_c2_TT_c4_targets': 4, 'conservative_extra_conditional_temporary': 1,
                              'remaining_margin_vs_before_table_erase': 6},
    'limits': 'The algebra admits only the stated ESh producer interface. Physical IDs can be reused after ESh erasure; old E IDs must not be interpreted as live E values. Fresh-wire mapping, caller flags, freelist peak, incoming phase and all retained garbage still require native proof. No fin4 native or full score claim.',
    'qualified_score': None,
}
(here / 'actual-esh-contract-v4.json').write_bytes((json.dumps(record, indent=2) + '\n').encode())
print(json.dumps({'status': record['status'], 'producer_rows': 128, 'all_E_output_counts': counts,
                  'postladder_margin': 6}))
