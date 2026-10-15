# Source binding for value-only measurement-macro proofs

The frozen original circuit is revision
`4b2ec52fc55da796aa8f5ef851290297e8706424`, final stream SHA256
`2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e`.
Gate-inert source markers reproduce the entire original raw builder stream,
SHA256 `ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69`.
They do not emit gates or change any protected harness or simulator file.
The raw dump is a component boundary, not a new complete circuit or score.

The first global symbolic loss is final operation 688826, HMR q1106 to b1565.
It belongs to the forward tick-3 `y15_onefold::body` Y21 `top1` cleanup.
The source's false branch is `nbx & bit0`: reconstruct add-1 carries, apply a
Z on the top carry, call `cmp0`, then uncompute/reset the carry chain.
Here `nbx` is b1566, the complement of the earlier `bitx` measurement, while
`bit0` is b1568. This explains their original write order (b1566 inverted at
687330, b1568 measured at 687604) without assuming any data or scratch value.

The exact source false branch is raw [688303,689304). Its final counterpart
is [688341,689350), 1009 operations. Inside it, `cmp0` calls the 19-bit,
borrow-seeded phase comparator at raw [688684,688905). The complete Y21
clause, including the earlier bitx branch and intervening unconditional
measurement of m0, is raw [687285,689304), final [687323,689350).

The final false branch differs from raw by a deleted top-chain AND into q767,
ten added phase gates, and one deleted conditional CZ. The full diff is
preserved. These inherited changes are why raw component identity cannot be
used as a substitute for a proof of the actual final interval.

The source arithmetic explains the expected value action. The carry chain
uses `s1(i)=b[i] XOR s2 XOR s1` and the actual recurrence
`r_next=z_next XOR ((s1(i) XOR r) AND (T[i+1] XOR s1(i))) XOR r`, where
`z_next` is the arbitrary prior value of the newly allocated physical wire.
The source's intended carry interpretation additionally assumes `z_next=0`;
the value-preservation argument does not. The macro temporarily peels
the target window with these forms, calls a phase comparison, and reverses
the same peels before clearing the carry chain. Affine form hosting uses
explicit inverse CX/X sequences. This restores the data values even when
the temporary carry wires initially contain arbitrary values, provided the
actual recorded block satisfies the indicated inverse/reset structure.

For `lin_and_erase`, the HMR value action is a conditional reset of its
target, and its subsequent phase correction has no net data-value action.
If the target was dirty, its phase correction may be wrong. Thus this is
not a phase-correctness argument or a clean-scratch assertion. Likewise,
all original random draws and conditional classical HMR writes must remain
at their original positions, even under an inactive condition.

The independent prefilter agent proves the actual final blocks against
reset-only projection using universally quantified initial quantum values,
classical entry values and measurement outcomes. That proof is the
acceptance gate. Source labels, unique anchors and protected finite replay
are provenance and validation, not substitutes for universal equality.

The first actual final false branch has 43 quantum wires with identity
action and 37 with the exact action `old AND NOT(snapshot1566 AND
snapshot1568)`, for arbitrary initial values. No clean-entry assumption is
needed. Its classical writes and all measurement draws are preserved.
The sibling also reports all 250 complete Y21 clauses and all 547 comparator
candidates universally equal their reset-only projections.

The complete clauses matter because the first bitx scope constructs carries
that survive beyond its Pop, an unconditional HMR of m0 follows, and later
scopes consume/reset those carries. A closed-Push-only scan cannot certify
the whole value-neutral composition at once.

For comparator-only spans, relative Push/Pop depth must remain nonnegative
and return to zero. A universal proof at incoming base=1 lifts lane-wise
to arbitrary incoming base: base=0 makes every quantum/classical value
operation inert while retaining random draws, and balanced snapshots restore
the caller's base. Phase is excluded throughout this lifting argument.

`bound-spans.json` records all 250 false branches. `complete-top1-spans.json`
records their complete clauses. `comparator-spans-v2.json` records 547
diagnostic comparator candidates, with exact anchor records, source labels,
balanced boundaries and actual-final-stream hashes. All exported TSV ends
are exclusive. The prefilter's independent per-final-span proof certifies
which intervals may be projected; no circuit source or nonce was changed.
