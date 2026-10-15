# Uniform Y15 seedless comparison experiment

Completed 15 October 2026. Both candidates are terminal and **neither qualifies
for a resource score**. The comparison change preserves all prior value-failure
sets, increases diagnostic executed Toffolis, and leaves phase counterexamples.

## Source change

Two isolated candidates inherit the narrow and wide dynamic-pool parents.
In `cells::y15_split_spec`, statistical source-bit seeds are removed uniformly.
The new window has width `max(refined_width, split - old_seed_position)`, so it
includes the former seed bit and preserves every previously compared bit.
Genuine retained carry wires are not removed by this function. The resulting
seedless comparisons remain truncated and approximate. Reconstructed carry
chains elsewhere in Y15 are unchanged.

Both candidates change only `src/point_add/`. The protected harness, scorer,
simulator, reference, Cargo files and toolchain match the B3 revision. The
fixed input packets and phase-audit tools are unchanged.

## Full fixed-input diagnostics

| Candidate | Family | Shots | Wrong values | Phase shots | Dirty batches |
|---|---|---:|---:|---:|---:|
| Narrow | Independent | 256 | 0 | 0 | 0 |
| Narrow | Structured | 256 | 128 | 122 | 0 |
| Narrow | Preserved candidate | 9024 | 5 | 4 | 0 |
| Wide | Independent | 256 | 0 | 0 | 0 |
| Wide | Structured | 256 | 128 | 127 | 0 |
| Wide | Preserved candidate | 9024 | 5 | 1 | 0 |

The five value failures remain indices562,720,2777,3447,8322. Structured
wrong values remain the128 zero-multiplicand cases (even packet indices);
all128 zero-slope point values pass. Phase remains a separate failure channel.

The wide parent's preserved-packet phase count was5, versus1 here. That change
is not an event-aligned comparison and does not establish monotone correctness
improvement. No identity tail, nonce, or hash-derived packet was selected or tuned.

Diagnostic peaks remain1282 and1464. On independent256, executed T totals are
197428259 (narrow) and193075492 (wide), increases of451.30859375 and485.44140625
per shot over their respective parents. These are diagnostic increases in
failed circuits, not scored Toffoli or product results. No candidate enters
the README performance plots.

## Remaining exact phase evidence

Each complete-stream BDD audit still finds a nonzero phase polynomial on the
first fixed zero-slope input. The protected native simulator verifies a
single-measurement counterexample with correct point values in each case:

- Narrow: measurement848289, operation10148844.
- Wide: measurement780824, operation9553940, Hmr qubit135 / bit1555,
  immediately following PopCondition and CX156→135.

Stream hashes:

- Narrow: `7fc4af20eba46456ccba4beec50b399599d485b6a25a117ba658f43dec13cc77`.
- Wide: `0e5b5f6f2640da7e50c6bb0ae788f093d4df7fedba811007b6a2894879dd6b3e`.

The selected witness moved later in each stream. This does not prove that
every earlier phase defect is absent. The audit covers one fixed input with
all measurement outcomes, not all possible point-addition inputs.

## Evidence and next action

PIDs3158520 (narrow) and3158521 (wide) exited0. All57 artifacts, two source
patches and the external proof-runner patch pass
[local verification](local-verification.json).
[Receipt](evidence/receipt.json) · [Diagnostic comparison](evidence/analysis.json).

Next attribute the wide witness to source and inspect its actual carry and
comparison predicates. Its local gate pattern suggests joint carry cleanup,
but source attribution is still required. The finite joint-carry model already
shows that its independently truncated carry reconstruction can fail even
after removing comparison seeds. Retain both parent candidates and this policy
variant until that cause is established. The five rail failures and the
zero-multiplicand contract remain independent work items.

The public refresh analyzed at12:58 Singapore reports1566 submissions,1225
eligible records and46 frontier points. Strict targets remain T≤761155 and
Q×T≤939347947; public minimum width is682. An unrelated failure-census process
was active during the resource preflight and was left untouched.
