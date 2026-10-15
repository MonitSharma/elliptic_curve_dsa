# Product prefilter: exact screener faster; arithmetic rejection still disabled

**16 October03:50 update:** the coordinator has accepted the separately proved
input-conditioned v3 mask and complete universal candidate25 transfer, and
started an operational ascending search. This replaces the earlier proof-gated
status for certified known-bit witnesses. The heuristic arithmetic predictor
still cannot reject on its own. Source/runtime acceptance, timing and active
search provenance are in
[the operational report](../product25-operational-20261016/STATUS.md).

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

The bounded pure-A ROBDD hybrid was stopped after its exact PID and argv
were verified. It did not improve the first proof obstruction and remains
an incomplete diagnostic. No certificate is claimed from it. The archive's
manifest records every included file's size and SHA256, plus exclusions and
the hash of the full coordinate TSV retained on the server. No unproved model
or RNG-free skip is enabled in any screen.


## Universal local value rewrites (16 October 2026)

The first classical abstraction cap belongs to a phase-helper macro. A new
local proof initializes every involved quantum and classical entry bit as an
arbitrary symbolic parameter, including dirty scratch, and compares its actual
quantum action with only its conditional R/HMR resets. It retains every original
MR draw, conditional classical write and Push snapshot. Caps and resource limits
return UNKNOWN. This certificate concerns all quantum/classical values; it does
not preserve phases or intermediate R dirty flags.

Universal proofs cover 250 complete top1 clauses and 547 source-bound comparator
regions, plus thousands of smaller scopes. The first export, certified-reduced-tip,
contains 4,034 disjoint certified regions and removes 1,517,553 quantum value
operations. Its compact16 SHA256 is
`a4d01570c76b589ed5d2d59b79ac12ccb4a7a155f1f70d415e3c5da2e5935927`.
Every quantum and classical wire matches the protected original on 5,132 shots,
including all 541 preserved failing inputs, 256 structured cases, 1,385 arbitrary
coordinate tuples and 768 deliberately dirty auxiliary controls, under multiple
MR streams. Phase differences are expected and separately recorded.

The corrected retained-mask global analysis completes in 200.50 seconds and
passes four protected full-state containment runs, but all 512 scored output
bits remain unresolved. Its first quantum MR dependency is at original op
3332030, crossing a scope boundary in a carry cleanup. A source-bound expansion
certifies 42 of 62 complete carry helper intervals, selecting 21 disjoint ones.
Combining those with all closed scopes gives 4,161 disjoint certified regions,
removing 1,526,376 value operations. The separately named carry export retains
906,156 original MR events and has 10,103,312 compact16 operations. Its compact
SHA256 is `f85d62e988b131cf8269564ee02f8d5b7c6614f2b8cda5fb10495f2fe394722e`.
The original Fiat transcript must always come from stream
`2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e`;
never derive benchmark inputs or measurement words from a rewritten research IR.

The first residual quantum MR dependency moves to original op 3930461. A stronger
local contract permits either exact zero-internal-MR arithmetic or the actual-guard
reset projection for each quantum output. Eighteen primitive/algebra tests pass,
but it certifies the same 42 carry intervals. The remaining tick126 interval has
one unresolved quantum output, q573. This is preserved as UNKNOWN, with no clean
entry assumptions. Further source boundary mapping is in progress.

These research IRs permit exact value-only rejection with the ORIGINAL random
measurement stream, followed by original phase/garbage validation on survivors.
The coordinator is integrating that path separately. Zero-MR rejection remains
disabled: empirical sensitivity tests and local rewrites do not establish global
measurement independence.


The carry-union global pass completed its symbolic work in 220.56 seconds,
with 412,074 caps; all 512 outputs remain unresolved. Four protected full-state
containment runs pass. Its process exit and before/after source hashes are zero
and equal. The carry-aware exported value IR also passes the complete 5,132-shot
protected differential with all quantum/classical words equal.

