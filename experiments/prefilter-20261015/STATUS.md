# Product prefilter: exact screener faster; arithmetic rejection still disabled

15 October 2026. **Research tooling only. No candidate, benchmark score or
submission.** The exact full-channel screener is **3.38 times faster** in a
paired 128-nonce comparison. With the separately validated C point backend,
the exact screener is **4.23 times faster** than the original. A classical arithmetic predictor is implemented,
but has no sufficient certificate for skipping a nonce. Do not use its
predictions as rejections.

All work is bound to public product source
`4b2ec52fc55da796aa8f5ef851290297e8706424`, original stream SHA-256
`2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e`.
The original and the imported protected simulator/curve/harness/Cargo files
match byte for byte; see `evidence/provenance.json` (eight protected files).
No submission files were changed.

## Completed exact accelerator

`tool/src/bin/fast_screen.rs` uses a 12-byte instruction format, buffered
measurement words and fixed-base secp256k1 precomputation. It preserves the
official packet input order, every R/HMR draw, condition stack, value, phase
and ancilla checks. It omits gate-count accounting during rejection; a selected
nonce still receives the verbatim protected `run_tests` recheck.

Against the previous exact screener, nonces 1 through 128 produce identical
pass/fail decisions, first failing batches and failure kinds: **1,034 batches**,
84.17 versus 284.85 thread-seconds, **3.3842Ã—**. Both used eight workers.
No nonce passed. See `evidence/nonce-differential.json`, paired logs and
`run-validate.sh`. This is an accelerator validation, not a resource result.

`fast_screen_c` integrates the coordinator's pinned, independently validated
secp256k1 batch library from `../scalar-fast-20261015/`. It agrees with all
128 prior nonce decisions and 1,034 first-failing batches, using 67.38 versus
84.17 thread-seconds for the Rust accelerator. Against the original 284.85
thread-seconds, the combined measured speedup is **4.227Ã—**. The C backend
produces both points and their expected sum in approximately 9.39 microseconds
per shot on fresh inputs; initialization costs 5.66 seconds and its shared
20-bit table uses about 800 MiB. See `fast-screen-c-differential.json` and
the coordinator's protected-reference validation in `scalar-fast-20261015`.

The fixed-base Rust helper matches the protected curve on **4,101 scalars**,
including 0, 1, group order, order+1 and the largest 256-bit integer. A ten-bit
table costs 0.19 seconds to initialize and 14.565 microseconds per scalar;
the protected reference costs 940.535 microseconds. A sixteen-bit table costs
6.98 seconds to initialize and 12.942 microseconds per scalar. These scalar
speedups are not whole-screen speedups. Protected gate simulation alone costs
about 98.7 milliseconds per batch in the single-thread differential.

## Arithmetic predictor and negative evidence

`walk_model.py` and `tool/src/walk_native.rs` implement the actual YP8 veto,
late windows, rail schedule, signed truncations and modular payload replay.
The native implementation initially costs approximately 84 microseconds per
shot for arithmetic alone, excluding point preparation; the 10-microsecond
target remains unmet. Compact signed operations pass an independent 512-bit
word comparison across 256 random cases, widths 3 through 259, shifts 0 through
6, addition, subtraction and negation.

On the **preserved** 4,096-batch census (262,144 shots; not a new fresh census),
the first model detects 376 of 431 value failures, with zero false positives
and 55 misses. Native and Python versions agree on the first 4,096 shots.
`evidence/unmodeled55.tsv.gz` preserves the missing inputs.

Adding the measured production Y15 fold boundary formula detects 410/431
known value failures and no false positives among 4,082 early passing controls.
The complete 262,144-shot native check then finds **four false positives**:
410 true positives, 21 misses, 261,709 true negatives. Thus this version is
**unsafe as a rejection predicate**, despite the smaller selected test passing.
Its complete evidence is retained separately as `native-fold4096.*`.

## Gate-inert per-tick differential

A private observer evaluates 24 known failing inputs and eight passing controls.
Its protected simulator agrees on every qubit, classical bit, phase and executed
Toffoli count. The generated final stream is byte-identical to the frozen tip.
See `observer-validation.json`, `observer.log.gz`, `observer.patch` and packets.
The original wrapper had a relative exit-marker path after changing directory;
generation itself exited zero and all checks passed. The wrapper is corrected;
the independent validation receipt records the distinction.

