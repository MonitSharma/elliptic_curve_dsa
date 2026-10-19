# Parent4 plus nine exact classical reductions — not a score

Declared 19 October 2026 before this candidate's implementation and tests.
The completed source-only expression probe proves that, immediately before
CCX(706,816;703) at op5387927 of the eight-factor stream, q706 equals the
XOR of the live classical bits773 and774. The effective guard is true and
the captured-scope depth is zero. The proof treats every registered quantum
input as unknown quantum data and every MR outcome as an independent variable.
No sampled packet or nonce is used to choose this rewrite.

Replace the one CCX with two CX(816;703), conditioned respectively on bits773
and774. This removes exactly one executed Toffoli on every shot, with no
new bits, qubits, measurements or resets. Every other operation is unchanged.
The production pass requires the exact pre-tail source length, full SHA3
and gate fields. The inherited identity tail remains unchanged.

Run exhaustive dirty-target/value/phase primitive controls, source-binding
negative tests, 512 full raw-input state/phase/classical/RNG transcript controls
against the eight-factor stream, and native reproduction in a fresh detached
worktree. All 17 protected files must remain unchanged. This is a prototype;
no statistical gate is declared and no nonce or official benchmark is run yet.
Use one build/compute core and a32GiB cap while the old frozen search runs.

## Completed evidence checkpoint

Native byte-identical parent4+simple8+one unconditional classical-XOR reduction. Four primitive/source-binding controls and512 full transcripts pass;17 protected files unchanged. Statistical qualification is separate; consult qualification/RESULT.json if present. No resource record claimed.