The stronger zero-internal-MR-or-reset theorem certifies 307 of 548 newly bound
complete helper intervals with arbitrary entry values. Its transition engine
passes 192 protected 64-lane primitive cases spanning all dirty entry assignments
and three MR words, alongside the algebra tests (27 tests total). A new global
contract replay is active and excluded from the terminal checkpoint. It accepts
explicit zero-entry preconditions only when its current symbolic prefix proves
those exact wire values zero; it also forbids contracts that partially overlap
a previously replaced region, since intermediate-state identity is not implied.
At tick126 the prefix proves q573, q583 and q1217 zero; even only q573=0 suffices
for the local theorem. These are proved constraints, never borrowed-cleanliness
assumptions. No global RNG-free output certificate has yet been obtained.


## Frozen input-conditioned MR certificate v3 (16 October 2026)

This terminal checkpoint supersedes the earlier active-job notes. Every owned
proof/export/validation job has completed, or was explicitly stopped with an
incomplete negative receipt. The earlier global-all-output proof attempts remain
negative: all 512 output expressions have unresolved symbolic MR support. The
new positive result is conditional on the supplied input and individual output
bit; it does not claim universal independence of all output bits.

The exact outer square-free MR polynomial retains coefficient functions as an
input-only Boolean DAG. OR of all nonconstant-term coefficients is a conservative
MR-dependence upper bound. A zero upper bound proves that output bit independent
of every physical measurement stream and every conservative capped unknown.
Wrong zero-MR scored output AND the resulting known mask is therefore a sound
value-failure witness. Unknown bits require the original exact fallback. Phase
and garbage-only failures also require original validation.

Frozen artifact: `evidence/mr-mask-tip-v3.bin`, SHA256
`560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d`.
It contains 7,914,981 nodes and is 126,641,776 bytes. The MRMASK01 format and
1024-port/512-output mapping are in MR-MASK-ABI.txt and its JSON manifest.
Declared input registers are P.x, P.y, A.x, A.y, each LSB first. Output roots are
MR-dependence upper bounds; known equals NOT root. Fresh MR/opaque symbols never
become declared input ports. Every input-only cap has an exact retained
immutable definition; missing definitions or undeclared terminals abort export.

The certificate binds ORIGINAL source 4b2ec52fc55da796aa8f5ef851290297e8706424,
stream SHA256
`2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e`.
It initializes all 1024 declared input bits symbolically and all auxiliary wires
zero. All physical MR events, including inactive ones, receive fresh symbols.
Local contracts bind exact operation digests; any zero-entry predicates are
checked against the current global symbolic prefix. Reuse on a changed source
requires an independent universal coordinate-equivalence transfer certificate.
No such transfer is claimed by this report.

Compactness comes from `input_anf_dag_trace.rs`, which retains each capped
input-only function's exact binary construction beside the independently retained
expanded semantic definition. `mask_program_trace.rs` emits those immutable
constructions, retaining kind8 monomial-product definitions, and rejects missing
or undeclared terminals. `global_rng_anf_mask_trace_body.rs` re-proves the selected
local contracts and checks the compiled masks against the full expanded
coefficient DAG on the audit inputs. Expanded v1 and compact v3 produce identical
audit masks. The expanded oracle has 128,173,614 nodes; no semantic definition was
replaced by a fresh known input to obtain the 7,914,981-node compact representation.

All 33 native exporter tests pass, including randomized binary-trace versus
expanded-definition equality, algebraic/capped negative controls, undeclared
terminal rejection, digest binding, dirty entries and mixed incoming base masks.
Four full-state protected containment runs pass during export. Before/after
source, program and dependency hashes match; exporter exits zero.
Independent Python ABI evaluation matches all 512 audit mask words, including
zero-padded lanes. Protected validation then compares eight independent physical
MR streams with zero MR on 2,214 inputs (17,712 stream/input comparisons): 32 audit,
541 saved failing census, 256 structured and 1,385 arbitrary coordinate tuples.
Every certified-known bit agrees. The 541 saved failures include 431 value
failures; 421 have a certified wrong coordinate, leaving ten value failures
uncertified. The audit certifies all 24 failures and none of its eight passing
controls. Structured expected targets are fixture-relative; arbitrary-coordinate
expected fields are placeholders and support no failure-count claim.