The first rail model agrees at 7,397/8,832 forward stages. Three actual semantic
errors were identified and corrected in the Python version:

- Y42 cuts the target using a two-tick lookahead before its payload operation;
  the cut must remain in effect at the next tick.
- The divide's N2 tail runs rails without a fused payload; its source must not
  inherit the narrower fused source width.
- YP8 computes its choice before the target is trimmed and reads a cropped
  source sign; carry-derived veto signs must retain the original source sign.

With those corrections, **all 8,832 forward rail states and tapes match** for
the 32 inputs when each leg starts from its observed seed. See
`evidence/stage-standalone.json`. This checks the individual walks, including
bad paths. Separate end-to-end propagation still disagrees on nine multiply
inputs; see `stage-differential.json`. The current hypothesis is that reverse
rails fail to restore the original denominator, whereas the model assumed an
exact restore. Reverse-rail observation/replay is the next step.

**Completed continuation:** the reverse model now matches **all 8,768/8,768
reverse rail observations**, including the bad paths. Combined forward and
reverse agreement is **17,600 stages**. It includes the exact inverse barrel
reflection permutation, N2 parked sign-copy returns, the reverse fused widths,
and the `FM_PARK_LEND=1:2` cut. An algebraic compilation of the inverse barrel
matches literal gate reflections for 4,032 exhaustive small words and 5,100
large-width boundary/random cases, including inputs outside the usual promise.

RT0's recovered denominator is `2*R1 mod p` immediately before tick zero.
This agrees with **all 32 observed coordinate boundaries**; nine bad cases
actually restore a different denominator. The full point model must account
for this before subtracting the slope's square. The square's T6 fused seed is
a **full signed extended rail**, so its low 256 bits cannot be compared as an
ordinary field coordinate. A failed raw-256 interpretation is preserved in
`point-stage-differential-raw256-failed.json`; after decoding the seed, all 32
square transitions agree.

Four divide and five multiply payload discrepancies remain among the 24 bad
cases; **all nine coincide with nonunit N2 endpoint rails**, violating the
sign-copy loan's clean-scratch promise. All eight passing controls agree.
The recovered-coordinate model explicitly returns **unknown** on these loans
and on a dirty FM loan. On the selected 4,513 inputs it gives 243 true positive
predictions, zero false positives, seven misses and 181 unknown cases (all
known value failures). This remains diagnostic: primitive summaries have not
been proved sufficient for an all-input rejection certificate. The bounded 14-worker full-population check completed: 262,144 shots, 243 true
positives, **four false positives**, seven misses, and 181 unknowns (all failed
shots), in 188.8 seconds. The nonunit guard is therefore insufficient for a
rejection certificate. Every mismatch is preserved under
`evidence/recovered-population/`; this model remains disabled for rejection.

The corrected Python fold model currently gives 408 true positives, zero false
positives and 23 misses on the selected 4,513-case test. It has not received a
complete population check or a sufficient correctness certificate. The native
model still preserves the earlier semantics until the corrections are ported.

## Preserved unsuccessful certificate attempts

An exact Boolean-DAG audit, with conservative randomness flags, processes all
11,630,716 operations into 44,086,289 nodes in 241.44 seconds. All 512 output
bits remain unresolved; randomness independence was **not proved**. Two
exhaustive identity/negative-control tests pass. See `rng-audit.*`.

A second exact representation expands measurement-variable polynomials while
keeping input-only Boolean functions as immutable DAG coefficients. At a
32-term cap, oversized expressions become fresh RNG-tainted unknown symbols,
preserving conservatism. It creates 1,597,440 unknowns and leaves all 512
output bits unresolved in 108.23 seconds. Three tests pass, including a cap
taint negative control. See `rng-coeff.*`. Neither audit enables any skip.

## Reproduction and remaining work

