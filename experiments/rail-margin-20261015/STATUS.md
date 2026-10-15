# Rail headroom: terminal partial repair

**Both variants are terminal. No qualified resource score.** The version with
more scratch space builds, passes all 256 independent inputs, and reduces wrong
values on the preserved 9,024-input packet from 16 to 10. The source remains
incorrect and is not ready for an official benchmark or submission.

| Fixed input family | Shots | Wrong values | Shots with nonzero phase | Dirty batches |
|---|---:|---:|---:|---:|
| Known earlier counterexamples | 15 | 11 | 7 | 0 |
| Independent | 256 | 0 | 0 | 0 |
| Structured | 256 | 189 | 123 | 0 |
| Preserved old candidate packet | 9,024 | 10 | 10 | 0 |

The new circuit's diagnostic width is 1267. No Toffoli mean or product is
promoted to a resource record. Both interior headroom and planner allowance
changed, so a scratch-only control is needed before assigning the improvement
to either change. Measurements across the arithmetic variants are not aligned;
these correctness counts are not a paired phase or gate saving.

All 38 archived artifacts and both source patches are verified locally.
Both checkouts' protected files match B3. The successful stream SHA256 is
`41640cec0a64c19b31d9dccd180bc311465b17fea9d33a536af63dd6ed94ae68`.
[Terminal receipt](evidence/receipt.json) · [Archive](evidence.tar.gz) ·
[Successful variant patch](evidence/margin-room-b3/source.patch).

## Preserved launch and construction history

The first variant is terminal: PID 3079263 exited 101 after compilation.
Circuit construction stopped at forward tick 128 because the existing payload
planner lacked scratch space (fold room 16, need 39). No stream or resource
score was produced. Source, patch and failed log remain preserved.

**Continuation launched at 11:10 Singapore, now exit 0:** PID 3081279, `run-room.sh`,
isolated checkout `margin-room-b3`, planner allowance 1267. It widens only
interior ticks 2..136; the first two rows and last row stay unchanged because
the seed seam and parked-rail routines require fixed widths. This variant is
still a diagnostic, not a claimed performance result. Both variants live in
`/home/hclau/ecdsa_research/rail-margin-20261015/`.

The preceding single-site repair fixed a tick-109 overflow but exposed an
overflow at tick 110. The first experiment increased every fitted rail-table width
by one, capped at 258, uniformly across all 138 ticks. Both variants keep the finite
tick-104 fold repair and the supported dynamic allocator; old-stream optional
optimization tables remain unused. The rule is fixed independently of test
inputs. This is a correctness diagnosis, not a width-only optimization.

Only the isolated checkout's `src/point_add/` changes. Protected-file equality
and the exact patch are recorded before building. Tests reuse the known fifteen
counterexamples and the unchanged independent, structured and old candidate
packets. The latter is a frozen failing packet, not a fresh score. The fifteen
counterexamples have a partial simulator batch, so its raw gate total must not
be interpreted as a mean. Measurement events across arithmetic rewrites are
unaligned; count and phase deltas are not paired cache savings.

Four build threads, one library thread, a 16 GiB process limit, dedicated logs
and a recorded PID bound resource use. No nonce search, packet tuning or
official benchmark is part of this diagnostic. Even a finite correctness
improvement must be costed and independently checked before qualification.
