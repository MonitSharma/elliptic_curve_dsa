# Exact phase checks on fixed component inputs

Status: both source-bound Q693 PH-owner and N275-v2 component suites pass.
These are not full benchmark results or all-curve-input proofs.

The earlier exact Boolean polynomial checker was inconclusive on conditional
Hmr classical-slot assignments: the stale conditional outcome representation
exceeded8192 terms while quantum and accumulated phase supports stayed small.
A canonical reduced ordered decision diagram represents the same Boolean
functions directly, with64-bit terminal masks for64 fixed inputs. Each R/Hmr
event has a new immutable measurement variable. Zero final phase and scalar
final quantum values establish independence of every measurement outcome for
each tested input lane. Conditions, nested snapshots, mutable classical slots,
conditional resets and all18 operation kinds retain the protected semantics.

The initial diagram attempt reached its cumulative million-node budget on
three fixtures. It did not diagnose nonzero phase. A live-root collector now
retains all quantum/classical values, phase and predicate snapshots, removing
only unreachable nodes and clearing the operation cache before ID reuse.
Five native/negative checks pass, including an independent64-assignment truth
check for6 variables and a reclamation/ID-reuse check. Resource limits remain
inconclusive; they never substitute unknown functions or declare success.

The Q693 PH-owner suite passes6 selected tests, including all13 no-payload
columns, shot3713/8048 and independently structured q22 payloads, plus dirty
single/two-owner preposition and inverse checks. The N275-v2 source passes9
selected tests, adding the full SY partition, SZ donor boundaries, and5 new
full columns at the96/97 boundaries and the wide first column. Its external
test wrapper freezes the entire point-add source and phase kernel privately;
the complete source tree, baseline revision and patch are hashed.

These tests justify generating the frozen N275-v2 full stream. Its actual
referenced width, operation count, loader memory and complete unchanged
9,024-shot benchmark remain separate gates. The complete benchmark determines
qualification; no component measurement is admitted to README scored results.

[Exact hashes, proof instances, failures and resource receipts](decision-phase-proof-receipt.json).
Reproduce with the tracked decision-kernel generator and detached
`server-decision-phase-tests.sh`/`server-qubit-decision-proof.sh` launchers in
the isolated server cycle directory. Candidate and protected harness source
are unchanged by these external proof crates.
