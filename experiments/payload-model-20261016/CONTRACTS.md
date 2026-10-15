# Rejection-certificate obligations and exact local results

The corrected population classifier is **not a rejection certificate**.
Zero false positives on262144 inputs is finite evidence, not an all-input proof.
The following source-derived components are useful, but do not discharge the
complete composition proof.

## Fixed source binding

Public source `4b2ec52fc55da796aa8f5ef851290297e8706424`:
`y15_onefold.rs::fold_window` uses57 bits for forward ticks0…99 and56 otherwise.
The old model imported a different source's57-bit prefix ending at55.
Four false positives first diverged at divide ticks91,86,84,87, respectively.
Their incorrect capacity losses were2^51,2^51,2^52,2^50. Replacing55 by99
removes exactly those four false positives on the full preserved population,
while retaining243 true positives. No input or packet special case was added.

## A local inherited-cut lemma

All144 inherited census edits are CCX edits:74 deletions and70 reductions to
CX on one surviving control. The exact pre-census stream is reconstructed by
undoing those changes in the final frozen stream. All144 original neighbourhood
SHA3 anchors match the production source. It has11,630,790 operations, including
the untouched96-X identity tail.

For an enclosing classical base c and two original controls a,b:

* A deleted CCX differs from the original exactly when c&a&b=1.
* A CCX reduced to CX(a) differs exactly when c&a&!b=1; interchange a,b when
  the other control survives.

These Boolean identities are valid for every possible local wire assignment.
The exported table `cut-guards.csv` and2304 exhaustive local assignments verify
the row transcription. If every predicate is false at its original pre-census
position, induction over the stream proves all144 edits preserve coordinate
values. Arbitrary measurement results may be fixed throughout that induction;
a universal abstract proof of predicate0 is stronger still.

**Missing:** the arithmetic model does not yet derive these internal wire
values, or sound input predicates sufficient to make them false. The cut table
and local lemma therefore do not authorize direct rejection. The parent task
is independently testing exact abstract circuit evaluation for those queries.

The four corrected false-positive inputs activate none of the edits, on either
the reconstructed pre-census or final path. They already pass the raw-builder
and pre-census circuits, so inherited cuts did not repair their modeled error.
Some other diagnostic failures activate edits; those remain part of the proof
obligation. The pre-census/final trace uses the protected simulator and agrees
with its independent observer on all qubits, bits, phase and Toffolis.

## Finite seed halving

Production `pingpong.rs::mod_halve_pm` subtracts parity*f only on its low
w=`go_fs("GO_FG_P")` bits, then rotates and restores the parity bit at the top.
For frozen public4b, w=53 and f=2^32+977. Let T be the unsigned256-bit input,
o=T mod2, M=2^w−1, and

    V = (T & ~M) | ((T − o*f) mod2^w)
    S_actual = floor(V/2) + o*2^255.

This follows from the truncated controlled-subtraction and the three
`finish_halving` operations: rotate down, XOR the saved parity into the vacated
top bit, and erase that saved copy. The corrected low bit is0.

For canonical T, ideal modular halving is S_ideal=(T+o*p)/2. Thus

    S_actual − S_ideal = 2^(w−1)

exactly when o=1 and (T mod2^w)<f; otherwise it is0. In particular T=1 has a
source-observed seed error2^52. Endpoint-unit and FM-loan guards do not test
this capacity condition. A model using ideal half must prove the predicate
false or return unknown; alternatively it must retain the actual unsigned word.

## Optimized tick0 is a different integer expression

`P3_T0_ONE_ADD=true` replaces the generic three-add integer by one shifted add.
For sign bits n0,n1,n2, define

    a0 = n2 & !n1, a1 = a0 & n0
    j = 1 if n1 else 0 if a0 else 2
    sc = n0 XOR a0, tc = n2 XOR a0 XOR a1
    X = 2^j * (T XOR (tc*MASK256)) + (S XOR (sc*MASK256))
    Nm = sc + 2^j*tc.

The actual forward fold uses this X and Nm. It does not use the generic
X=T+S0'+2S1'+4S2'. Before capacity loss, their field maps agree when T=2S modp:
both coefficients are9−2n0−4n1−8n2 times S. They can differ after a finite fold.

For T=2^63−1, the53-bit seed halve is ideal, signs=(1,0,0), extra=0. The
optimized one-add output differs from the generic model by2^54. This case is
included in the protected source primitive replay. The model therefore needs
the actual integer expression, or a guard proving the two truncated folds
coincide. Merely checking clean terminal loans is insufficient.

A one-sided counterexample is also confirmed through eight protected MR
replays: T=f, S=2^255 (the seed is ideal), signs=(1,0,1), extra=0. The optimized
source output equals the exact field result, whereas the generic model differs
by+2^54. `t0-witness.log` records this source-correct/model-wrong case. The same
tape pattern occurs in the point-stage fixtures, but no full valid-curve point
addition witness with this special payload is claimed.

## Forward fold arithmetic

Let E=X>>256, L=X mod2^256, s=3+extra,

    A = L + E + (E−Nm)*(f−1)
    m = A * inverse(f mod2^s) mod2^s
    C = E + (E−Nm−m)*(f−1)
    W = (L & ~MASK_w) | ((L+C) mod2^w).

The source's unsigned fold-and-rotate word is

    R = floor(W/2^s) + m*2^(256−s).

The low s bits of W equal m. Without dropping the carry at w, the expression
equals division of the intended field numerator by2^s modulo p. Dropping
c=floor(((L mod2^w)+C)/2^w) changes that field value by−c*2^(w−s).
These equalities are integer algebra; using the right X, Nm and source-specific
w is essential. `source_payload.py` records the corresponding source formulas.

The production seed plus optimized tick0 gates were replayed on928 boundary
assignments using the actual live budget1105 and pinned recipe. All unsigned
seed/fold outputs matched these formulas. Every qubit, bit, phase and Toffoli
matched the protected simulator. The128 nonideal seed cases were retained,
rather than excluded from the test. These are component tests, not a full
point-addition score or a machine-checked all-input gate proof.

## Still required for complete arithmetic certification

The contract must also cover the source's coordinate/seed finite folds,
ordinary and terminal payload cells (including the observed multiply tick127
miss), endpoint negation/representation, square accumulation windows, and all
borrowed-scratch promises. The abstract model's fixed field formulas currently
idealize some of those operations. Every unsatisfied promise needs a sound
unknown predicate or an exact source-derived value model. Exact postpass
composition and cut-inactivity must then connect those primitive contracts to
the complete frozen output. None of these remaining obligations is waived by
the corrected population result.
