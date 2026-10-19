# Carry research: unresolved integration directions

These are source-level hypotheses, not new resource results or final gates.
Keep every original failed generation, source freeze and statistical verdict.

The direct-source plain and paused primitives have native controls. A plain
borrowed MAJ/UMA saves one clean carry per additional CCX. In a paused ladder,
the borrowed MAJ also changes its incoming carry wire. Only views whose
following stage is ordinary (plus the terminal carry) are valid at the pause.
The tested paused API hides the invalid views. A consumer must honor its
declared source/target read set and restore all data/carries it touches.

Lowering the global planner cap from1234 to1233 replans many original chunks
and adds about700 static-expected raw Toffolis. That is already around the
617-Toffoli budget per qubit, before full measured optimization. An alternative
worth testing is to preserve the1234 planner and impose a separate hard1233
carry limit with exact source borrowing. Original source-site audit predicts
123 extra borrowed stages for plain ladders at this hard limit, substantially
less than replanning. Paused ladders and Y15/square peaks must also be handled;
this is not yet a complete source or a proven lower global width.

The first remaining peak after plain-only borrowing is a YP8 paused add plus
its comparison. Its forward consumer temporarily writes every target sum via
`flip`, although yp8_logic reads only low bits, signs and its fixed W1 windows.
A possible exact change is to flip only a proved conservative read set, borrow
outside that target set and outside the original source read set, then use the
tested paused API. The reverse consumer only reads that same subset and the
terminal carry. All generated yp8_logic operations should be audited against
the declared read set; a guessed mask is not adequate. Global source sign-XORs
around the consumer temporarily affect borrowed carry pivots and must cancel
before any exposed carry is read again. Do not transplant the primitive into
the existing callback without this proof and complete paired raw validation.

Y15's fixed-storage bottleneck is independent. The new seven-carry schedule
is native-tested but a five-drop allowance saves three ladder-budget wires,
not five. Its allocation accounting must include reverse regeneration and
both exact phase compares. Native actual component peaks were8/7, static
emitted CCX113/130. Existing nonadjacent-drop code cannot simply accept adjacent
drops; the invalid-adjacent control correctly panics. More aggressive pebbling
requires a new proof and implementation, not an assertion change.

Square borrowing must preserve copy requests, deferred phases, known output,
known carry and retained-boundary contracts. The current modular adapter
deliberately excludes all such calls. A configured cap is never a measured
width: plan7 at configured1233 generated actual1237 in square; the first square
adapter reduced that to actual1234, exposing a separate plain modular ripple.
