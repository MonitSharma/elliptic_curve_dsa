# Guard-aware proofs of clean ancilla lifetimes

Prospective declaration, 19 October 2026, 16:50 Singapore, before any screen.
Parent: public 9dc3798c / 0c3a0751, compressed stream SHA256
99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683.
The frozen parent4 nonce search remains independent and unchanged.

Hypothesis: an ancilla initially zero, written only under captured condition F,
then reset under F is zero on every input after that reset, even when F is
unknown. The earlier reset-only allocator cannot release it; the bounded value
interpreter can lose F when arithmetic expressions grow. Tracking only the
conditions under which a wire can be nonzero avoids expanding its arithmetic.

Represent the nonzero support as a conservative DNF over immutable classical
Boolean-function IDs. Initial quantum register wires have support TRUE; other
wires have FALSE. X adds the effective guard; CX/CCX add that guard intersected
with control supports; resets remove support terms that imply their guard.
Conditional swaps combine old supports conservatively. Captured Push guards
retain their old function IDs when the underlying classical bit changes.
Classical operations use a canonical Boolean DAG, with fresh unknowns on any
deliberate complexity cut. DNF overflow becomes TRUE, losing proof power safely.
Fixed bounds: at most 16 terms and 32 factors per term; overflow never means zero.

After an emitted operation, a logical role whose support is FALSE may release
its physical lane. Every original operation, R/Hmr event and Toffoli is retained;
only quantum wire labels and final output-restoring swaps change. Reset RNG is
consumed even on zero targets or behind false guards. The inherited 96-op XX
identity tail is validated, detached before rewriting, then appended after
output restoration so future frozen-nonce tools can still bind the tail.

Required controls: exhaustive Boolean-constructor truth tables; support-rule
soundness under arbitrary basis/control/guard assignments; nested and mutated
captured guards; conditional reset/reuse and inactive measurement RNG; capped
support fallbacks; independent protected-simulator transcripts. A positive
width result needs native reproduction, a new predeclared statistical gate,
frozen ascending nonce search, and unchanged benchmark before any record claim.

Plan: one build job using an existing research dependency cache, one screen
core, up to32GiB after fresh memory/process checks. No server job is launched
for this experiment yet. This smaller proof method precedes the more complex
materialized-guard scheduling proposal.
