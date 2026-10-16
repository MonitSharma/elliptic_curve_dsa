# Exact source seed restoration

The candidate restores every inherited CCX-to-CX reduction inside every source
`mod_halve_pm` helper. This source-defined family contains one edit. It adds
exactly one Toffoli and no qubits, classical bits, measurements or operations.
Every other operation, including every physical measurement position and the
identity tail, is byte-identical to the original public 4b circuit.

The complete helper has an exact BDD proof for all 256-bit target inputs and all
96 measurement outcomes: it implements the finite 53-bit source formula,
restores all 48 required clean scratch wires, and cancels phase. An independent
hash-pinned whole-prefix support replay proves those 48 wires zero for every
symbolic ABI input and measurement. No dirty-scratch or ideal full-modulus
halving claim is made. The inherited helper remains a negative control with
both value and phase errors. Independent read-only review passes.

The native stream SHA256 is
`a996cf16d64b11a20cb9a56d0688d034153f843751f640ea7113f50739c20608`.
Native guards and 262144 protected full-state/phase/MR cases pass.
The source archive `native-source-freeze-v1.tar.gz` verifies all 207 members,
SHA256 `7b1b9452aade402546069fa2143b389edcd13d7f940a92f1384852437446b582`.

The sole fixed fresh paired gate is terminal and negative: 32768 batches of
64 shots per source, original parent first and candidate second, using label
`public4b-all-seed-dropped-control-restore-independent-20261016-v1`.
Both sources have 4214 failing batches and 4523 failing shots: 3622 value,
2723 phase and zero dirty shots. Their measured rate is
18.13275146484375 failed batches per 9024-shot packet, exceeding the cap of 18.
No failure-status repairs or regressions were observed. Every batch costs
exactly 64 additional Toffolis, or one per shot. This is not a claim that all
incorrect quantum outputs were identical.

The comparative count is equal, but the strict gate fails the cap. There is
no resampling, nonce search, submission or seed cache composite. The source
primitive diagnosis and proofs remain valid; no census improvement or resource
record is demonstrated.

`terminal-v1.tar.gz`, SHA256
`10b984fdd3fd878b75882b5cbb7c7eec8d3684f61d6b7388e751b796d81cef7f`,
contains all 32768 raw rows for each source, fixed-label/provenance data,
checker binary and source, terminal summary and logs. All 44 members and two
base archive pins verify locally; both large streams are explicit external
server files. An independent complete raw recount in
`terminal-v1-local-verification.json` agrees with every reported count.