This agent has enabled no live search or submission. The coordinator independently
validates the fast evaluator, integrates masks with zero-MR coordinate witnesses,
and controls any source-transfer and screening gate. Full source/ABI/runtime
binding is required for that gate. Large immutable binaries remain server-only
with archive-manifest hashes; source, proof receipts, test logs, audit vectors,
metadata, validators and negative experiments are archived locally.


## Terminal accelerator supplement (16 October 2026)

The separate partial-per-wire v4 proof passes 38 tests and four protected
full-state containment runs. It retains actual symbolic output for every
unresolved wire, rejects incomplete resource/scope traces, and checks zero-entry
preconditions within application. Its exported Boolean mask is BYTE-IDENTICAL
to frozen v3, so it adds no coverage. This is a useful negative improvement result;
v3 remains the frozen source certificate.

A separate protected transfer validator compares candidate25 physical MR streams
with ORIGINAL zero-MR coordinates on v3-certified-known bits. All 2,214 inputs
and eight independent candidate streams pass; 421 of 431 saved value failures
remain certified. It checks candidate SHA256
`180af069679ffa33b099b200d3337d6fc6c20a451a72508a40dea6617150dc64`,
original stream SHA2a522394..., and frozen mask SHA560c12d5.... This finite replay
supplements the coordinator's universal cache-equivalence transfer certificate;
it does not establish transfer on its own. Its 16 native tests pass, exit is zero,
and before/after hashes match.

The frozen MRMASK01 program's backward compiled-node liveness removes only one
node. Last-use slot scheduling reduces workspace from 506,558,784 to 339,456 bytes
for 512 inputs, retaining 7,914,980 instructions and 5,304 live slots. Every plan
instruction and final root is independently checked against its exact original
node ID. Audit and 11 randomized 512-input trials across widths1..8 match every
reference output word (393,216 words), with five corruption and five runtime
negative controls. Its MRSLOT01 plan and evaluator remain separately frozen.

Exact two-node fusion then reduces dispatch to 4,842,602 instructions using
5,323 slots. MRSLOT02 keeps a16-byte instruction by packing third operand and
destination in16-bit halves; the slot bound is explicit. Fused kinds reconstruct
parent(child(a,b),c) for XOR, AND and OR. All operations and roots reconstruct the
original v3 DAG under an independent checker. Exhaustive ternary truth tables,
audit and randomized comparisons pass all widths, including 393,216 reference
output words and 1,327,104 truth-case/root/width combinations. Five plan-corruption
and five runtime controls reject. Caps and theorem coverage are unchanged.

The fused plan SHA256 is
`1ccbbfc4a45b8d359be9ce21eb4640c72bb9bfe9bffb35f5630c0d13da3f2f8a`;
its evaluator library SHA256 is
`dc8219ae84c21e244ec0e1b92a14e9d0705faf7ebced04a2663499a75a6af1a0`.
Full512 workspace is 340,672 bytes; width64 workspace is 42,584 bytes. In one
same-process comparison, full512 median is25.80ms versus60.42ms for the original
DAG interpreter; width64 median is18.12ms. These are evaluator timings; integrated
throughput and concurrent-worker performance are the coordinator's separate gate.
Header mask_fused.h documents the complete ABI and inactive-word handling.
No nonce search or submission was launched by this agent.


## Bounded nary runtime alternatives: terminal performance negatives

Fanout-one XOR expansion with cap8 leaves reduces the Boolean plan further to
3,014,234 instructions and 5,295 slots when single-use AND leaves are absorbed
as bounded sums of products. MRSLOT03 plan SHA256 is
`65de4a60334f7484197735ab30d524b6d6d06e7cad101e192e19ee9b0e9c7326`.
Every instruction/root reconstructs the original frozen v3 DAG; seven corrupt
plan/source-map controls reject. Both looped and unrolled/branchless kernels pass
all 508 bounded linear/product layouts over 2,015,532 exhaustive assignments,
the earlier ternary truth tests, and all 393,216 audit/random reference words
across widths1..8. The branchless variant's constant-one slot0 precondition is
explicitly enforced and has two additional rejection controls.

