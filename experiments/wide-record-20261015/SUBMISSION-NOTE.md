# Independent minimum-Toffoli candidate: 753745 T at Q1464

This candidate targets the independent executed-Toffoli record. It does not
improve Q × T. Submission is queued; it has not been sent to ECDSA.fail.

The unchanged official `benchmark.sh` passes all 9024 shots with zero
classical mismatches, phase-garbage batches or ancilla-garbage batches.
Total executed Toffolis: 6801794152; mean: 753744.9193262411; rounded:753745.
Peak logical qubits:1464. Q × T:1103482680. The refreshed public Toffoli
minimum remains753771/Q1464 (source5a7c3902, submission3f32acd2), so this
complete local reproduction improves that independent record by26 T.

Base revision:5a7c390233c72133df9b591c92e43422c5892142. Changes are confined
to nine files under `src/point_add/`: four exact retained-expression/cache
passes and the identity-tail nonce. Repeated products use existing clean
scratch, preserving width. Native phase/value tests pass21/21, including
dirty inputs, all guarded event patterns and a deliberate phase-fault
negative control. Complete event-aligned original-to-final reconstructions
agree on every quantum/classical word, phase and scratch on512 fixed inputs.
Inherited arithmetic limitations remain; this is not an all-input proof.

Identity-tail nonce:**92**. Policy:ascending from1, lowest passing nonce,
independent of its resource count. **164 nonces screened**; all1–91 fail.
Extra screened nonces come from parallel in-flight work. The selected nonce
also passes the protected official replay before the unchanged benchmark.
No content, cut, table or resource setting was tuned to a packet.

Fresh-input failure disclosure:

| Sample | Shots per source | Parent failed batches | Candidate failed batches | Expected candidate failures /9024 shots |
|---|---:|---:|---:|---:|
| Pre-search, fixed label `wide-frozen-four-stage-20261015` |262144|155/4096|155/4096|5.335693359375|
| Final, predeclared label `wide-four-stage-final-20261015` |1048576|678/16384|674/16384|5.8004150390625|

The final paired parent rate is5.8348388671875 per packet. Candidate wrong
value shots:588; phase-failing shots:366; dirty shots:0. All sample rows are
retained, including failures. The small rate difference is sampling evidence,
not a claimed failure-rate repair. Both samples meet the paired-parent gate
and community cap18. Final diagnostic paired saving:23.065684 +/-0.398086 T.

Final op-stream SHA256:
`ba9bd28402c5821e5dcb36795003f3ee5fe729bc2a071a9942567ce875ed02be`.
Final point-add patch SHA256:
`2586ec9d711e7d382490cae95e46cfcbfdf01446f0cd4d4cb03174b7a99d8d89`.
All tracked files outside `src/point_add/` were hash-checked against the base
before and after the benchmark. Full patch, sources, benchmark, tests,
nonce-screen log, both censuses and hashes are preserved in `evidence.tar.gz`
and `RESULT.json`.
