# Scope of the exact transfer certificate

The existing qualified parent4 value-mask certificate is preserved. This
extension proves equality of the entire reachable state and physical RNG
transcript from that frozen circuit to the new nine-reduction circuit. It
does not assert that point addition never fails, and does not replace the
fresh paired failure-rate gate or the unchanged official benchmark.

For the first eight replacements, the copied source analysis assigns each
registered quantum and classical input an immutable atom before op zero.
Each quantum basis value, classical bit, and captured guard has an exact
Boolean table over at most seven atoms. A larger unsupported expression
becomes a fresh atom for the whole result. Correlations may be forgotten;
equalities valid for every assignment of these atoms remain sound. Copying
and updating a physical slot never reassigns the meaning of an old atom.
Every conditional classical write uses its original effective guard; an Hmr
outcome is fresh and the old bit is retained on the inactive branch. Push
stores a guard value, rather than a mutable bit reference. Resets set the
active branch to zero. Phase gates do not change these basis functions.

The audit serializes the pre-op tables at each actual rewrite without making
any additional abstraction queries. Replaying the instrumented pass gives the
same full stream as the frozen eight-factor pass. Independent Z3 encodings
prove, for every atom assignment, that the old guarded control product equals
the emitted classical-factor product. Complemented factors use the exact
identity y*(1-c)=y XOR y*c. Every emitted gate has the original target and
direct condition, and new scopes are balanced around that single operation.

For the ninth replacement, a separate prefix analysis begins with every
registered quantum input unknown. It records a classical expression for a
quantum wire only while that wire is provably a basis value determined by
classical inputs and MR outcomes. Unknown quantum-dependent operations remain
unknown; a known-zero product may safely keep a classical target known.
Unconditional reset permits a known zero. A mixed conditional swap loses both
classical tags, while a classically known swap uses exact conditional values.
Every MR variable has a unique physical event ordinal. Boolean cuts retain
their exact AND operands. The source-bound expression at the target gate is
q706=bit773 XOR bit774, with a true effective guard and empty scope stack.
Independent SMT replay proves the dirty-target identity for arbitrary values
of both classical bits, the other quantum control, and the target.

Equality of the basis permutation on every reachable basis assignment also
preserves coherent superpositions of those assignments. No replacement adds
a phase gate or changes phase. No classical bit is written by a replacement.
The full-stream edit audit verifies that every other operation is identical,
including every R/Hmr field and its original event order. Hence their random
words, outcomes, phase effects and all subsequent state updates can be coupled
exactly. This proves transfer for arbitrary classical inputs and MR words,
independently of any nonce-derived packet. Finite protected-simulator controls
and native byte reproduction corroborate this source-level certificate.

The new Fiat–Shamir stream is different. Its seed generation, compact runtime,
full-state/phase/physical-RNG execution, and value-mask implementation must be
qualified on that stream before authoritative rejection is ever enabled.
