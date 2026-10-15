# Generic free-borrow audit: terminal diagnostic

This experiment audits source-defined comparator families after the frozen
front-seam candidate's independent gate completed. It creates no circuit
candidate, modifies no frozen source, and performs no nonce search/submission.

The gate-inert observer replays the frozen public4b raw builder stream exactly:
SHA256 `ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69`.
It exposes complete operand arrays at all 2,093 ordinary chunk comparators and
512 TOP1 comparator calls in the instrumented source routes. Every call is
included, independently of witness failures, ticks, or any official packet.

Of these, 1,956 ordinary and all 512 TOP1 calls have a predictor equal to the
next lower source wire b[lo-1]. At all these sites the next two source wires
and lower accumulator are distinct physical wires. Retaining this predictor
and adding its position is redundant: MAJ(!a,b,b)=b. It does not increase
precision. Moving to a new lower predictor generically requires a nonlinear
carry operation. No free extension is admitted from this structural identity.

A conservative exact-affine-or-unknown replay of the entire raw prefix checks
up to four lower operand positions at every call. All 9,872 lower source and
9,872 accumulator queries are UNKNOWN; none is certified constant or a copy of
an immutable classical input. UNKNOWN is not a proof that hidden nonlinear
identities do not exist. This raw-source diagnostic also does not account for
inherited post-builder edits and cannot justify a final-stream replacement.

The source inventory finds one front classical seam (raw HMR63593), one T6
quantum seam (5892145), and two back classical seams (5392157,11255695). Back
seams compare against a source-derived classical c3 or immutable ox word.
They are plausible zero-Toffoli extensions, but remain unimplemented. Required
obligations include complete actual-final region binding, guarded scratch-zero
entry, untouched high arithmetic interface through inherited low-fold edits,
and all-input/MR local phase and quantum/classical interface proofs. In the
multiply back seam add=ox+1 and comparator=ox, so its arithmetic derivation
must preserve that distinction rather than blindly reuse the front proof.

No ordinary/TOP1 zero-cost family was justified by this audit. The initial
Rust Option parser failure and the first wrapper's invalid exit marker are
preserved; the corrected single-thread audit exits zero and its summary is
independently asserted. The observer uses at most four build threads and one
runtime thread; unrelated server processes and other agents' files are intact.
