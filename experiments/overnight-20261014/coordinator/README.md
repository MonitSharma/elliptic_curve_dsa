# Conservative allocation experiments

These are complete **research diagnostics**, with no candidate, score or
submission. The passing public Q1234 stream was inspected without modification.

Baseline: `c5bb1ec876db859a3f9f8a9052c140a145df834e`;
compressed stream SHA256:
`49b35cf7640ebd529d76894eb8bef93ebf57e7e970fe14b3c27c8c5feb6e73e4`.

## Clean-boundary interval packing: no reduction

Hypothesis: beginning temporary wire lifetimes at their first operation, and
ending them at an unconditional reset, might eliminate early allocator
reservations without changing arithmetic or phase.

The streaming analyzer reserves all 512 ABI qubits throughout. Only an R/Hmr
outside every classical condition creates a clean split; conditional resets
are deliberately unsplit. Any unfinished interval remains live to stream end.
Thus the analysis never infers a globally clean passenger from a reset that
executes only on some shots.

The 11,459,514-operation stream contains 760,718 unconditional temporary reset
boundaries and 145,665 unsplit conditional resets. After reserving ABI wires,
641,617 intervals still peak at **1,234 simultaneously live intervals**, first
at operation 1,444,991 (zero-based). Simple interval recoloring under these
rules offers no width reduction. This is not a lower bound against arithmetic
rescheduling, stronger clean-value proofs or conditional sharing.

Run: PID2321720, exit0, 13.98 seconds and 217,812 KiB peak RSS; one thread, 8 GiB
virtual-memory limit. Server evidence:
`/home/hclau/ecdsa_research/overnight-20261014/coordinator-wire-lifetimes/`.
Log SHA256: `8fe146e54fcabbec1173c7aff8bfe5fc6803a130e1384bdec11928fa7e300b43`.
Four synthetic tests pass, including conditional-reset passengers, ABI
reservation and malformed/truncated-frame rejection.

## Exact known-zero query at the first peak

Hypothesis: a wire still inside a conservative interval might nevertheless be
proved globally zero and parked at this peak. An external crate copies the
baseline's immutable Boolean abstractions and adds only read-only queries;
the submission and protected harness are untouched.

The six-atom truth abstraction finds only wire1233 zero immediately before
operation1,444,991. That operation is CCX(control253, control803, target1233).
The follow-up checks the larger affine and degree-two polynomial abstractions:
**both likewise prove only wire1233 zero**. These methods expose no spare
parking wire at this peak. Failure to prove another wire zero is not a proof
that every other wire can be nonzero on an admissible elliptic-curve input.

Initial external audit PID2326769, exit0; broader audit PID2330295, exit0.
Initial audit log SHA256:
`adcb0fc6099a20e24353e52c57beaf94ed4a27e2111ee6c53c12c18cff8c363a`.
Server directories `coordinator-wire-zero/` and `coordinator-wire-zero-v2/`
preserve commands, source/Cargo hashes, logs and limits (16 GiB, four build
threads, one analysis thread). The public source remains unchanged.

Next actions: investigate actual arithmetic scheduling or predicate-dependent
ownership rather than repeating static recoloring. The product agent is
examining more expressive exact polynomial and commuting-gate identities;
the qubit agent audits the separate low-width quotient-owner schedule.

## Conservative classical dependency census

A four-state abstraction tracks constants, arbitrary classical functions and
quantum-dependent functions. Conditional reset or swap merges both paths; an
unproved cancellation never creates a classical-value fact. It observes the
unchanged complete baseline stream rather than sampled control patterns.

Only six CCX sites have a provably classical control in this abstraction, and
none has a constant control. All six are unconditional. This makes a general
classical-shadow engine a weak next lead here, although the abstraction loses
some cancellation facts and is not an upper bound on all possible rewrites.
No shadow computation, gate deletion or candidate is implemented by this census.
[Complete compact census](classical-dependency.json).

PID2356145, exit0, 19.33 seconds and88,840 KiB peak RSS; one thread and8 GiB
virtual-memory limit. Evidence directory:
`/home/hclau/ecdsa_research/overnight-20261014/coordinator-classical-controls/`.
Log SHA256: `cc06aeeac3ed2efb1037f18cba048f7e23c55e7286fe64809d87370aff1d5dc7`.

The separate product candidate uses exact equality with a current classical bit
and complemented-bit factorization; it finds eight structural replacements.
Those candidate results remain in its own diagnostic report, with no scored mean.

## Two-live-wire XOR witnesses: two structural hits

Hypothesis: a control product may equal the XOR of two existing physical wires,
allowing a CCX to become two CX gates without scratch or altered phase. The
read-only audit extends the public immutable interned-expression abstraction,
skips baseline single-wire witnesses, excludes the target and updates every
changed physical slot. A rare-atom index narrows candidate pairs; equality is
rechecked on complete expressions. Unknown expressions only lose proofs.

The first launch failed before compilation because Cargo was absent from the
detached shell's path (PID2372508, exit127). It is preserved in
`coordinator-linear-pair/`; log SHA256
`ba8bc2f07591bfd053173ed96fc2599e0d9f3a4d1c54a14329027ebb6d0320ff`.
The corrected launch explicitly loads the installed runtime and uses a fresh
evidence directory. PID2372876 in `coordinator-linear-pair-v2/` runs with16 GiB,
four build threads and one analysis thread. Its synthetic positive identity and
mutated-slot negative check pass. Complete-stream analysis ends0 in23.18 seconds,
with691,968 KiB peak RSS. Among813,269 CCX queries it tests748 candidate pairs and
finds two exact unconditional products: at operation5,339,866, wires820 XOR44
replace the toggle on target588; at11,397,834, wires860 XOR44 replace the toggle
on target613. These are two structural CCX-to-two-CX identities, not an executed
mean or qualified score. [Source, binary, tests and log receipt](linear-pair-receipt.json).

