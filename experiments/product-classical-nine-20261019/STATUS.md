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

## Live qualification checkpoint,19 October20:46 SGT

Native run1336448 exited0;175 source files and17 protected files checked.
Full raw SHA3 is4b81cbc1e247e791ab11ff56c5f84b4da5edc8618d7c19fe590305390fa6f93f;
compressed SHA25676271c7d66785b62ec4077ec241e80d3645841ba898cf8b633c377099da687c1.
The one final gate was declared at12:46:11 UTC with label
pareto-parent4-classical9-gate-20261019-v1,262144 batches/16777216 shots per
source, versus exact refreshed public9dc3798c stream. Manager1377879 runs
run-gate-v2.sh, two compute threads, streams sequentially, three reserved slots.
Consult gate-v2.exit and qualification/RESULT.json for the authoritative state.
Never restart this declared census or change its label/count/source.

The preceding shell launch1374176 died on CRLF before any declaration,
qualification directory or census shot existed. Its script/log/PID and the
zero-shot GATE-ADMISSION-FAILURE.json are preserved. This is a launcher repair,
not a rerun of a declared gate. The source and inherited nonce are unchanged.
No identity-tail nonce has been screened on this source and no official
benchmark has run. The pre-gate evidence archive intentionally excludes live
census rows; preserve final gate evidence separately when it is terminal.