Server directory: `/home/hclau/ecdsa_research/prefilter-20261015`.
Original immutable stream: `../product-exact-20261015/tip/ops.bin`.
The server keeps the full census coordinate TSV; the local evidence package
contains compressed selected inputs, complete outcomes, observer logs,
source/protected-file/binary hashes and all launchers. Use one library thread;
this experiment is bounded to at most 16 workers and 60 GiB.

Next: port corrected rail/recovery semantics into the native hot loop, account
for the remaining supported-path misses and exceptional borrowed-scratch cases, then establish
a sufficient source-level rejection certificate. Until then, only the exact
full-channel screener can reject a nonce. No long product nonce search has
been started.

## Exact SIMD confirmation with advisory batch ordering

A separate research-only screen links the independently validated exact
AVX512 eight-batch interpreter and SHAKE8 libraries. The cheap native forward
rail interpreter uses the corrected Y42/YP8/N2 semantics and checks both
`P.x-A.x` and `A.x-(P+A).x`. On the full preserved 262,144-shot population,
359/431 known value failures raise a flag, as do nine passing shots. It takes
35.27 microseconds per input for both walks. These flags only choose which
batch to check first; they never reject a nonce directly.

Every rejection requires an exact simulator witness that checks output
coordinates, phase and all unregistered quantum scratch. Random measurement
words are selected at the batch's original packet offset after all 9,024
scalar pairs have been consumed. If the selected batch passes, the full
ascending exact check follows; every accepted shot and final partial batch
uses the protected evaluator's skip rules. The omitted 96-operation nonce
tail is asserted to consist of identical unconditional X/X pairs.

For predetermined labels 1 through 128, advisory and ascending SIMD checks
agree with both the original evaluator and earlier compact C-curve screen.
All 128 labels fail. Advisory ordering needs 128 exact batches, versus 1,034
in ascending order. With two workers, wall times are **6.756 vs 16.795
seconds** (2.49x). Aggregate worker time is **13.378 vs 31.588 seconds**,
versus 67.38 seconds for the compact C-curve screen and 284.85 seconds for the
original evaluator: **21.29x** the original measured work on this fixed test.
The chosen batch averages index 10.086. See `advisory-differential.json`.

The known passing frozen-tip nonce 1046072871510, with batch seven forced
first, passes the entire accelerated packet and a protected official replay:
9,024 shots, zero value, phase or scratch failures. A constructed acceptance
test passes zero/order/infinity, equal-x and opposite-point skips, preserves
accepted-input order, refills a full 64-shot batch and a partial six-shot
batch. Explicit no-hit fallback, nonmultiple-of-eight packets, concurrent lowest-nonce controls and full official positive replay all pass. This is validation only, not a new search or resource record.


## Completed packet bucketing and capacity checks (16 October)

The lookahead scheduler preserves independent transcripts while regrouping
nonces with similar selected batch offsets. Every source context is retained
for full fallback. A 64-byte routing self-check verifies each combined lane.
On predetermined labels 1–1,024, all exact screen variants agree: 1,024
rejections, 1,173 exact batches and nine full fallbacks. On the same two-worker
machine, unbucketed wall time was 66.242 seconds; 128-label bucketing took
50.417 seconds. Replacing only the advisory calculation with the independently
validated SIMD rail implementation reduced this to 42.443 seconds. A full
1,024-label lookahead measured 38.372 seconds with two workers and 6.538 seconds
with 16 workers. These are measured screening results, never scored resources.

The frozen product candidate's census implies an expected 190,311,598 nonces
before a passing 141-batch packet. Even the improved pipeline projects roughly
63–84 hours at 64 threads under ideal scaling. This fails the current cost
gate, so no long product search has begun.

The original compact ABI now rejects dimensions or operands colliding with
its 16-bit sentinel. A separate 16-byte ABI widens classical IDs to 32 bits;
this supports the frozen product stream's 91,691 classical bits. Every quantum
wire, classical bit, phase bit and RNG draw agrees with eight separate
protected simulators on 512 actual Fiat-transcript shots for both the public
tip and the frozen product candidate. A high-ID conditional/snapshot fixture
and old-ABI rejection tests pass. The widened screen also passes the known
public-tip packet and its complete protected official replay.

## Arithmetic-model correction and remaining proof gaps

