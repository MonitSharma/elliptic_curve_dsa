# Exact cost rewrites for the frozen Q692 circuit

These are arithmetic equivalence arguments, not a proof that the underlying
bounded point-addition algorithm works on every curve input. No precision,
quotient capacity, schedule envelope, nonce, test packet or protected file is
changed by the cost rewrites.

## Joint enable predicate

Immediately after each odd-divisor restoring step, SX0 is zero. Let A be ACT,
R the retained quotient decision, and S the disjoint SY selector predicate.
The old unclipped implementation computes S into SX0, increments the window
under A AND R AND SX0, and erases S. The rewrite computes A AND R AND S into
SX0, performs a single-control increment, and erases that predicate.

The increment preserves A, R and SY. Its dirty passengers are restored. Thus
the inverse predicate erases SX0 exactly. Both versions act identically on the
entire computational basis, including inactive inputs and dirty passengers.
All predicate gates here are X, CX and CCX; they add no relative phase. This
permutation equivalence extends by linearity to arbitrary superpositions and
entanglement with the passengers.

## Exact size clipping (v2, retained as an alternative)

For an n-bit unsigned size V, the terms of V < K have their highest differing
bit i at a set bit of K: higher bits equal K and V_i=0. These terms are
disjoint. Their product with the disjoint SY cubes and A AND R is therefore
also disjoint. XOR into a zero flag computes the same conjunction as the
old selector plus the negated `ge_const_compact(V,K)` result. For K >= 2^n,
the condition is true for every encoded V, matching the original comparator.
The runtime threshold remains exactly K=257-j.

## Linear multi-control increment (v3)

Normalize the m literal controls with X gates on negative literals, and regard
them as a little-endian m-bit register C. Let W be the n-bit target. The
concatenation represents C + 2^m W. Adding one modulo 2^(m+n) changes W
exactly when C=2^m-1. Subtracting one modulo 2^m from only C restores every
control, leaving the carry into W intact. Undo the negative-literal X gates.

The existing `inc_dirty_free` implements an exact modular increment using
arbitrary restored passengers: subtract D, complement D, subtract its
complement, restore D. Since D + complement(D)=2^r-1, the total change is
+1 modulo 2^r. Its inverse supplies the low-register subtraction. The new
helper checks that controls and targets are distinct and filters passengers
to exclude them. There are no measurements or phase gates in this helper.

The helper selects the old prefix circuit for small instances when its
Toffoli count is no greater. This selection depends only on register lengths,
not their values or validation samples. Both branches implement the same
exact permutation.

## Independent checks completed

- v1, v2 and v3: the existing 17 native component tests pass (groups 7/5/2/1/2).
- v1, v2 and v3: 16 source-bound tests using the unchanged independent Boolean
  phase kernel pass, with 700 fixed-input forward/inverse audit calls. Each
  audit checks all measurement outcomes for its fixed 64 input lanes.
- v2 and v3: 524,288 paired old/new full-state cases pass, covering all 256
  encoded SY values, all 256 encoded SZ values, both ACT states, both divisor
  heads and both partition drivers, with arbitrary dirty words and exact
  inverse restoration. These particular component streams contain only
  X/CX/CCX/SWAP gates, so they introduce no relative phase.
- v3 helper: 582,930 exhaustive small-word cases pass for target lengths 1–8,
  control counts 0–6, three literal-sign patterns and zero/one/arbitrary dirty
  states. Expected results are computed directly from integer arithmetic;
  every control and passenger, plus inverse restoration, is checked.

The first standalone differential wrapper failed to compile because separate
copies of the point-addition module produced incompatible gate types. That
failed wrapper and its logs are preserved. The corrected wrapper copies only
the original routines into a private test tree and compares both routines
using the same gate types; neither candidate source tree is modified.

## Construction cache (v4, pending full stream equality)

