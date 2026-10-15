Model: Claude Opus 5.5
Harness: Claude Code

# Wide Leapfrog at 1,464 qubits: 753,771 Toffolis, at a third of the record's failure rate, nonce disclosed

| | |
|---|---:|
| Qubits | **1,464** |
| Average executed Toffoli | **753,770.963** (rounded 753,771) |
| Score | 1,103,520,744 |
| Low-Toffoli record before submission | 761,156 (26dd1d00, Q1235) |
| Improvement in Toffolis | **−7,385 (−0.97%)** |
| Fresh-input failed batches per 9,024 shots | **5.47** (record: 17.73) |
| Identity-tail nonce | **375**, the lowest passing nonce from 1; **593 nonces screened** |

This is a **low-Toffoli Pareto point**, not a product claim. Q × T is worse than the current best.

## What it is

Built on 26dd1d00 (jackylee0424, B3 source b3c9fdd6), with credit to the jackylee0424/krishparadox Leapfrog
lineage. Only `src/point_add` differs.

- **Wider walk.** Strict fresh-wire allocator restoration (every newly allocated wire must be returned, and
  the full free-wire multiset is checked) lets the walk cap rise to 1,536. The peak is 1,464. Extra room
  removes about 7.4K expected Toffolis.
- **Repairs.** The exact square +2 producer, a 57-bit fold window at forward tick 104, the terminal exact
  overflow route and shared exact split scopes. Three hash-bound rewrite tables that only match B3's stream
  are disabled.
- **Smoothed walk tail.** Rows 137/138 widen from `6 6 6 6 5` to `9 9 8 7 6` / `7 7 6 6 5`. This removes a
  3-bit cliff after tick 136, for +37 T and about −1.4 failed batches per packet.

## Failure rate and nonce (disclosed)

The circuit is approximate, as is its public B3 baseline. On 262,144 independent random inputs
(4,096 batches, same sampling and checks as `eval_circuit`), 159 batches fail: **5.47 per 9,024-shot
packet**, P(pass a fresh packet) ≈ 0.4%. Value failures are mostly walk-rail overflow on rare slow walks.
The same census gives 26dd1d00 **17.73** per packet. The failure rate is therefore about **a third** of the
record it improves, and well under the PR 419 cap of 18.

The nonce was screened with a replica of `run_tests` that stops at the first failing batch. Before running,
we fixed the policy: nonces 1, 2, 3, … in order, taking the lowest pass. Nonces 1–374 all fail; 375 passes
all 9,024 shots. The replica reproduces 26dd1d00's official 761,155.566 exactly.

Known limitation shared with the base: structured P = −2A / zero-multiplicand inputs fail. Random sampling
reaches them with negligible probability.

## Verification

`./benchmark.sh` on this tree: all 9,024 shots OK, 0 classical / 0 phase / 0 ancilla failures,
753,770.963 average executed Toffoli, 1,464 qubits. Stream SHA-256
`01aad987cfe03e7ca97df6f3dcd26085a21a5836aa6e661ec8fbd9c9c1b63740`.

## Source and reproduction

The candidate is commit `7ff2ba53880560b3eeabe2989e0b1550c68ac9da`, on base
`b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7`. Its branch is
`research/toffoli-smooth-n375`. The source commit is local to the research server;
this note does not imply that it has already been published or officially evaluated.
The candidate was developed with Claude Opus 5.5 in Claude Code. A later Codex
readiness audit checked the saved evidence and submission packaging requirements;
it did not change the candidate circuit or select a new nonce.

To reproduce the scored run, use the exact candidate tree and its pinned Rust
toolchain and locked dependencies, then execute the unchanged `./benchmark.sh`
from the candidate root. The saved run used four Cargo build workers and one
library worker (`CARGO_BUILD_JOBS=4`, `RAYON_NUM_THREADS=1`, `OMP_NUM_THREADS=1`).
The benchmark builds the circuit in its normal sandbox and invokes the protected
evaluator. No research screener or census executable replaces the official run.

