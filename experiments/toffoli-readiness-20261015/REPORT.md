# Lower-Toffoli submission readiness, 15 October 2026

The three objectives are independent. A new minimum Toffoli count is valuable
even if it uses more qubits or does not beat the scalar product. This cycle
targets that record; the other chat continues its Q692 work separately.

The refreshed public minimum is 761,156 executed Toffolis at Q1235. A new
record requires a complete passing benchmark with rounded mean at most
761,155. The product target is not an additional requirement. See
[the dated public snapshot](public-frontier.json).

## First candidate: reuse existing clean wires

Base: public B3, revision
`b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7`.
The previously tested exact lazy-cache transformation was ported to this
low-Toffoli baseline. All arithmetic parameters, identity tail, protected
harness, scorer, simulator, curve reference, manifests and toolchain remain
unchanged. Three point-addition source files change.

The ordinary complete build and unchanged benchmark finished in 4:25.01.
All 9,024 shots were tested. The result **failed**, with 16 value mismatches,
11 phase-failure batches and zero dirty-ancilla batches. There is no qualified
score and this source is not ready to submit.

| Paired input family | Shots | Unequal full-state batches | Value failures in each | Phase batches in each | Diagnostic mean saving |
|---|---:|---:|---:|---:|---:|
| Candidate's official packet | 9,024 | 0 | 16 | 11 | 3.9885859929 Toffolis |
| Independent | 256 | 0 | 1 | 1 | 4.015625 Toffolis |
| Structured | 256 | 0 | 189 | 4 | 4.015625 Toffolis |

These savings compare identical inputs and aligned original measurement events.
They are not official counts or a new resource record. Every observed failure
also occurs in the baseline. The replayer reconstructs the complete candidate
stream, including its unchanged tail, then checks all quantum slots, original
classical slots, phase and cleanup of new flags. All families have zero dirty
ancilla batches. This finite agreement supports the rewrite, not correctness
of the inherited approximate arithmetic.

The candidate selects 2,738 cache leases and remains at Q1235. Three native
tests pass, covering dirty classical scratch, condition snapshots, restored
controls, overlapping leases and independently varied measurement outcomes.
A deliberately removed phase repair is detected. The depth-based estimate
of 575.47 savings is not a measurement: the actual paired saving is about four
because many repeated operations belong to mutually exclusive branches.

Patch SHA256:
`3e77607c51d25fdcefd98f8ce9c136a8d43ccb994a0251a6148b9590eec66358`.
Stream SHA256:
`8bc2a903c59013fbbecda4258ae655e052260adc4d6bc6848e971488b889c6f2`.
The [terminal receipt](evidence/terminal/receipt.json) binds protected files
and the [exact patch](evidence/terminal/candidate.patch).

## Wider construction

The second construction explicitly trades additional clean qubits for fewer
Toffolis. Every eligible identical-product group obtains a cache wire;
nonoverlapping lifetimes reuse those new wires. Unlike the first construction,
it does not require an already idle wire in the original circuit.

Two native tests pass. The positive test covers all 256 combinations of four
quantum input bits and four classical predicate bits, under all four independent
measurement outcomes for two overlapping leases: 1,024 cases. It checks incoming
phase, dirty new classical slots, restored controls, deterministic generation
and zero cleanup of the added quantum wires. The negative test detects an
intentionally omitted phase repair.

The full wider build completed at **Q1239**, using four added physical qubits
across 2,838 nonoverlapping/overlapping cache leases. Both fixed 256-shot
comparison sets measured **74.91796875 fewer executed Toffolis per shot**
than the unchanged B3 baseline, a substantially larger saving than retaining
the original width allowed. This is an unscored relative saving, not a new
official Toffoli count or Pareto point.

Across all 512 compared shots there were zero unequal state/phase batches and
zero dirty-ancilla batches. The comparator also explicitly checks that every
added quantum slot returns to zero. It reconstructs the complete stream before
simulation. Independent inputs still yield one wrong point and one phase
batch in both versions; structured inputs yield 189 wrong points and four
phase batches in both. The known arithmetic failures therefore remain, and
the wider candidate is blocked from submission. It was not advanced to another
official benchmark after this independent correctness failure.

The [wider source receipt](wide-evidence/terminal/receipt.json) was captured at
generation, before independent validation, so its historical status is
`pending`. The later [submission status](wide-submission-status.json) records
the decisive correctness block. The build is no longer pending or running.
Its [patch](wide-evidence/terminal/candidate.patch) has SHA256
`c14824d71427958144d513973192a6e36b8f68352c82397060889e0fec3c316c`;
the complete stream has SHA256
`bb2bb4ba78738069b1b5ac7360fc93f864038bd788c4207a2e1212116d248c9b`.
No protected source files changed.

## Submission gate and evidence handling

[The readiness check](check_readiness.py) treats qubits, Toffolis and product
as separate record objectives. Its tests include a hypothetical Q1235/T761155
result: it is recognized as a Toffoli-only improvement despite its worse
product. Failed official evaluation and known independent correctness failures
block packaging; diagnostic counts are never promoted to qualified metrics.
All four readiness tests pass.

The first comparison launcher finished compiling before the candidate benchmark
was complete, then stopped at its explicit prerequisite check. That exit is
preserved as `replay/run.exit`. The continuation reused the same comparison
binary after the benchmark finished; `replay/run-r2.exit` records completion.
This was a scheduling failure, not a circuit or simulator repair.

No nonce search, packet tuning, submission, shared-track edit, or change to the
Q692 chat's work was made. Server jobs and files belong only to
`/home/hclau/ecdsa_research/toffoli-readiness-20261015/`.

## Remaining obstacle

Neither source is submission-ready. The blocker is inherited arithmetic and
phase correctness, not failure to improve the scalar product. The wider
transformation is worth preserving for a repaired arithmetic implementation.
Repairing that implementation may increase its gate count; the net result
must then be evaluated afresh against the independent Toffoli target.

All work in this cycle finished. The [evidence manifest](evidence-manifest.json)
binds source patches, tests, logs, streams and fixed replay packets. Large
streams and packets remain on the server; bounded evidence is stored here.
No background job is continuing from this chat.
