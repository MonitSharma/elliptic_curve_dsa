# Product optimization, 19 October 2026

Research in progress; no new scored result or submission.

## Active long run — launched 10:29 Singapore

PID **443914**, `run-continuation84.sh`, server directory below. This is a
new experiment directly on the exact public product parent, not a resumption
of the historical PRODUCT179 certificate-marker issue. The fixed 84 stages
are declared before generation in `continuation84/DECLARATION.json`.

Checkpoint at **10:38 Singapore**: stages 1–4 generated, stages 1–3 passed
their independent audits, stage 5 generating. The four-product native pilot
has also passed operation-byte identity and Q1234 verification. The extended
candidate and its final gate are still pending.

The pipeline generates a fixed sequence of exact cache extensions, audits
every stage using the existing independent universal cache verifier, ports
the fixed final output into an isolated submission tree, verifies native
generation and protected files, refreshes the public parent, and declares
and runs one 32,768-batch paired failure-rate gate. It stops on any failure.
The final gate label is `pareto-parent84-gate-20261019-v1`; its actual stream
hashes and declaration are written after the native circuit is frozen and
before any census starts. A failed verdict is terminal. No nonce search or
submission is part of this pipeline.

Prior stage timings suggest several hours for the 84 stages; this is an
estimate, not a completion promise. Generation uses one thread, at most two
single-thread audits run alongside it, builds use four threads, and the
final gate uses 16 workers per stream (32 total). New stage launches wait if
available memory falls below 180 GiB, allowing for the job's memory budget.

## Completed evidence in this session

- The public parent's native rebuild is byte-identical to published SHA-256
  `99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683`.
- The primitive value/phase test passes 96 exhaustive cases and detects 12
  cases of a deliberately omitted phase correction.
- Corrected symbolic scanner tests pass, including a regression for late
  input-register annotations and rejection of unknown guards as constants.
- The copy-removal checker rejects changed controls and a measurement with
  an extra reader. It identified **769** removable single-use copies in the
  public parent and **808** in PRODUCT179. This operation saves zero Toffolis
  directly and creates clean donor intervals.
- On the public parent after copy removal, full-expression symbolic checking
  proves **four** new unconditional retained products, at the same Q1234.
  A second discovery method uses fingerprints only to propose pairs and
  full exact local expressions to prove them; it proves three public-parent
  pairs and nine PRODUCT179 pairs, rejecting unproved proposals. These are
  diagnostic circuit transformations, not official resource records.
- The native four-product source in `candidate-parent4` compiles and emits
  exactly the pilot's serialized operation bytes: 17,889,606 operations,
  Q1234, raw SHA3-256
  `97c40ed1dd3f5123c9554ebf29c54c433960804c0effce63dc7bba52844ae9ae`.
  The official generator's compressed stream has SHA-256
  `9f50f06098026882a57f5f6c436abaaf68be79be2fc7c6e33b8e884065195a3a`;
  compression differs from the research writer, so identity is checked on
  the decoded operation bytes. `NATIVE-PILOT.json` records this check.
- The public-parent three-way pilot uses fresh label
  `pareto-exact-diagnostic-20261019-v1`, 512 batches / 32,768 shots per stream.
  Parent, copy-removed, and four-product candidates each have **47 wrong-output
  shots** and **zero dirty shots**. Failed batches are 57, 53 and 55.
  The four-product candidate's paired mean saving is **5.049 ± 4.510 T**
  (standard error), consistent with a small improvement but not a robust
  measured margin. This pilot is not the final failure-rate gate.

The continuation starts from this four-product candidate; it does not select
or tune stages using the pilot's packets. Its fixed sequence repeats the
existing seven stage configurations twelve times. Expected benefit remains
unmeasured. README plots and scored-result tables are unchanged.

## Follow-up

Read `continuation84-generation.log`, `continuation84/PROGRESS.json` and the
per-stage audit receipts. `continuation84.exit` is written only by the shell
wrapper on actual exit. If it finishes successfully, read `NATIVE.json` and
`gate/RESULT.json`; `READY_FOR_NONCE_RESEARCH.json` still is **not a score**.
Remaining work then is a sound candidate-bound prefilter or affordable exact
screen, ascending nonce search, unchanged official benchmark, public-record
refresh, and a reviewable submission. Never rerun a failed statistical gate.

Failed tooling attempts are preserved: scanner v1/v2 initialized registered
inputs when their annotations were encountered instead of before op zero.
Annotations can occur late in this format. Their discoveries and counts are
INVALID and must never be used as evidence or candidates. No gate or nonce
search was run on them. Version 3 initializes all registered resources before
scanning and adds a regression test for late and duplicate annotations.

Public API refreshed at 10:05 Singapore: product leader is `9dc3798c`,
commit `0c3a0751ab66bd9144358d67563bcb79201cf636`, Q1234, T761096,
product 939192464. Our `62341149` is now officially scored at Q1863,
T752991 and remains the minimum-Toffoli entry. Raw API responses and hashes
are saved beside this file. Existing repository changes are preserved.

Objective: reduce complete measured Q × T. At Q1234 the strict target is
T <= 761095. Begin with exact repeated-product reuse at unchanged width.
The old PRODUCT179+ estimate is only a lead, not a verified implementation.
Its exploratory scripts contain heuristic treatment of unknown cache flags;
new work must prove the actual conditions rather than assume them true.

New experiment: an exact symbolic scanner with collision-checked expression
interning, classical condition tracking, and conservative expression-size
limits. Find repeated unconditional products and clean idle donor intervals.
The identity a*b = a*(1+a+b) = b*(1+a+b) is exact over Boolean values.
Unknown or truncated expressions may hide opportunities but cannot establish
false equality. No arithmetic cuts, packet-dependent choices, or nonce search.

Server checked: LHC-104-070, 144 CPUs, load about 35, 255 GiB available.
Two unrelated 18-thread workloads and suspended historical ECDSA jobs are
preserved. Research lives under /home/hclau/ecdsa_research/product-pareto-20261019.
Use four build threads, one symbolic scanner thread, and at most 32 total
census threads initially. No scheduler command was found.

Parent checkout is detached at the exact public leader. Research tools and
logs remain outside submission trees. Final qualification requires source
binding, correctness checks, a declared 32768-batch paired failure gate against
the exact public parent, then ascending nonce search and unchanged benchmark.