The four full-population false positives were traced to the public product
source's 57-bit forward fold prefix through tick 99; the inherited wide-parent
model incorrectly used tick 55. The old model is preserved, and only this
source-bound constant was corrected. The independent corrected population
check reports 243 true positives, zero false positives, seven misses and 181
unknowns across 262,144 shots. This remains diagnostic only. Separate protected
primitive probes expose finite 53-bit seed-halving and special tick-zero
three-add semantics not represented by the idealized summaries; historical
cut guards also require proof. Zero empirical false positives do not establish
a sufficient rejection certificate.

## RNG-independence certificates: successes and negative results

A concrete-input Boolean polynomial interpreter uses 64-bit input masks as
coefficients and fresh independent measurement symbols. Conditional resets,
all inactive measurement events and capped unknown dependencies are retained.
Interning normalized capped expressions, with constants outside immutable
keys, proves all 16,384 output bits on the 32 audit inputs independent of every
measurement symbol in 7.176 seconds. It certifies the 24 known wrong outputs
and all eight passing controls; four protected full-state containment runs
pass. This is a finite-input universal-MR proof, not an all-input certificate,
and its present runtime is too slow for production screening.

Global variants keep every input bit symbolic and input-only coefficients
separate from MR polynomials. Binary-coefficient V2 completed in 1,354.51
seconds with 199,075,679 coefficient nodes and left every output unresolved.
An associative coefficient variant exceeded its 32-GiB address-space limit;
the bounded variant completed in 184.20 seconds with 30,802,974 nodes and also
left all 512 bits unresolved. Both completed variants pass four protected
full-state containment seeds and preserve matching before/after source and
stream hashes. The earlier stopped and memory-limited attempts remain clearly
marked incomplete. None enables rejection or output masks.

A distinct square-free input coefficient layer is under bounded validation.
It retains exact input-only opaque function definitions and distributes small
Boolean products to recover cancellation without expanding all quantum input
functions. Its report preserves a per-output RNG-free mask even if the full
output proof fails. Only a positive sound, stream-bound proof could authorize
using the independently validated zero-MR evaluator as a rejection witness.

An empirical MR-sensitivity check separately tests all 541 failing-census
inputs (431 value failures, 297 phase failures, with overlap) and 256 unique
structured boundary inputs. Each input is repeated across eight independent
MR streams and compared against zero-MR values. No output-coordinate variation
was observed for either the public tip or the frozen product stream. This is
useful negative diagnostic evidence, not a proof of MR independence; all skip
paths remain disabled. See `rng-sensitivity-*.json` and the empty witness files.


## Terminal certificate diagnostics and checkpoint

The square-free cap16 method completed in 423.62 seconds with 34,283,438
input-only coefficient nodes. All 512 output bits remain unresolved, including
206 represented by a single capped RNG term. Four protected full-state
containment runs pass. First abstract precision loss is original operation
688826: HMR q1106 into reused classical bit b1565. This is a limitation of the
representation, not proof that any output actually depends on MR.

A separate 8-GiB retained-key cache run completed with zero cache evictions in
148.68 seconds, retaining 1,694,699 exact opaque keys. All 512 outputs still
remain unresolved. Thus cache eviction alone does not explain the missing
certificate. The larger cap128 input-ANF variant was explicitly stopped only
after its exact PID/argv were verified; it was superseded by the faster cap16
variant and remains incomplete, with no certificate claimed.

The arbitrary-coordinate MR diagnostic covers 1,385 tuples: 1,024 independently
sampled coordinate words and 361 invalid boundary combinations. Eight MR
streams and zero-MR give identical coordinates for both frozen streams.
The expected-value columns are explicit zero placeholders and are not used to
claim correctness. This remains empirical sensitivity evidence only.

The next bounded hybrid experiment canonicalizes pure classical A-input
functions with exact ROBDDs, retaining quantum-input functions separately.
It preserves caps conservatively and is under active validation; its active
source/logs are excluded from the terminal checkpoint archive. The archive's
manifest records every included file's size and SHA256, plus exclusions and
the hash of the full coordinate TSV retained on the server. No unproved model
or RNG-free skip is enabled in any screen.
