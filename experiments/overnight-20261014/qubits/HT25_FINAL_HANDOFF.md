# Final qubit research handoff (2026-10-14 20:02 UTC snapshot)

No new qualified resource record has been established. The complete N275-v2 and
headflag benchmarks failed and their evidence remains preserved by the
coordinator. The unchanged clean c95 primitive reproduces the independent
shot2379 quotient-capacity failure; that result has expected-negative scope.

HT25-v9 passed its 16 native tests and 576 exact measurement-phase instances.
Its frozen full generation completed with native and wrapper exit0:
N=2,499,445,456, maximum referenced quantum width692, compressed4,723,526,209 bytes,
SHA256 `3b64970ffab83deb99c0f74d6277879f3ec33d157a765b5f47ba7bd6f3ea7e1d`.
These are stream diagnostics. The coordinator chose not to grade V9 so that one
full benchmark can assess the separately proved bank-transfer variant.

Bank-transfer-v2 passed 17 native tests and 17 independently selected exact
phase tests comprising 704 fixed-lane audit instances. Its component receipt
and independent review bind patch
`61bd0d94831feea58dee9fc1c6a9cc2db10ed32e9a65f95ed5ebfe33a9a32f43`.
The source restores public mixed-HR capacity23, adds HT storage25 and conditional
32-bit precision, and preserves explicit expected-negative q>=2^25 cases.
The tests do not establish all-curve admission or a general quotient bound.

The following authorized jobs continue under
`/home/hclau/ecdsa_research/overnight-20261014/qubits`:

- Bank generation wrapper2802421: `evidence/ht25-bankswap-v2-full-build.log`,
  `.pid`, `.exit`. Limit16GiB virtual, four build threads, one runtime thread;
  dedicated target and exact external stream. It performs no operation-vector
  allocation or grading. The frozen pending receipt is explicitly timed.
- Coordinator-launched conditional grading queue2805813:
  `evidence/ht25-bankswap-v2-official-cycle.log`, `.pid`, `.exit`. It waits up to
  24 hours for generation, then requires source, serializer, native, exact-phase,
  parser count, actual width, stream hash, protected-harness, actual capacity,
  memory and sole-evaluator-lock guards before one unchanged 9024 benchmark.
  No other full grading run is authorized by this queue.

The queue reuses the unused pristine c95 protected evaluator in
`harness-ht25-v9`, binary SHA256
`88b6fd33dfcd85b317ed6694c10715dbb6b4d5926838400ec7c4e23cdda77e3a`.
Historical outputs are sparse-excluded. The external stream is symlinked only
after admission; the candidate's empty stream placeholder cannot be scored.
Allocation requires N*56 bytes plus16GiB below both the 256GiB virtual cap and
fresh available memory. Unrelated server calculations are preserved.

Terminal collection rechecks source/actual diff, stream and binary, preserves
both native and wrapper exits, copies only fresh outputs, and leaves
`qualified_score=false` pending coordinator review of all9024 failure channels
and score artifacts. Conditional-queue source is frozen after approval.

Versioned failed preparations and arithmetic attempts are retained. The first
protected-harness launcher compiled successfully but ended with wrapper127 due
to a trailing carriage-return command; its exact server bytes are compressed.
The LF correction completed0 using the existing Cargo artifact. V9 generation
actually completed0 with an LF server launcher; no bookkeeping failure is
attributed to it. Completed raw logs and exact launcher archives carry their own
hash indexes. Active streams are not hashed or represented as complete results.