A controlled, randomized interleaved comparison on 16 fresh 512-input trials
matches all 262,144 compared words. MRSLOT02 fused remains fastest: median17.71ms
at64inputs and25.02ms at512inputs. Looped nary costs23.76/26.64ms; unrolled nary
costs25.61/27.96ms. They are semantic passes and performance negatives, preserved
without replacing the selected MRSLOT02 library or frozen v3 certificate. All
owned research jobs are terminal; no live nonce search was launched by this agent.


## Width1233 follow-up (16 October; terminal bounded negative)

Complete original4b high-wire census covers3442 lifetimes/48681 references. Strict borrowed mixed-carry contract requires donorC wholly unreferenced, A/B stable, Z read-only, exact scope/phase/MR cleanup and dead old measurement bit. Native primitive tests pass512 exhaustive first-carry cases and65536 arbitrary bit-parallel borrowed-carry cases. Capped-affine queries find2075/2076 identities, but124 conditional-entry cases need an unproved cleaner-hoisting contract. Strict global-entry coverage is1951 atcaps32/128 and1952 atcap512. After checked paid rules,709 lifetimes remain unresolved and added unconditional T is753 (32/128) or752 (512); no complete Q1233 candidate exists and these costs already exceed the product margin. Untouched native source remainsQ1234. No generation/census/nonce search was launched for this route.

[Proof and limitations](width-contracts-proof.md). Incremental immutable archive `evidence-width-supplement.tar.gz`,SHA256 `3b5faa0cf6bf60e292db91f602964a2648ea921956c9c8b3bd9017ba9270ed8d`:95 manifested files,7 server binary references; all local manifest entries verify. Historical CRLF wrapper receipt errors are preserved; separate LF-only unchanged-binary/exact-JSON recheck exits0. All prior mask artifacts and active product25 libraries remain unchanged.


## Immutable mask root cones (16 October; terminal source-only negative)

Frozen v3 has463 constant dependency1 roots (always unknown),49 nonconstant roots, no constant dependency0 root and only1 dead compiled node. All49 nontrivial cones are large: two are89.94% of the DAG, the other47 exceed99.65%. Full per-root/group1..64 census plus21 independent DFS/original-node-identity reconstructions PASS in5.67s on one core. [Report](mask-cones-v1-report.md). Archive `evidence-mask-cones-supplement.tar.gz`,SHA256 `32d624bd849f7e488a780a5d701a380b09e9c8c5bbcebad041838f1f76a43d17`,15files/2serverhashrefs, all locally verified. No production change or speedup claim.


### Width scope correction

A final review found124 affine identities start inside Push scopes and need an unproved cleaner-hoisting contract. Strict global-entry loan coverage is1951 atcaps32/128 and1952 at512, leaving709 unresolved lifetimes; paidT unchanged753/752. The earlier2075/2076 and585 counts were optimistic query accounting. Original raw evidence/archives stay immutable; `evidence/width-scope-correction-v1.json` records every excluded entry. This strengthens the terminal negative.

### Lazy mask source analysis (terminal negative)

Existing32-input audit, both child orders, packed32 and8scalar lanes: packed traversal needs99.816–99.986% of frozen DAG nodes, scalar lanes96.7–98.1%; large XOR backbone prevents useful absorbing shortcuts. No lazy runtime built. Archive `evidence-mask-lazy-supplement.tar.gz` SHA256 `1bf8fcce985e741ad156b5fbc6e324d3b6736acf4716e1d4f0f8c4ea3115cdfa`,13files/4serverrefs; all local manifest entries verify.


## Deferred expected-sum scalar API (validated, isolated)

