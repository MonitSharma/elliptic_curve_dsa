# ECDSA Circuit Research

**Smaller quantum circuits for secp256k1 point addition. Three independent goals:
fewer logical qubits, fewer Toffolis, and a lower qubit × Toffoli product.**

**Current priority — 15 October 2026 (night):** improve **Q × T first,
Toffolis second, qubits third**, through long unattended runs driven by
[docs/AUTONOMOUS_PROMPT.md](docs/AUTONOMOUS_PROMPT.md). Each objective stays
independent, and existing evidence, including the Q692 width result, is preserved.

## Where we stand

**16 October 2026, 09:19 Singapore — product final verification failed its
failure-rate gate.** PRODUCT25 passes the unchanged 9,024-shot benchmark at
Q1234/T761171 (product939285014), but the predeclared final fresh comparison
finds4,139 failing batches versus the parent's4,118 across2,097,152 shots each:
17.8100 versus17.7197 per9,024-shot packet. Both are below18, but our standard
also requires no worse than the parent. An independent complete raw recount
agrees. This candidate is **not eligible for submission under that standard**;
there is no resampling or new product-record claim. Other research remains
paused, and nothing was submitted during verification.
[Final verification evidence](experiments/product25-final-20261016/VERIFICATION.md).

**16 October 2026, 09:40 Singapore — next product candidate searching.** We
did not submit Product25. For future runs only, the failure-rate gate is now a
paired statistical test (`AGENTS.md`). PLAIN67 (the record circuit plus an
exact 67-stage cache, Q1234, −102 T per shot in paired fresh tests) passes it
on its pre-declared cohort. Its lowest-pass nonce search has been running
since 09:36, with about 21 h expected. There is no new score yet.
[PLAIN67 status](experiments/plain67-operational-20261016/STATUS.md).

