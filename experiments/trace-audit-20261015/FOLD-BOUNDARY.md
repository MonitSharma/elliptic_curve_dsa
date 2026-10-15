# Exact correction for a truncated payload fold

15 October 2026. Algebraic result and finite-model validation only. No quantum
implementation, full point-addition pass, or resource claim.

This addresses the separate equal-input division counterexample, not the 186
random value failures attributed to walk rails.

Let N=256, f=2^32+977, p=2^N-f, d=2^s (s=3..6), and w be the fold window.
The three complemented additions produce X. Write E=floor(X/2^N), L=X mod 2^N,
and let Nm be the weighted sign bits. Define

```text
A = L + E + (E - Nm)(f - 1)
m = A * inverse(f, d) mod d
W = A - m(f - 1)
```

Then W mod d=m. The signed integer rotation expression is

```text
R(W) = floor(W/d) + m*2^(N-s)
d*R(W) = A + m*p
```

Since A is congruent to the required signed three-add result modulo p, R(W)
is the correct field division by d. This identity permits negative W; it does
not silently reinterpret W as an unsigned N-bit integer.

The implemented low-window replacement preserves L's upper bits and drops the
signed carry across bit w. With

```text
C = E + (E - Nm - m)(f - 1)
c = floor(((L mod 2^w) + C) / 2^w)
W_window = (L - (L mod 2^w)) + ((L mod 2^w) + C) mod 2^w
         = W - c*2^w
```

and w>=s, the low s bits are unchanged. Therefore the exact field correction is

```text
correct_output = R(W_window) + c*2^(w-s) mod p.
```

This is a signed correction: a borrow means c=-1. Merely adding another window
bit does not remove it.

For E in [0,7], Nm in [0,7], m in [0,63], the conservative bound is
`-300647779040 <= C <= 30064777911`. At w=56 or57, c can only be -1,0,+1.
That reduces the required control to three cases, but gives no circuit cost or
clean-uncomputation guarantee.

## Evidence

The Boolean transcription of `fold_fwd_v2`'s quotient core agrees with
`k=Nm+m-E` for all 16,384 combinations of low six bits, E, Nm and shift. This
checks the quotient equation against the inspected source logic, independently
of the abstract modular derivation; it is not direct observation of internal
qubits or a test of the later addend netlist.

In the saved tick120 counterexample, E=1, Nm=6 and s=3. The core gives k=5,
hence m=0; W=-856 and c=-1. The corrections are:

| Window | Saved wrong output | Signed correction | Correct field output |
|---|---|---|---|
| 56 | 2^53-107 | -2^53 | p-107 |
| 57 | 2^54-107 | -2^54 | p-107 |

The exact model reproduces both saved outputs. Exhaustive enumeration of
524,288 toy cases covers every 7-bit stored target/source, every sign letter,
all four shifts and windows max(s,5), with p=111. All corrected values equal
direct modular arithmetic; 483,365 uncorrected values differ. The toy modulus
is deliberately reported as composite: the identity only needs an odd modulus
to invert powers of two. Its many signed carry values exercise the general
formula, not a fitted production error rate.

See [executable model](fold_boundary_model.py) and
[results with evidence hashes](fold-boundary-result.json).

## What remains

Directly observe the production carry/quotient wires to verify all assumptions
at the failing tick. Then design a reversible correction with a clean control
and prove its measurement phases; changing the live value may invalidate existing
carry-erasure shortcuts. Measure the total added cost before choosing this over
other arithmetic representations. A generic modular correction at every payload
tick may consume the candidate's Toffoli margin. The formula is not a submitted
repair and does not establish a new Toffoli or product record.
