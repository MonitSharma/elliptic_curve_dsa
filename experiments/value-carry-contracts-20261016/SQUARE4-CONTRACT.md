# Complete C130 square precision family

The family is all four `square::wcin_windows` calls whose high operand has
130 bits, covering NAF shifts 4, 6, 10 and 32. Selection uses source width
and the complete source-defined term list. It uses no saved failing input,
scored packet, nonce, or input-specific predicate.

All four complete original windows are byte-identical between the gate-inert
raw builder and the final public 4b stream, including every inherited pass.
The next physical payload bits are respectively 154, 156, 160 and 182. No
operation anywhere in its corresponding entire old window reads, writes,
or phases that next bit. Each window has balanced scopes and starts at
depth zero; each replaced terminal CCX is unconditional. The direct source
guard cost is therefore exactly four added Toffolis per window.

Each terminal has physical incoming carry `p`, penultimate accumulator `a`
and top accumulator `T`. These are after any original window complement.
The source addend is padded zero in these last positions. The old terminal
is `CCX(p,a,T)` followed by `CX(p,a)`. Replace only that CCX with:

```
CCX(p,a,d)
CCX(d,T,U)
CCX(p,a,d)
CCX(d,T,U)
CCX(p,a,T)       # original instruction, unchanged
```

The donor is physical q0 in every window. It is distinct from `p,a,T,U`.
It can enter in an arbitrary dirty state and is restored exactly. The two
toggles into `U` cancel its initial donor value and leave `p*a*T`. All
gates are ordinary CCXs and contribute no phase. No zero-donor premise,
measurement, classical write, condition, or quantum allocation is added.

For arbitrary entry quantum values, classical values, original measurement
assignments, guard snapshots and initial phase, the whole new window has
the same old quantum outputs except `U`, the same donor value, every old
classical output, and the same accumulated phase as the old window. The
next bit receives the old terminal's actual `p*a*T` value. This whole-window
relative theorem follows from the exact local Boolean identity, the donor
restoration, literal unchanged prefix/suffix, and exclusion of `U` from the
entire old window. It does not assume clean inherited scratch or a correct
old arithmetic state.

When `p` has its defined incoming arithmetic carry value, this is exactly
the signed add/subtract operation at one additional bit of precision. The
old low window is unchanged, `U` receives its carry/borrow, and every bit
above `U` is explicitly unchanged. For complemented subtraction, a truly
wider source window would complement `U` before and after the addition;
these two complements cancel and leave the same carry XOR into the actual
uncomplemented `U`. The independent integer oracle checks both signs.
This does not claim full 256-bit carry propagation or correctness of
unrelated inherited approximations. Later original windows may read earlier
corrected outputs and run normally.

All original R/HMR instructions and draw ordinals are identical. Their
absolute operation indices move by four after each insertion, but their
instruction sequence, physical targets, classical targets and conditions
are unchanged. Every original classical write and Push/Pop snapshot remains.
The new source uses the original ABI, Q1234, B45701, and 906156 physical
measurement/reset draws. It adds 16 generated/executed Toffolis and no
qubits or measurements. It cannot improve a resource record by itself.

The candidate checks a frozen SHAKE256 digest of every complete original
pre-tail operation before modifying it. Every original pass and table
assertion runs first. All four unique entire-window matches are mandatory;
any missing, changed, ambiguous, overlapping or wrongly scoped region
rejects the whole family. The original identity tail is preserved.

The sole fresh gate was frozen before candidate generation: 32768 batches
of 64 inputs per source, label
`public4b-all-C130-square-dirty-carry-independent-20261016-v1`, original 4b
then candidate sequentially, at most four workers. Report all value, phase,
scratch and failing-batch repairs/regressions. Require candidate failing
batches no greater than the original and expected failed batches per
9024-shot packet at most 18. There is no resampling or subset selection.
No cache composition, old arithmetic-mask transfer, search or submission
is authorized by the local theorem alone.
