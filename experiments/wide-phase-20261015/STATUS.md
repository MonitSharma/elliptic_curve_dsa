# Wider-circuit phase source

Completed 15 October 2026. Source observation only; **no qualified score**.

A gate-inert caller/backtrace observer identifies the native-verified witness
from the wider dynamic-pool circuit. The observer's stream matches its parent
byte for byte:
`95e771bae57bd96e75c11b569faf2f87cd7dfa52b227b40dd16e40a301d8e122`.

Measurement278924 at optimized operation3610757 corresponds to raw builder
operation3609779. Its Hmr acts on qubit221 with classical bit1566. The unique
matching trace points to `y15_onefold.rs:2770`, the division `body` routine's
`top1` branch (Y21 top cut), reached through `body_capped` and `fwd_tick`.

This branch measures m1 first, reconstructs the upper carry chain from a
truncated window, and measures m0. Its conditional correction combines the
reconstructed h1 and a windowed comparison `cmp0`, whose optional source-bit
seed comes from `cells::y15_split_spec`. Both the carry reconstruction and the
comparison need examination. The source trace does not establish which
approximation causes the counterexample, so removing a predictor alone is
not yet a justified repair.

Next capture the exact m0 value, reconstructed h1, transformed comparison
operands and seed under the verified measurement assignment. Validate any
observer against the protected simulator. Then derive and test a general
repair with its full width/Toffoli cost; do not tune the fixed packet.

PID3142012 exited0. The first launcher failed before executing a workload
because Windows line endings made Bash reject `pipefail`; its original
script and error log remain archived. The corrected launcher writes Unix
line endings. All35 artifacts, the source patch and external proof-runner
patch pass [local verification](local-verification.json).
[Receipt](evidence/receipt.json) · [Source attribution](analysis.json) ·
[Parent circuit and phase witness](../dynamic-pool-20261015/STATUS.md).