The follow-up expands from pairs to arbitrary sparse linear combinations of current
wires and the constant function, with exact GF(2) elimination. It excludes the
target and rechecks the full expression before reporting any result. This is
also a read-only research audit. It ends0 in18.98 seconds, with689,660 KiB peak
RSS and two passed positive/fault tests. Its110 admitted queries find exactly
the same two identities, with no further saving. [Linear-span receipt](linear-span-receipt.json).

A source-only generic replacement is separately preserved in
[the candidate patch](linear-witness-candidate.patch) and
[manifest](linear-witness-candidate-manifest.json). Native tests cover64 dirty
basis/classical assignments and32 measurement patterns, nested snapshot
conditions with a mutated bit, a following CZ/HMR and target exclusion. All
2,048 paired quantum/classical/phase states agree. The candidate patch reapplies
to exact c5bb1ec8 blobs byte-identically with line-ending conversion disabled.
Its official-builder binding and full benchmark are not run: a standalone
two-gate reduction cannot bridge the public record gap. No score is claimed.

## Complete public qubit model: the sixth failure is crossing storage

The independent earlier integer audit focused on reciprocal tests and map
valuations. A new external crate imports the unchanged public point-add source
and runs its complete classical failure model, including schedule envelopes,
Q capacity and crossing reserve. All18,048 intended division inputs from the
preserved failed packet are examined. This model flags exactly six divisions,
one in each of the six observed mismatching shots. Every schedule envelope
passes. Five are reciprocal-search failures; shot3713 division1 is a crossing
parking failure. Earlier failure ordering masks shot8048's later quotient cap.

At shot3713's direct crossing, Euclidean step60 has Y of119 bits and quotient
375,614 of19 bits. Its parked quotient needs119+19−129=9 reserve lanes, while
the source provides7. The highest parked index is137 in a136-lane cycle.
This explains the new ideal-model discrepancy and supplies an exact native
regression input. It is not yet a native proof of the first failing gate.
Increasing reciprocal precision or quotient capacity alone cannot repair it.

The source-model audit ends0 in1.79 seconds,5,760 KiB peak RSS, PID2379894,
8 GiB virtual-memory limit and four build/one runtime threads. Its initial
external import failed compilation because contestant code is deliberately
absent from the shared evaluator library; the corrected external crate imports
that source directly, leaving the protected library unchanged. Both attempts
are preserved. [Model assumptions, exact input, source hashes and log](schedule-receipt.json).

The qubit agent's separate paired batch58 replay also fails shot3713 on both
base and compact circuits. All six observed classical failure inputs are now
inherited at point level. Phase and scratch behavior differs, and neither the
source model nor those selected paired inputs establishes full equivalence.

## Reproduction commands

The fourth checkpoint adds a canonical reduced decision-diagram kernel with
exact live-root collection. It proves all measurement outcomes on the tested
fixed-input component fixtures: 74 forward/inverse Q693 instances and 116
N275-v2 instances. Every earlier limited fixture now passes. The kernel's five
native tests include a separate truth-table oracle, classical snapshot and
phase faults, and node-budget failure. Source-private proof crates prevent
cross-checkout build-cache reuse. This finite component evidence does not
replace the full unchanged official point-addition benchmark, which is active
for the generated N275-v2 stream. [Proof and reproduction](DECISION_PHASE_PROOF.md),
[complete source bindings and receipts](decision-phase-proof-receipt.json).

The third checkpoint adds an exact conditional phase checker for all18
operation types. Each R/HMR receives its own immutable Boolean variable;
condition snapshots and mutable classical slots retain their exact semantics.
Four native/fault tests pass. On the cap24 Q693 source it proves38 forward or
inverse fixed-input instances, including all256 modeled shot3713 payload
lanes. Two other fixtures exceed the support limit; the stopped column test
does not reach its last fixture. No nonzero-phase diagnosis follows from an
inconclusive limit. [Complete receipt](conditional-phase-audit-receipt.json).

The independent N275 geometry screen covers18,048 original denominators and512
fixed-seed independent denominators. No quotient, parking, reciprocal or map
domain event is flagged. Four separate regressions reproduce the old six
source-model failures and detect insufficient reserve/cap. The screen cannot
establish a clean third physical map owner, schedule envelopes for fresh
inputs or quantum correctness. [Model receipt](capacity-screen-receipt.json).

Copy the tracked research helpers to the isolated server cycle directory and
run the corresponding detached launchers after resource preflight:

```bash
python3 analyze-wire-lifetimes.py ../product/ops.bin analysis.json
python3 test_wire_lifetimes.py
python3 prepare-wire-zero-audit.py ../product external-zero-audit
cd external-zero-audit
cargo generate-lockfile --offline
cargo build --release --locked --offline
target/release/wire_zero_audit /home/hclau/ecdsa_research/product/ops.bin 1444991
```

These commands inspect the existing stream and produce no official benchmark
score. The separate receipt checker keeps diagnostics and partial/failed full
evaluations out of qualified results; its four admission-fault tests pass.
The checker also correctly admits the preserved complete Q1234 baseline evidence
and rejects the preserved failed compact full run. This is a receipt-tool check
against historical logs and streams, **not a new benchmark reproduction**.
