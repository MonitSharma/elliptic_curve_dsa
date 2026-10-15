# Exact AVX512 eight-batch simulator — verified research backend

The published original `libsimd8.so` accelerates the complete compact circuit
interpreter without an arithmetic approximation. It has passed protected
full-state differential checks on the frozen public `4b2ec52f` stream.
This is a research backend, not a circuit record or a completed nonce search.
No candidate circuit was changed, no nonce was selected, and nothing was submitted.

## Measured recurring cost

On the Xeon Gold 6154 server, the final same-run comparison was:

| Work for eight independent 64-shot batches | Time |
|---|---:|
| Original exact SIMD kernel | 34.657 ms |
| Preallocated eight-way SHAKE MR matrix | 22.438 ms |
| Combined compute | 57.096 ms |
| Scalar compact simulator including scalar SHAKE | 497.101 ms |

The ratio is **8.706×** for recurring simulation plus measurement randomness.
A preceding loaded run measured 40.769 + 23.458 = 64.227 ms, approximately
7.8× against the scalar result. These timings exclude input curve arithmetic,
advisory selection, one-time hashing, static stack-depth analysis, allocation,
and screening scheduling. They are not whole nonce throughput estimates.
Five repetitions of each kernel are retained in the logs.

The first prototype's 108.6 ms combined result included allocating/zeroing
the 58 MB matrix and redundantly scanning all compact operations for maximum
stack depth. Both costs can be moved out of the recurring caller loop.

## Exactness and evidence

* Compact stream: 11,629,688 operations, 139,556,256 bytes, 906,156 unconditional
  MR/reset draw positions. Register annotations remain in Fiat–Shamir hashing.
* Frozen full stream: 11,630,716 operations; 49 bytes per Fiat–Shamir record,
  including all registers and the complete 96-X identity tail.
* Eight predetermined labels 0…7 were differential fixtures. The full protected
  `fiat_shamir_seed` function independently hashed each complete variant.
  All 9,024 scalar pairs per lane (577,536 bytes) matched eight-way SHAKE.
  Every pair was consumed before measurement randomness.
* All 906,156 measurement words per lane (7,249,248 bytes) matched protected
  scalar SHAKE, including conditionally inactive measurements/resets.
* On 512 actual first-batch Fiat–Shamir input shots, every one of 1,234 qubit
  words, 45,701 classical words, phase, and final RNG byte count matched eight
  separate protected simulators. A separate independent-input 512-shot replay
  also passed, so 1,024 distinct full-stream input-shot replays were checked.
* All 4,096 assignments of four quantum inputs, four classical inputs and four
  measurement outcomes pass a fixture with every executable opcode, nested
  conditions, mutated pushed guard bits, arbitrary initial phase and dirty
  inputs. Negative checks detect changed random-row order and phase, short
  RNG matrices, and stack underflow.
* Eight distinct selected measurement offsets (batch indices
  0,1,2,3,1,2,0,3) match scalar SHAKE at every returned word.

The public 96-X tail is retained by the compact interpreter. For the differential
fixtures, each changed nonce tail is checked to consist of 48 unconditional
identical X pairs; pairs have no net value or phase action and consume no RNG.
Protected scalar replay runs each actual variant tail. Only these identity
pairs differ from the single canonical tail used by the eight-lane interpreter.

## Semantic argument

Each AVX512 lane contains exactly one protected simulator's 64-shot word.
AND, XOR, OR and ANDNOT act independently on those words. Every opcode has
the same Boolean and phase update as the protected interpreter; there is no
cross-lane operation. For R/HMR, a random row is consumed before any decision
about activity, phase changes by target & draw & condition, the active target
is reset, and HMR writes the active measurement bits while retaining inactive
bits. Push stores the old base-condition value; the new base is its AND with
the current classical value. Pop restores that saved value, so subsequent
mutation of the pushed bit does not alter the captured predicate.
Induction over the full stream therefore preserves all wire words, phase,
stack values and draw positions for arbitrary initial words and draws.
The native exhaustive fixture and full protected replay test the implementation
of these equations. CPU AVX512F/DQ/BW/VL support is checked before invocation.

## API and integration

Server: `/home/hclau/ecdsa_research/simd-prefilter-20261015/libsimd8.so`.
Header: `tool/simd8.h`; source: `tool/simd8.c`.
`CompactOp` has five u16 fields a,b,t,c,bt followed by u8 k and padding,
with a compile-time size assertion of 12 bytes. NIL is 65535.
Every q, bit, RNG and stack row contains eight u64 words in lane order.
The caller validates operands/stream shape, prepares maximum stack depth once,
and reuses allocated buffers. The kernel mutates all q/bits/phase and reports
consumed RNG rows. Error codes cover short/extra RNG, stack bounds/imbalance,
and unsupported opcodes; an error is never interpreted as a passing batch.

The sibling prefilter task owns advisory ordering, output/phase/ancilla checks,
early rejection and refill. The kernel itself makes no pass/fail or resource
record judgments. The final selected circuit must still use the unchanged
official benchmark.

SHAKE backend: root-owned `shake8-20261015`, XKCP revision
`4affab454735d54e78156880b3b44e38dcbf765c`, original CC0 notices preserved.
Its original wrapper/header/library and upstream revision are snapshotted in
the evidence archive. `words8` produces the kernel's row-major matrix directly;
`select_words8` produces different exact batch offsets for the eight lanes.

## Preserved negative experiment

`simd8_fast.c` adds separate opcodes for statically unconditional operations.
8,662,785 operations qualify, and exhaustive plus full-state checks pass.
It is slower: 36.199 ms versus 34.657 ms for the original kernel in the same
run. It is retained as a negative experiment and is not the published library.

All jobs finished with exit 0. The final verifier used about 1.0 GiB peak RAM
and one execution thread; builds used four threads. Launch scripts, resource
preflights, PIDs, exit markers, all timing logs and SHA256 source/library hashes
are preserved. No pre-existing workload was stopped or modified.