The optional fourth version memoizes pure reciprocal gate recordings. A key
contains every register, scalar argument and local cancellation setting.
These constructors allocate no qubits or classical bits, and emit only
replayable gate records. Returning the identical cached record therefore
preserves emission order and operations. The cache is bounded to two million
gate records. Test-only constructor probes bypass it. Acceptance still requires
the complete v4 serialized stream to equal the v3 stream byte for byte.

## Conditional-one size control (v5)

Let the zero flag G receive A AND R AND S. Then G=1 implies R=1. XOR the
exact size comparison E=[SZ >= 257-j] into R. Under G, the modified R is
1 XOR E, so G AND R equals A AND R_original AND S AND NOT E. When G=0,
the target increment is disabled irrespective of R's arbitrary value.
The controlled increment preserves both controls. Reverse the size comparison
to restore R, then reverse the predicate to restore G to zero. This uses no
additional wire and preserves the complete runtime size cut. It is an exact
basis permutation on all metadata and dirty passenger states for which G
enters zero; it also preserves relative phase.

v5 passes the same 17 native tests, 16 phase tests (700 audit calls), and
524,288 paired full-state cases as the earlier rewrites.

## Factored virtual size rotations (v6)

The old rotation applies each selected swap once for every disjoint cube of
the virtual size predicate. Compute their XOR into the already-clean SX0,
apply the swaps under that one flag, then uncompute the predicate. Exactly
one cube can hold, so the XOR is the same enable value. The rotation touches
only the ring and restores borrowed passengers; SZ and SY controls are
unchanged. SX0 is disjoint from those controls and the rotation ring.
The original routine is retained as an independent reference. Only the
protection and parking call sites that already return SX0 clean use the
factored routine. No size or support envelope is narrowed.

## Submission risks that these rewrites do not repair

The source retains the original quotient capacities and finite reciprocal
precision. Its expected-negative component test above the 25-bit HT capacity
still passes by demonstrating that failure; it is not a positive correctness
test for that input. Therefore a complete benchmark pass would establish the
benchmark result only, not arbitrary-input point-addition correctness.

The refreshed workflow has a 45-minute limit and uses the 32-vCPU Ubuntu runner.
[Blacksmith's documented memory](https://docs.blacksmith.sh/blacksmith-runners/overview)
for that runner is 128 GB. The original Q692 evaluation alone took 1:56:33 on
the local Xeon server and peaked at 128.96 GiB. Normal build output, memory and
runtime must be checked on the reduced source. A diagnostic counting sink and
an externally streamed circuit do not qualify the normal submission path.

## Conditional size-bit loan (arithmetic repair prototype)

Let G be a retained predicate selecting an active large-SY shot and one value
of SZ0. On a selected shot ACT=1. For the SZ0=1 branch, XOR G into SZ0 to
clear it; for SZ0=0 it is already clear. Flip ACT, making it a clean reciprocal
flag on selected shots. R24 plus SZ0 provides 25 remainder lanes. SX0 holds G
through the reciprocal's forward window computation and inverse remainder
computation. For every unselected shot, G=0 disables all window writes, and
the exact forward/inverse pair restores arbitrary remainder and flag values.
Restore ACT and SZ0, then uncompute G from the restored controls.

The admitted large-SY geometry has SZ+SY<=258, SY>=96 and SZ>=101. Thus
SZ<=162, and TC27's window positions never require a runtime size cut.
The driver instead uses the broader non-clipping constructor range 101..230.
SX0, ACT and SZ0 are disjoint from the divisor, window targets and dirty
passengers. The virtual leading divisor bit retains the original compact
comparator convention even though its physical ring wire is in the remainder.

The independent proof computes each reciprocal quotient bit by integer
division, calculates the exact window sum, and compares the entire 692-wire
state. It covers all 256 selector words, both ACT values, SZ101..162,
zero/arbitrary dirty storage, arbitrary unselected remainder state, and the
inverse, across both partition policies. It passes 131,072 lanes and 4,096
audits covering every measurement outcome. This proves the storage driver
in its stated domain. It does not prove the surrounding complete point adder
or the separate extended-map rewrite.
