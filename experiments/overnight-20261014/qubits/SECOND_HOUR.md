# Original transcript and wider reciprocal components

These are research diagnostics, with no qualified score. The preserved compact
submission and protected harness remain unchanged.

## Complete original failure transcript

The external original-transcript evaluator completed with exit 0 on 2026-10-14
at approximately 11:43 UTC. Its process was 2359071 (wrapper 2358879), elapsed
25:54.55, peak RSS 61,714,312 KiB. It replayed all 9,024 original inputs and the
contiguous original measurement RNG transcript against the preserved compact
stream, rather than reseeding each batch. The exported packet is byte-identical
to the earlier packet, SHA256
`fbeaf4f6dd9584527f974d49244d0a3af69f3f1370ef7cbe25e603061f90ba6e`.

| Batch | Failing shot | Phase nonzero | Dirty ancilla lanes |
|---|---|---|---|
| 18 | 1170 | false | 22 |
| 30 | 1937 | false | 34 |
| 58 | 3713 | true | 45 |
| 64 | 4131 | true | 33 |
| 65 | 4202 | false | 20 |
| 125 | 8048 | true | 29 |

This reproduces the historical six classical mismatches, three phase batches
and six ancilla batches. Its exit 0 means the diagnostic successfully collected
the failed trajectory. It is not a passing benchmark. The independent paired
diagnostics use a separate fixed per-batch RNG domain and have different phase
patterns; those results must not be substituted for this original transcript.

The newly localized sixth input, shot 3713, was not flagged by the independent
integer reciprocal or valuation model. A separate paired batch-58 replay
completed with exit 0: both clean base and compact fail that input alone.
The base has phase0 and28 dirty ancilla lanes; compact has phase mask0x2 and
45 dirty ancilla lanes. Its compact wrong output coordinates equal the
original-transcript wrong output for this input. All six observed classical
mismatch inputs therefore also fail the base stream under paired inputs.
This does not establish equal intermediate states or identify the sixth cause.

## Arbitrary-remainder and K32 component evidence

The compact restoring step has two invariant domains for normalized odd
`D` of width `k`. For `R<D`, it maps to `(2R+1) mod D`. For `R=D+u`, it maps to
`D + ((2u+1) mod (2^k-D))`. Both moduli are odd and both maps have explicit
inverses. This extension matters because inactive borrowed remainder lanes can
contain unrelated data. Assuming an unconditional remainder modulo D outside
the valid domain is false, as the preserved solver counterexamples demonstrate.

The solver script proves the partition and inverse for widths 2–8, 16, 24, 25
and 32 (UNSAT for the proposed counterexamples), with SAT negative controls for
the invalid unconditional-mod-D assertion. The proof report completed, but its
first quick-launch wrapper did not record an exit marker; no measured wrapper
exit is claimed.

Native emitted-gate tests completed with exit 0 at 11:36:51 UTC. They cover
21,844 exhaustive normalized odd-divisor/arbitrary-remainder cases at widths
2–8 and 256 cases of a 693-wire K32 V fixture. The fixture borrows Q121–Q127,
includes mixed active/inactive lanes and arbitrary dirty remainder/passengers,
checks the active integer result and inactive identity, and checks all-wire
inverse restoration and zero phase. These particular primitives contain zero
measurement coefficients. This is unitary component evidence, not a test of
the complete column's measurement phase or a complete borrowed-lane schedule.

The isolated source patch and manifest are `component-dirty-k32.patch` and
`component-dirty-k32-manifest.json`. It adds tests to preserved compact source;
the middle's integrated arithmetic is still K24. Caller ownership, full-SY
partition and changed-source column tests remain required before integration.
