# Both back-seam comparator precision

Let U and C be the actual unsigned 256-bit words on the source-bound sum and
classical operand at a back-seam comparison. No claim that U is an ideal curve
coordinate is needed for this definition. Let Pk be strict less-than between
their top k bits. For every pair of unsigned words,

    P20 <= P21 <= [U < C].

This is an exact lexicographic identity. A prefix comparison is true only when
the first differing position in that prefix has U=0,C=1. Extending the prefix
can only resolve some former equal-prefix cases; it cannot reverse a previous
decision. If d=U235 and c=C235, the carry out of the new lowest complement/add
position is (!d)&c. Passing this carry into the old high20 comparator computes
exactly P21. This requires no relation between U, C and the measured overflow.

The actual source-bound middle at each seam has a universal exact immutable
XOR/AND-DAG proof that every sum bit235..255 and overflow is restored to its own
entry value. All entry quantum/classical values are arbitrary and every HMR is
fresh. No clean scratch assumption is used by this middle-interface theorem.
The two inherited-edited middles remain verbatim; their temporary parity-form
writes to overflow are admitted only by the complete proof. The exact R5 source
prefix, unchanged classical loads and complete helper/suffix also bind uniquely.

Whole-original-prefix conservative propagation proves each comparator's19
carry scratch wires and20 classical-load wires zero at their respective entry.
The cb word is not mutated inside the complete source region. Thus the compare
operands are exactly the actual U/C high bits, with clean allocated comparator
scratch, for arbitrary ABI inputs and every measurement assignment.

After the original HMR clears overflow q, under its unchanged outcome m, add

    q ^= c; q ^= d & c.

These are a classical-conditioned X and CX. They compute (!d)&c into the cleared
overflow wire. Supply q to the comparator's first carry, including its measured
CZ correction, and restore it. Applying the same two conditioned Clifford gates
in reverse clears q. Two further CXs conjugate and restore the first carry's
control. Hence each site adds six Clifford operations, zero Toffolis, zero
physical qubits, and zero measurements. Neither classical writes nor snapshot
scopes change. The ordered Toffoli-condition skeleton is identical, so every
coupled execution has exactly the same Toffoli count.

Old/new local ANF plus independent BDD proofs quantify every data/classical
entry bit and every internal measurement. Both restore all data, clear measured
target/carry scratch, and produce exactly

    old phase = m*(entry_overflow XOR P20),
    new phase = m*(entry_overflow XOR P21).

Each of the four contracts has4,096 protected arbitrary-bitplane checks; a
deliberately incorrect Clifford correction must fail. Added lower data wires
are restored and every original classical HMR outcome/write is retained under
the identical measurement-word coupling.

The stronger assertion [U<C]=overflow is deliberately NOT claimed. Each exact
R5 prefix has105 auxiliary entry wires whose cleanliness remains UNKNOWN under
conservative ternary replay; immutable-atom replay leaves104 at the first site
and105 at the second. This may
reflect lost correlations or inherited arithmetic failures. The two negative
cleanliness proofs are preserved. No unknown is assumed zero. Even when the
old predictor error improves locally, other phase errors may cancel globally.
The sole predeclared independent full-circuit paired census measures every
phase/value regression and repair. A failed gate forbids resampling or search.

This is zero-resource-cost failure-repair research, not a global arithmetic
correctness proof or a new resource record.
