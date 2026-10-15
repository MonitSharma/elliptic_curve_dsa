The family is every public4b `merged::flag_erase` call: ten source width16
and two source width18. Selection uses the function and source widths/costs,
with no input, nonce, measurement witness, or failure-tick selection. The four
joint-lowfold width13/14 calls were rejected before candidate construction:
they erase real inserted midpoint carries exactly and have no supported
source-bit precision repair.

Write the actual unsigned comparator words as A (target) and B (source),
and let lo=256-k. The old k-bit comparator starts with the source-bit
predictor B[lo-1]. The new predictor is

    c = MAJ(!A[lo-1], B[lo-1], B[lo-2])
      = B[lo-2] XOR ((!A[lo-1] XOR B[lo-2])
                    AND (B[lo-1] XOR B[lo-2])).

Using c in the unchanged high-k ladder computes exactly the k+1-bit
complement/add carry with predictor B[lo-2]. This is a source-defined extra
precision bit. A source-bit predictor is approximate: there is no claim
that the new predicate is pointwise monotone, is the ideal whole-word
overflow, or makes point addition globally correct. The inherited
approximation remains disclosed and the sole fresh gate decides usefulness.

After the original overflow HMR, under its original outcome m and enclosing
scope snapshot, the now-cleared overflow wire stores c. Clifford affine
conjugations and one CCX compute it while restoring all three lower data
wires. The old comparator's four seed occurrences use this borrowed wire;
the comparator restores that wire and all operands. A new HMR with fresh
independent outcome r clears c. Its phase is r*c. Under the unchanged outer
guard and r, the five Clifford terms

    Z(B_low), Z(S), CZ(A_low,B_low), CZ(A_low,S), CZ(B_low,S)

add exactly r*MAJ(!A_low,B_low,S), cancelling the new measurement phase for
every input and every new outcome. S is B[lo-2]. There is no new qubit, one
new physical MR per site (including inactive guards), and one guarded CCX.
The exact source-bound classical snapshot replay gives mean added T=6 over
the complete12-site family. Generated/static counts are not scored results.

All12 old complete HMR/Push/comparator/Pop intervals are uniquely
byte-identical in the final inherited-table stream. The full operand arrays
and source-bit rules are logged by a gate-inert observer reproducing raw
SHA256 ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69.
Conservative whole-original-prefix propagation proves every allocated
comparator carry scratch zero for arbitrary ABI inputs and all MR. The
candidate repeats these zero and complete-region checks at native build.

Each old and new local helper has an exact symbolic MR polynomial, with
arbitrary operand and classical entry bits. An independent BDD checks all
input-coefficient identities. All24 proofs have zero caps, all quantum
outputs restored/cleared, and exact phase

    m * (entry_overflow XOR old_or_new_carry_predicate).

Every internal MR is independently quantified. Inactive enclosing scopes
leave all quantum/classical state unchanged in either helper; every MR draw
is still consumed. Each helper also passes4096 protected bitplane cases,
and all12 deliberately wrong cleanup-CZ controls are rejected. Six native
admission tests pass. The first proof driver incorrectly expected n rather
than the actual2n-1 physical MR draws in an original comparator; that count
assertion failure is preserved, corrected before native candidate generation,
and the semantic theorem/source/selection were unchanged.

Delete only the eight added compute rows and eight cleanup rows, then
replace the four borrowed controls by the old seed: the exact original
operation sequence is recovered. The new classical bit45701 is above every
original physical bit. Under the deterministic original-MR ordinal mapping
(skip each new cleanup draw), every original HMR outcome, old bit operation,
condition and Push snapshot is therefore identical. Together with the local
quantum restoration theorem, this composes through the whole circuit and
preserves coordinate values for every original input/MR assignment. Phase
changes only by the explicitly proved old/new predicate difference. This
does not assert old/new equality for an unmapped, shifted physical RNG tape.

No original Clifford-feedforward omission is diagnosed. Existing primitive
phase cleanup was already exact for its approximate predicate. This candidate
changes that predicate using one additional source bit; it does not suppress
phase checks or erase observed failures.
