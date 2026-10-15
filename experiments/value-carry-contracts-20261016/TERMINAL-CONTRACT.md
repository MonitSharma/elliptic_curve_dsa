# One-bit terminal precision contract

This report is a local theorem and a source-interface investigation. No
candidate circuit, record, failure improvement, or global correctness theorem
is claimed.

Let `a,T` be the original last two accumulator bits, `C` the incoming carry
to `a`, and `s` the sign extension repeated in those two addend positions
and in the new next position `U`. The existing ladder hosts
`A=a XOR C`, `B=s XOR C` and applies `CCX(A,B,T)` before restoring its
Clifford controls and applying `C XOR s` to `T`. Its final top sum is
therefore `T XOR A*B XOR C XOR s`.

The exact outgoing carry relative to the repeated sign is

```
delta = MAJ(T,s,MAJ(a,s,C)) XOR s
      = (a XOR s)*(C XOR s)*(T XOR s)
      = (A*B XOR B)*(T XOR B XOR C).
```

The repaired terminal writes `U XOR delta`. This is a one-bit wider
modular signed-tail addition: all original low sums are unchanged, the next
sum includes both its sign bit and its incoming carry, and every payload
bit above `U` is explicitly unchanged. It does not propagate the remaining
carry into those higher bits. Thus its defined precision is `w+1`, exactly
the arithmetic truncation used by a width-`w+1` ladder, rather than a full
256-bit addition.

The identity relating `delta` to a mathematical carry is conditional on
the incoming `C` actually being that carry. The gate theorem below is
unconditional for arbitrary hosted controls, including dirty inherited
arithmetic states. A full source-family certificate must distinguish those
statements. Existing approximate arithmetic is not assumed correct merely
because its current control is named a carry.

For a distinct donor `d` proved zero at this terminal, replace the old CCX
by:

```
CCX A,B,d
CX B,d
T ^= B XOR C
CCX d,T,U
T ^= B XOR C
CX B,d
CX d,T
HMR d -> m
CZ A,B controlled by m
```

Every gate runs under the same captured original guard. The new HMR is
physically consumed even when inactive. The donor is restored zero, the old
target receives exactly the old `A*B`, all other old quantum and classical
values are framed, and the measurement phase `m*A*B` cancels exactly.
The primitive adds one CCX, one physical measurement, no quantum width,
and a fresh classical measurement bit. Arbitrary initial phase is preserved.
Its universal theorem has no scratch precondition except this donor zero.

After affine control hosting, the physical wire named `ci` can contain
`C XOR 1` if the sign is constant and that wire hosted `B`. The contract
also covers `C=B` and `C=B XOR 1`; source admission must bind the correct
case. It may not read the physical `ci` as an unchanged logical carry by
assumption.

A second theorem permits an arbitrary dirty donor. Four CCXs realize the
triple-controlled action on `U`, restore that donor, and then retain the
original CCX. It costs four added CCXs, no measurements, and no qubits.
This fallback has no donor-zero premise and no new random stream. Both
versions require distinct physical donor, target, and hosted controls.

For padded-zero square windows, the same argument specializes to
`delta=p*a*T`; a clean donor costs one added CCX and one HMR with the
corresponding `CZ(p,a)` correction. This is not yet bound to a square
source family.

`prove-terminal.py` proves the formulas using canonical square-free Boolean
ANF with no caps. It checks all six donor/hosting contracts, the square
specialization, and a deliberately omitted-CZ phase negative. An independent
integer addition oracle checks 174,752 exhaustive small cases and 20,480
wide cases. `protected_terminal.rs` uses the unchanged protected simulator
and independently computes two majority carries. It checks every quantum
bit, classical bit, phase, and physical draw count in 1,572,864 cases,
including guard snapshots whose physical bit is overwritten. Its missing-CZ
negative produces 24,555 phase errors.

The remaining source obligations are concrete: bind actual surviving
terminal bytes, the sign extension and logical-C frame, the complete old
fold's exclusion of `U`, a globally proved clean short donor or the dirty
fallback, identical guards and live interfaces, and unchanged inherited
table checks. A complete width-57 generated block is an independent
arithmetic comparison target where available; different allocator and MR
layouts must not be mistaken for an arbitrary dirty-entry equivalence.