**16 October 2026, 06:08 Singapore — official Toffoli record: 753,721
Toffolis at Q1468**, 50 below our previous public Toffoli record. The unchanged
benchmark passes all 9,024 shots with zero value, phase or ancilla failures.
Nonce 644 is the lowest pass from 1 (731 screened). The final paired census
passes at 5.77 failing batches per packet versus the parent's 5.80, across
1,048,576 fresh shots each. After a fresh unchanged benchmark reproduced the
same score and stream, it was **submitted at 05:19 Singapore** as
[`03be8e19`](https://api.ecdsa.fail/api/submissions/03be8e19-ab3b-45c7-9c62-9d78970c4d95).
Official evaluation confirms 753,721/Q1468, source `b5adb653`; rejection is
solely because its product does not improve. It is the independent Toffoli minimum.
[Upload receipt and fresh verification](experiments/wide15-record-20261016/submission-20261016/STATUS.md).
[Benchmark and source evidence](experiments/wide15-record-20261016/STATUS.md).
The earlier753,745/Q1464 complete pass is preserved as a lower-width alternative;
it no longer improves the current independent Toffoli minimum.

**Historical result, 15 October 2026, 19:19 Singapore — our previous publicly
scored Toffoli minimum: 753,771 at 1,464 qubits.** The official evaluation of
[`3f32acd2`](https://api.ecdsa.fail/api/submissions/3f32acd2-71bf-4cc7-bae6-7407be97fe3b)
matches our complete local benchmark and is 7,385 Toffolis below the previous
minimum of 761,156 (−0.97%). The service marks it **rejected solely because
its product did not improve the current best**; this is an officially scored
Toffoli minimum, with no product promotion. Official source: `5a7c3902`.

Its Q × T is **1,103,520,744**, 17.48% worse than the product leader. Fresh-input
tests still find **5.47 failed batches per 9,024-shot packet**, compared with
17.73 for the prior B3 Toffoli leader. We disclose nonce **375** (the lowest
passing nonce from 1; 593 screened) and retain the arithmetic limitations.
The complete scored packet passes; the circuit is not correct on every input.
[Official result, screen and census](experiments/nonce-screen-20261015/STATUS.md)

**Earlier on 15 October 2026 — one new complete local benchmark result: 692 logical qubits.**
The original bank-swap v2 circuit passed all **9,024 shots**, with zero value,
phase or ancilla failures. The refreshed public minimum is now **677 qubits**;
our preserved local result is no longer below it.
It is **not an official submission**.
Its width submission work remains deferred; the newer Toffoli candidate above is separate.

The newer Q692 version that fits the normal build is a **different circuit**:
its full benchmark failed correctness. That failure does not invalidate the
preserved original pass, and the original pass does not qualify the new version.
[Current results and submission status](docs/results-status.md) ·
[Original passing result](experiments/followup-20261015/bankswap-terminal/RESULT.md) ·
[Independent verification](experiments/verification-20261015/independent-verification.json)

![Public Pareto frontier with our official Toffoli minimum and local Q692 pass](docs/figures/frontier.png)

The gold step is the **officially scored public frontier**, including our
**cyan-star Toffoli entry**. The cyan diamond is our **separate local Q692 pass**.
Leftward means fewer qubits; downward means fewer
Toffolis. The vertical axis is logarithmic. The original Q692 circuit saves width
at a substantial gate-cost increase. Failed and component-only experiments are
excluded from these performance figures.

## Three records, not one

| Objective | Public record | Our result | Next strict target |
|---|---:|---|---:|
| **Minimum logical qubits** | 677 | **692 — complete local pass**, not submitted | Q ≤ 676 |
| **Minimum executed Toffolis** | **753,721 at Q1468 — ours** | **Officially scored**; score-only product rejection | T ≤ 753,720 |
| **Minimum Q × T** | 939,347,948 at Q1234/T761,222 | No new qualified record | Q × T ≤ 939,347,947 |

These remain three distinct records, with **product first, Toffolis second,
qubits third** in our research. The challenge
promotes the scalar product, while its Pareto view also recognizes the low-qubit
and low-Toffoli extremes. A Toffoli record can use more qubits and have a worse
product. These are separate achievements.

![Why the low-Toffoli record and best product are different](docs/figures/record-tradeoffs.png)

The next Toffoli target is **T ≤ 753,720**, at any allowed width. At our Q1468,
the strict product threshold is **T ≤ 639,882**. At Q1235 it is **T ≤ 760,605**;
at Q1234 it is **T ≤ 761,221**. These are independent objectives, using rounded
mean executed Toffolis rather than emitted gates.

Snapshot: **1,573 public submissions · 1,232 eligible scored records ·
52 public Pareto points**, analyzed 16 October 2026 at 06:08 Singapore.
The current width minimum is Q677 (jackylee0424, `18912d63`).
[Full frontier and provenance](docs/frontier-results.md) ·
[Machine-readable records](docs/data/latest-leaderboard.json) ·
[Public API](https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74/submissions)

## Complete passing results

Only complete passing circuit evaluations appear in this table.

| Circuit | Peak Q | Rounded mean executed T | Q × T | Provenance |
|---|---:|---:|---:|---|
| **Our fifteen-stage cache, nonce644** | **1,468** | **753,721** | **1,106,462,428** | [Unchanged9,024-shot benchmark](experiments/wide15-record-20261016/STATUS.md); officially scored as`03be8e19`, source `b5adb653`, stream`1d8c05ee`; final fresh census5.766 failures/packet |
| **Our four-stage cache, nonce92** | **1,464** | **753,745** | **1,103,482,680** | [Unchanged9,024-shot benchmark](experiments/wide-record-20261015/STATUS.md); complete local alternative, stream`ba9bd284`; final fresh census5.800 failures/packet |
| **Our wide smooth Leapfrog, nonce 375** | **1,464** | **753,771** | **1,103,520,744** | [Official evaluation `3f32acd2`](https://api.ecdsa.fail/api/submissions/3f32acd2-71bf-4cc7-bae6-7407be97fe3b), source `5a7c3902`; also complete local pass, stream `01aad987`; census 5.47 failed batches/packet |
| **Our original bank-swap v2** | **692** | **1,481,382,858** | **1,025,116,937,736** | [9,024-shot local pass](experiments/followup-20261015/bankswap-terminal/RESULT.md); streamed generation, unchanged protected evaluator |
| Public C5 reproduction | 1,234 | 761,658 | 939,885,972 | [Complete passing reproduction](docs/data/server-verification.json), source `c5bb1ec8` |
| Public B3 reproduction | 1,235 | 761,156 | 940,027,660 | [Complete passing reproduction](experiments/overnight-20261014/coordinator/b3-reference-full-receipt.json), source `b3c9fdd6` |

**The latter two reproduce other contributors' circuits; they are not our own
record improvements.** Each passed its complete benchmark packet. Independent
inputs also expose inherited arithmetic and phase failures in those baselines.
A finite passing benchmark is not a proof for every valid input.
[Counterexamples](experiments/overnight-20261014/product/b3-paired-results.md)

## Why the low-Toffoli records do not pass fresh tests

The benchmark derives its 9,024 test inputs from a hash of the circuit, so any
change gets a fresh test set. On **262,144 independent inputs**, the former B3
Toffoli leader has only about a **2–6×10⁻⁹ chance of passing a fresh test set**
(two independent censuses),
and the C5 product baseline about 1.5×10⁻⁸. B3's source pins a ground
`TAIL_NONCE`; its walk-width table states a deliberate drop budget of
0.00077 per walk; its recipe comments budget about 19 expected failed batches
per test set. These baselines use searched identity-tail nonces. The inherited
PR 419 contract caps the failure rate at 18 batches per
9,024 shots (the "PR 419" contract). **Since 15 October we follow a
disclosed-failure-rate standard.** We screen nonces only on frozen circuits whose
fresh-input failure rate is at or below that of the record they beat, and we
publish the nonce, the census and the number of nonces screened. Lowering the
failure rate remains valuable, because it makes the search cheap and the result
more honest.

Our officially scored circuit's fresh-pass probability is about **0.4%**; the
passing packet was selected under that disclosed policy. The independent census
and structured counterexamples remain relevant after official scoring.
Diagnostic count/failure plots stay in the experiment reports, separate from
the scored performance figures above.
[Census](experiments/failure-census-20261015/STATUS.md) ·
[root-cause trace](experiments/trace-value-20261015/STATUS.md) ·
[walk widening](experiments/widen-walk-20261015/STATUS.md)

## What the recent experiments established

- **Correctness diagnosis:** exact, gate-inert tracing localizes the saved
  failures outside the walk-rail events to payload-fold truncations and square
  merged windows. The previously unexplained floor now has known sources.
  Uniform precision widening is expensive; a selected one-bit product repair
  fails its fresh paired failure gate and triggers no nonce search. Cheap
  repair remains unresolved. Diagnostic counts and failed variants stay in
  the research reports.
  [Census](experiments/failure-census-20261015/STATUS.md) ·
  [trace](experiments/trace-value-20261015/STATUS.md) ·
  [widening](experiments/widen-walk-20261015/STATUS.md) ·
  [guard sweep](experiments/guard-sweep-20261015/STATUS.md) ·
  [completed localization](experiments/failure-floor-20261015/STATUS.md) ·
  [current-source repair](experiments/precision-repair-20261016/STATUS.md).
- **Width:** the original Q692 pass is preserved with its exact patch,
  stream hash, evaluator hash and score. Ordinary submission generation and
  arithmetic limits remain unresolved for that original version.
- **Submission engineering:** a later Q692 version builds within the tested
  memory budget, but its complete benchmark reports three value failures,
  two phase-failure batches and three ancilla-failure batches. Diagnosis is
  continuing on the same failed inputs.
- **Toffoli reduction:** the 753,721/Q1468 complete pass is now officially scored;
  the 753,745/Q1464 alternative is preserved. Product25 has an affordable
  certified search running; product67 has native, fresh, universal and disabled
  runtime qualification. Neither has a complete product benchmark result. Their
  diagnostic savings stay in the [current research report](experiments/product-exact-20261015/STATUS.md);
  the [older cache study](experiments/cache-retention-20261015/STATUS.md) uses a
  different baseline and does not establish the saving on our public source.
- **Arithmetic repair:** the tick-104 borrow repair now integrates on B3 and
  fixes the known independent input's value and phase. Its native prototype
  passes 256 fixed independent inputs; other packet and structured failures
  remain. [Repair, local proof and limits](experiments/arithmetic-repair-20261015/REPORT.md).
- **Rail diagnosis:** fourteen of sixteen packet failures now have exact
  forward-rail counterexamples. A widened primitive passes 43,680 exhaustive
  signed cases, but repairing tick 109 exposes another overflow at tick 110;
  the complete candidate remains incorrect. [New evidence](experiments/rail-repair-20261015/REPORT.md).
- **Historical exact-only search cost on public tip `4b2ec52f`:** the
  record circuit fails **17.69 batches per packet** on fresh inputs, and its
  fresh mean is 761,221.70 T, against a strict threshold below 761,221.5.
  Packet means vary by about 6 T. With our exact screener, a lowest-pass nonce
  search needs about 1.6×10⁸ nonces, about **58 days on 64 threads**. The
  width-free cache saves only **2.2 ± 1.2 T** on the tip. The product record
  was blocked under that exact-only cost model. The new certified prefilter
  gives a measured 19.609-hour mean projection at 48 threads on product25; this
  is an expectation, not a completion guarantee. The search is now active.
  [Current measured search](experiments/product25-operational-20261016/STATUS.md) ·
  [New mask-cost figure and assumptions](experiments/search-cost-mask-20261016/STATUS.md).
  [Measurements and search-cost figure](experiments/product-tip-20261015/STATUS.md).
- **Earlier product cycle:** no qualified improvement. Exact savings and
  unsuccessful width searches are preserved.

Detailed counts, test domains and failures:
[current results](docs/results-status.md) ·
[Toffoli experiments](experiments/toffoli-readiness-20261015/REPORT.md) ·
[product experiments](experiments/product-focus-20261015/REPORT.md) ·
[experiment archive](docs/experiment-outcomes.md).

## What we are building

The circuit performs **`P → P + A`** on secp256k1, with a quantum point `P`
and a classically supplied point `A`. It must compute the right coordinates,
clean temporary storage and preserve quantum phase. Correct classical output
alone is insufficient.

This is a building block of quantum elliptic-curve algorithms. We design and
simulate circuits on classical computers; this repository does not implement
a complete private-key recovery system.

**Q** is peak logical storage, not circuit depth or physical qubits.
**T** is rounded mean *executed* Toffolis, including conditional execution.
It is not the number of Toffolis written into the generated stream.

## Next work

1. **Finish a product record first.** The frozen product25 search is active.
   Preserve its source, ascending nonce ledger and disclosed fresh census;
   any pass must reproduce the unchanged full benchmark. Product67 is the
   stronger qualified alternative, with diagnostic savings documented in the
   [research report](experiments/product-exact-20261015/STATUS.md).
2. **Improve the official T753,721 record** (`03be8e19`, Q1468), aiming toward
   roughly 753,670. Extra qubits are acceptable for this independent objective.
   Keep failed fresh gates separate; do not resample them or count source
   proxies as complete results.
3. **Reduce failures cheaply on the current product source.** Attribute the
   remaining current 4b failures, qualify complete source-defined precision
   repairs, and prove fresh arithmetic-specific filters before combining them
   with exact caches. Earlier B3 witnesses are historical evidence.
4. Gate every frozen candidate with its predeclared fresh census and rate cap.
   Publish nonce, census and number screened. This run remains queue; separate
   user-authorized submissions are recorded explicitly.
5. **Width record:** the public minimum is Q677 (`d9d5e991`); the next target
   is Q676. Preserve the Q692 evidence and all failed experiments. Width is the
   third research priority, independent of the product and Toffoli records.

Only `src/point_add/` may change in a contestant submission. We preserve the
harness, scorer, simulator, curve reference, dependencies and toolchain. We
never tune circuit content to a packet; identity-tail nonces follow the
disclosed-failure-rate standard in `AGENTS.md`.
**Picking this up as an AI agent?** Start with
[docs/AGENT_HANDOFF.md](docs/AGENT_HANDOFF.md).
[Research plan](docs/research-plan.md) · [Server workflow](docs/SERVER_HANDOFF.md)

## Reproduce and explore

The figures are static PNGs for reliable GitHub rendering, with downloadable
[frontier SVG](docs/figures/frontier.svg) and
[record comparison SVG](docs/figures/record-tradeoffs.svg).
Their green-and-gold presentation is inspired by the challenge; all points use
this repository's dated evidence.

```bash
git submodule update --init --jobs 3
python -m pip install matplotlib
python scripts/test_leaderboard.py
python scripts/test_frontier_plot.py
python scripts/frontier_plot.py                         # offline, tracked data
python scripts/analyze-leaderboard.py --refresh --plot  # refresh public records
```

Use an isolated Python environment. Circuit builds use pinned Rust 1.93.0 and
locked dependencies. [Local setup](LOCAL_SETUP.md) documents the environment.
Research runs on `smu_server` under `/home/hclau/ecdsa_research`, with resource
preflights, dedicated logs and saved process IDs.

| Location | Contents |
|---|---|
| `agents/qubits/`, `agents/toffoli/`, `agents/product/` | Separate public source tracks and working research |
| `experiments/` | Exact patches, proofs, tests, failures and receipts |
| `docs/data/`, `docs/figures/` | Dated evidence, public records and figures |
| `scripts/` | Reproduction, analysis, plotting and validation tools |
| `research-output/` | Ignored raw snapshots and large artifacts |

A root Git commit does not preserve uncommitted submodule changes. Reapplicable
experiment patches are retained separately. Older evidence gaps are documented
in the [workspace recovery audit](docs/data/workspace-audit.json).

## Foundations and attribution

This project builds on the [ECDSA.fail challenge](https://ecdsa.fail/),
its [public source](https://github.com/Layr-Labs/ecdsafail-challenge), and the
circuits contributed by other researchers. Public reproductions are credited
to their source revisions; our modifications have separate patches and receipts.

Relevant methods include
[optimized point-addition circuits](https://arxiv.org/html/2606.02235v1),
[record-and-replay arithmetic](https://arxiv.org/html/2609.28882v1),
[space-efficient point addition](https://arxiv.org/html/2607.13816v2),
[temporary logical ANDs](https://arxiv.org/abs/1709.06648), and
[controlled add/subtract multiplication](https://arxiv.org/html/2410.00899v1).
See [NOTICE](NOTICE) and the [challenge terms](https://ecdsa.fail/terms) for
licensing and attribution.
