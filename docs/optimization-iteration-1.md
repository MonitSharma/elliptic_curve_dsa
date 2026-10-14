# First optimization iteration

Historical root-checkout experiment, 14 October 2026. For the current three-track
state and machine migration see [SERVER_HANDOFF.md](SERVER_HANDOFF.md) and
[parallel-campaign.md](parallel-campaign.md). The Q1235 baseline below is the
minimum-Toffoli record in our latest snapshot; Q1234 now leads the product.

**An exact local gate saving was found, but no new leaderboard
record was qualified.** The reproduced upstream circuit remains the default.

## Change kept for research

The final cleanup uses complete Boolean truth functions to identify implications
between Toffoli controls. If, under the current classical predicate, `a AND b`
equals `a`, the gate becomes a CNOT controlled by `a`. It can similarly become
a CNOT controlled by `b`, an X, or disappear when its toggle is identically zero.

The proof functions refer to immutable values rather than mutable wire names.
Oversized supports become unknown atoms, which prevents a missing proof from
being mistaken for an identity. Classical conditions are captured by value,
including when their original bit slot is subsequently overwritten.

The new pass runs after the existing prefix-bound tables. Their hashes and
checks remain intact, and the original early simplification rules remain
unchanged. No measurement or reset is moved or removed by the kept change.

On the saved incumbent stream, the cleanup reduces emitted nonlinear gates
from **816,456 to 816,454**, with the peak fixed at **1,235 qubits**.
One operation disappears and one becomes a Clifford operation.

## Verification

- Exhaustive small-input fixtures check values, phase, and measurement history.
- A stale-control negative control demonstrates that an unsafe CNOT replacement
  is caught; modifying a control invalidates the old relation.
- Another fixture checks a captured condition after its classical slot changes.
- A paired full-stream check covers **2,048 fresh arbitrary basis inputs**, with
  identical random measurement words. All quantum values, classical values,
  phase, and register layouts match. Mean saving: **1.504395 Toffolis**.
- A separate check uses the **9,024 valid elliptic-curve inputs from the
  candidate's canonical packet**, with the canonical forward measurement stream
  applied to both circuits. Reverse comparisons use independent random words,
  so they do not alter the forward scoring experiment. Every forward and reverse
  quantum state, classical state, and phase agrees between the two circuits.

The canonical same-packet saving is **1.493462 Toffolis**; the paired candidate mean is **761157.311946**, matching the official run's rounded display.

Machine-readable canonical results are in
`research-output/canonical-inheritance.json`. The baseline, candidate streams,
and experiment logs are archived under `research-output/` and `.tools/`. For transfer,
the important `.tools` logs are copied to `research-output/iteration-1-logs/`;
the handoff archive excludes `.tools` itself.

## Why the candidate is not enabled

The official candidate run reported **11 classical mismatches**, **9
phase-garbage batches**, and **0 ancilla-garbage batches**. Replaying the
incumbent on that packet gives the same failures. The change preserves behavior;
it does not repair the incumbent's approximate arithmetic.

Changing even a single gate changes the Fiat-Shamir hash and therefore the
packet. The incumbent's passing packet cannot establish that a modified stream
will qualify. The candidate's official mean was **761,157.312 Toffolis**, and
the run failed. It has no valid new score.json or leaderboard result.

The small gate saving is also below the observed packet variation. It is useful
as a checked optimization primitive, not a substantial competitive result.

`EXPERIMENTAL_FINAL_CLEANUP` in `src/point_add/mod.rs` is **false**. The default
benchmark was rerun successfully at **761,155.566 average Toffolis**, **1,235
qubits**, and score **940,027,660**, reproducing the incumbent.

## Other avenues checked

The forward correction program's outputs have nonlinear linear-span rank 14
relative to its input bits and the available quotient intermediates in the
exhaustive 14-input Boolean model. The existing program already uses 14 ANDs.
That rules out eliminating one of those gates merely by expressing it as an
XOR of the available values. It does not prove that the complete fold is
globally optimal: the broader joint model has a lower bound of 19 additional
nonlinear dimensions under the tested raw-input/carry basis.

Broader structural implication, local commuting-pair cancellation, and cubic
phase reduction experiments found no additional savings on this stream. Their
extra runtime and production code were removed; their logs remain available.

## Reproduce locally

```bash
source ./activate.sh
cargo test --release --locked --offline --bin build_circuit \
  point_add::final_cleanup::tests -- --include-ignored --nocapture
./scripts/benchmark-local.sh --note "Default baseline verification"
```

The explicitly ignored stream checks require the archived local research files.
Ordinary unit tests do not. Enabling the experimental constant generates the
cheaper but currently unqualified packet; it is kept disabled for normal use.

The harness, simulator, scoring program, Cargo dependencies and toolchain
specification were not modified. All results.tsv rows were appended by the
official harness. No public submission was made.

## Updated direction

Further work should pursue savings large enough to exceed packet variation,
with complete cleanup and phase costs included. The next useful synthesis
boundary is the complete low-bit fold construction, rather than the already
rank-tight 14-AND addend program. Its output and scratch-lifetime requirements
must be modeled together before implementing another candidate.

The scorer in this checkout checks the forward result, phase and ancillas. It
does **not** implement the README's stated forward/reverse identity test. The
paired inverse test above compares the two circuits; it does not assert that
the approximate incumbent implements a universally correct unitary oracle.