New `scalar-split-v1/libscalar_split.so` SHA365407f4d6922f4cedeaa23c896d4f3ffd53b264dbfa9689bea774988e52695d preserves original immutable sources/library and pinned clean vendor. Protected4096pairs/24576coords,81independent edgepairs,29partial/invalid/guard controls PASS. Nine pinned fresh131072-input paired rounds: full10.4828us vsP/A-only9.9759us, pairedratio.94940; deferred64batchadd.588us/selectedpair. Caller musttrackexpectedReady and fill before every comparison/fullfallback. Root owns disabled integration; no production change here. [Report](scalar-split-v1/REPORT.md). Archive `evidence-scalar-split-supplement.tar.gz` SHA9eddecdeb5f77498e73500a12a5f5160cf46d9502b498bbac0e7470f6fe6a5a4,42files/3serverrefs, locallyverified.

## Candidate67 source/known-bit controls (terminal PASS)

Frozen268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d independentlyhasQ1234/B54995 and four physical256-slot ABIs identical to original. Jointworkspace54995 covers original45701. Universalcert303a75ec/per-inputd774c492 were available and pinned before unchanged protected validator2214inputs*8candidatephysicalMR streams:17712known-coordinatecontainmentchecks PASS against ORIGINALzeroMR. Saved541inputs catch421;32auditcatch24;256structuredcatch125;1385arbitrary containmentonly. [Report](candidate67-knownbit-report.md). Archive `evidence-candidate67-controls.tar.gz` SHA8433b1dd26f914e5eafdb0498c4537f939c1bfa3ab764ba0ec1e46c86495808b,30files/7serverrefs, locallyverified. This empirical supplement does not replace the separate universal transfer certificate.

## Terminal auditor independent review

Rootaudit-terminal.py SHA70dd1d4378b498600027aefabbe7e170a2c356a9a9571773766aa148d768348e andtest8286d3f1 reviewed onlyfromsource. No materialfindings;23stock adversariallanecontrols and11independentfullsyntheticcontrols PASS, with globalprefixindependentlyenumerated. No productionlogsread orrootfilesedited. [Review](review/terminal-audit-v1/REVIEW.md). Archive `evidence-terminal-review-supplement.tar.gz` SHA0db4231b6b1f9026ec64c2b7963336a559d87ea3b535f7c72091a53d36667420,8files, allmanifestentriesverified.


## Deferred-sum integration review correction (terminal negative)

The isolatedCAPI validation remains valid, but root's attempted drop-in integration is rejected. Initialreview checkedcomparison/fallbackReady paths and missed `rail_fast_ffi::rail_flags`, which usesexpected sum inreverse-denominator `model.sub(o.0,e.0)` BEFORE `expected_one`. Rootdisabledvalidationfound81/128first-witness rowdifferences; independentownedreview reproduces81frompreservedfixtures. Allgatesfalse,productionunchanged. [Correctedreview](review/lazy-sum-v1/REVIEW.md); initialincompletereview is explicitlyhistorical. Archive `evidence-lazy-review-negative.tar.gz` preservesmissedconsumer,sources,rowsandcorrectedreceipt. P/A-onlypreparationspeed doesnotestablishthisintegration'sequivalence.


## Bounded NUMA affinity comparison (terminal, no robust win)

Immutable disableddispatch binaryfa676f13,FAST_ZERO_DISPATCHabsent,3paired4096-nonce trials4threads,unboundversusnode3CPU+memorybind. All6complete4096rowsets identical; gatesfalse,productionunchanged. Medians17.630565sunboundvs18.275030sbound(3.66%slower); pairedratios1.13697/1.05051/.91739 showmixedresultsunderexistingload. CapturedCPUaffinitymatches54-71/126-143 andboundresidentpages~99.9%node3; separatepolicyprobereportsbind3. [Report](numa-affinity-v1/REPORT.md). Archive `evidence-numa-affinity-supplement.tar.gz` SHA70dd36efc52560664f07fa5d77fd204e7bc072cbdf2f378746a5a5800819acd7,43files/10serverrefs; allmanifestentriesand6rowidentitiesindependentlylocalverified.24576repeatedtimingattempts=4096distincttimingnonces,notoperationalsearch. Four-threadbudgetreleased.
