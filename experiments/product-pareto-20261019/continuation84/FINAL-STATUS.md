# 84-stage continuation: final gate failed, ineligible

The run completed on19October2026. All84 independent exact-transformation
audits passed. Native generation reproduced the exact final stream, with
Q1234, four source-binding tests passing and protected files unchanged.
Stream SHA256: `93341e8f0a96970c0cbe8225f100148e10e44dc819de8f06c075d64597319d5a`.

The single predeclared census `pareto-parent84-gate-20261019-v1` used32768
batches of64 shots per circuit. Its final verdict is **FAILURE_GATE_FAIL**.

| Criterion | Candidate | Exact public parent |
|---|---:|---:|
| Value-failing shots | 3696 | 3696 |
| Failed batches | 4225 | 4229 |
| Failed batches per9024-shot packet | 18.180084 | 18.197296 |
| Dirty-ancilla shots | 0 | 0 |

Paired newly failing/passing batches348/352; one-sided exact McNemar
p0.574938. Three criteria passed, but the absolute candidate failure limit18
did not. The parent's rate on this census does not waive that limit.
Never resample this candidate to reverse the verdict. No nonce search,
official benchmark or submission follows.

Diagnostic paired mean Toffoli saving:5.354970 ±0.577743 (standard error).
Candidate mean761088.112412, parent761093.467382. These are not scored results.
The small total gain also argues against continuing the same cache chain.

All sources, patches, streams, census rows and logs remain on the server.
Audit result, native receipt and gate declaration/result are saved locally.
The distinct smaller parent4 candidate retains its own passing gate; its
fast-filter transfer proof remains unqualified.
