"""Independent exhaustive value/phase test of the new retention primitive.

Includes both measurement outcomes, arbitrary target values, and all three
control-pair representations of the same Boolean product. Deliberately omitting
the phase repair must fail. This is not a full-circuit correctness claim.
"""
import itertools
import json
from pathlib import Path

cases = 0
detected_faults = 0
for x, y, t0, t1, measurement in itertools.product(range(2), repeat=5):
    product = x & y
    triple = (x, y, 1 ^ x ^ y)
    for a, b in ((0, 1), (0, 2), (1, 2)):
        later = triple[a] & triple[b]
        assert later == product
        original = (t0 ^ product, t1 ^ later, 0, 0)
        donor = product
        first = t0 ^ donor
        second = t1 ^ donor
        measurement_phase = donor & measurement
        donor = 0
        corrected_phase = measurement_phase ^ (later & measurement)
        actual = (first, second, donor, corrected_phase)
        assert actual == original
        detected_faults += measurement_phase != 0
        cases += 1
assert detected_faults > 0
result = {
    'status': 'RETENTION_TEMPLATE_EXHAUSTIVE_PASS',
    'cases': cases,
    'missing_phase_repair_faults_detected': detected_faults,
    'scope': 'Local primitive only; whole-circuit donor, guard and product proofs remain required.'
}
Path(__file__).with_name('template-test.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
