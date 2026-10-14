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

## Reproduction

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