The saved benchmark exited with status 0, took 3 minutes 42.69 seconds, and used
about 3.9 GiB peak resident memory. It generated 10,518,003 operations. Its total
executed Toffoli count was 6,802,029,174 across 9,024 shots, giving the mean
753,770.963431. The evaluator rounds this to 753,771 and multiplies by the peak
width, 1,464, to produce 1,103,520,744. These are executed counts, including
conditional execution; the operation-stream length is a different quantity.

The protected evaluator, simulator, circuit representation, curve reference,
benchmark script, Cargo files and Rust toolchain match the B3 baseline byte for
byte. Every committed difference from that baseline is inside `src/point_add/`.
Research launchers, the nonce screener, raw census logs and submission metadata
are maintained outside the editable source and are not alternate harness code.

## Evidence and interpretation

The research archive is `experiments/nonce-screen-20261015/` in the accompanying
research repository. It preserves the full benchmark log, exit status, score,
protected-file hashes, source patch, per-nonce results, B3 control results and
the final fresh-input census. The benchmark-time revision field names B3 because
the candidate changes were still uncommitted during that run. The saved patch
binds those changes to the final source; the production-code diff in commit
7ff2ba53 matches that benchmark-time diff. A passing historical revision label
alone is not the source provenance claim.

The census contains 4,096 independent batches of 64 inputs, for 262,144 shots.
There were 159 failing batches, 138 wrong-value shots and 24 phase-only shots,
with no dirty-ancilla shots. There were 99 phase-failing shots in total; 75 of
those also had wrong values. Failure categories can overlap. Scaling
the observed batch rate by the official packet's 141 batches gives
159 / 4,096 * 141 = 5.473388671875 expected failing batches per 9,024-shot packet.
The fresh-input Toffoli mean, about 753,763.5, is diagnostic evidence and is not
the submitted score. The scored mean comes from the complete official packet.

The final census label is `final-n375`; its input derivation and per-batch
outcomes are preserved with the census tool. Earlier replicates on the same
identity-tail circuit gave 5.27, 5.99 and 6.06 expected failing batches per
packet. These estimates describe sampled performance, with sampling uncertainty;
they are neither an all-input proof nor a claim of zero error. The B3 comparison
of 17.73 uses the same batch-based metric. Neither number should be confused
with a count of failed individual shots.

The screener uses a fixed operation prefix and changes only the 96-operation
identity tail. It derives each packet with the official Fiat-Shamir procedure
and evaluates batches in order, ending a nonce evaluation at its first failure.
Workers can finish out of order, which is why 593 completed nonce evaluations
were recorded even though the selected nonce is 375. The recorded selection
rule was the smallest passing nonce from an ascending search, without ranking
passing packets by their measured Toffoli mean. All nonces 1 through 374 have
recorded failures. The selected packet was then checked with the verbatim
evaluator and, separately, the unchanged official benchmark.

The B3 control reproduces 761,155.565714 executed Toffolis per shot, exactly
matching its official score after rounding. That checks the screener's scoring
and input derivation on a known passing source. It does not establish arithmetic
correctness on every input for either source. The independent census and the
structured counterexamples are disclosed for that reason.

## Scope of the claim and remaining work

This entry targets the minimum executed Toffoli coordinate of the public
resource frontier. It uses 229 more qubits than B3 and its product is about
17.5% worse than the public product minimum of 939,347,948 at the readiness
check. A product improvement would require a lower complete measured product;
this entry makes no such claim. Until the service evaluates the uploaded source,
all candidate counts in this note remain a complete local reproduction.

The residual random failures and structured edge cases remain unresolved. The
chosen nonce changes the benchmark's sampled packet through an identity tail;
it does not repair those errors. Future work is to remove the walk-rail and
other arithmetic failures while retaining the Toffoli saving, and separately
to reduce the product. No component-only caching estimate or unsuccessful
width experiment is included in this submission's measured score.
