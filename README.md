# ECDSA Circuit Research

**Smaller quantum circuits for secp256k1 point addition. Three independent goals:
fewer logical qubits, fewer Toffolis, and a lower qubit × Toffoli product.**

**Current priority — 15 October 2026:** focus on lower executed Toffolis and
lower Q × T. Defer width-only optimization and Q692 submission engineering.
Preserve the width result; spend extra qubits when the gate savings justify it.

## Where we stand

**15 October 2026 — one new complete local benchmark result: 692 logical qubits.**
The original bank-swap v2 circuit passed all **9,024 shots**, with zero value,
phase or ancilla failures. The refreshed public minimum is now **680 qubits**;
our preserved local result is no longer below it. It is **not an official submission**, and we do not yet have a
submission-ready circuit or a qualified new Toffoli/product record.

The newer Q692 version that fits the normal build is a **different circuit**:
its full benchmark failed correctness. That failure does not invalidate the
preserved original pass, and the original pass does not qualify the new version.
[Current results and submission status](docs/results-status.md) ·
[Original passing result](experiments/followup-20261015/bankswap-terminal/RESULT.md) ·
[Independent verification](experiments/verification-20261015/independent-verification.json)

![Public Pareto frontier and our locally verified 692-qubit circuit](docs/figures/frontier.png)

The gold step is the **officially scored public frontier**. The cyan diamond is
our **separate local Q692 pass**. Leftward means fewer qubits; downward means fewer
Toffolis. The vertical axis is logarithmic. The original Q692 circuit saves width
at a substantial gate-cost increase. Failed and component-only experiments are
excluded from these performance figures.

## Three records, not one

| Objective | Public record | Our result | Next strict target |
|---|---:|---|---:|
| **Minimum logical qubits** | 680 | **692 — complete local pass**, not submitted | Width work deferred |
| **Minimum executed Toffolis** | 761,156 at Q1235 | No new qualified record | T ≤ 761,155 |
| **Minimum Q × T** | 939,347,948 at Q1234/T761,222 | No new qualified record | Q × T ≤ 939,347,947 |

These remain three distinct records, but **Toffoli count and product now take
priority in our research**. The challenge
promotes the scalar product, while its Pareto view also recognizes the low-qubit
and low-Toffoli extremes. A Toffoli record can use more qubits and have a worse
product. These are separate achievements.

![Why the low-Toffoli record and best product are different](docs/figures/record-tradeoffs.png)

At Q1235, **T761,155** would improve the Toffoli record, while **T760,605** or
less is needed to beat the product. At Q1234, the product threshold is
**T761,221**. These thresholds use the refreshed public score, not emitted gates.

Snapshot: **1,568 public submissions · 1,227 eligible scored records ·
48 public Pareto points**, analyzed 15 October 2026 at 16:55 Singapore.
[Full frontier and provenance](docs/frontier-results.md) ·
[Machine-readable records](docs/data/latest-leaderboard.json) ·
[Public API](https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74/submissions)

## Complete passing results

Only complete passing circuit evaluations appear in this table.

| Circuit | Peak Q | Rounded mean executed T | Q × T | Provenance |
|---|---:|---:|---:|---|
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
change gets a fresh test set. On **262,144 independent inputs**, the public B3
Toffoli record circuit has only about a **2–6×10⁻⁹ chance of passing a fresh test set**
(two independent censuses),
and the C5 product baseline about 1.5×10⁻⁸. B3's source pins a ground
`TAIL_NONCE`; its walk-width table states a deliberate drop budget of
0.00077 per walk; its recipe comments budget about 19 expected failed batches
per test set. These records pass because a lucky test set was searched for.
**We keep the no-nonce rule**, so our circuits must actually be correct.

![Fresh-input failure rate vs diagnostic Toffolis](experiments/failure-census-20261015/figures/honest-pass.png)

This is a diagnostic figure, **not scored results**. Each point is one
candidate stream, censused on fresh inputs with the unchanged protected
simulator. The benchmark requires zero failed batches. Every candidate built
so far, ours and the public baselines alike, sits two orders of magnitude above
the honest-pass zone. Our widest circuit is about 7.4K diagnostic Toffolis below
the record, and that margin is the budget for making it genuinely correct.
[Census](experiments/failure-census-20261015/STATUS.md) ·
[root-cause trace](experiments/trace-value-20261015/STATUS.md) ·
[walk widening](experiments/widen-walk-20261015/STATUS.md)

## What the recent experiments established

- **Honest correctness (new):** a one-minute failure census now gates every
  candidate. Exact, gate-inert tracing places 84% of the wide circuit's wrong
  outputs in the leapfrog GCD walk rails. Of those 155, 98 have a target rail
  off by exactly ±2^k, and 55 keep a correct target but corrupt the source rail
  (an independent audit corrected our first count). 31 failures show no
  walk-rail event and are not yet localized. Walk-only repairs have
  plateaued:
  - smoothing the tail-width cliff gives 7.2 → 5.8 expected failed batches per
    test set, for +37 Toffolis;
  - widening the rails *together with* their choice-window anchors by 2 bits
    gives 4.2, for +4.7K Toffolis;
  - +4 and +6 bits do no better: they recreate the tail cliff, and other
    stages degrade as rails widen;
  - convergence-aware (late-weighted, tapered) envelopes and a rebuilt tail
    descent remove the unconverged walks and halve walk failures. Non-walk
    failures then rise, so the total stays at about 3.8.

  A constant ~1.1 batches of non-walk failures remains in every variant. The
  benchmark needs under 0.1.
  [Census](experiments/failure-census-20261015/STATUS.md) ·
  [trace](experiments/trace-value-20261015/STATUS.md) ·
  [widening](experiments/widen-walk-20261015/STATUS.md) ·
  [guard sweep](experiments/guard-sweep-20261015/STATUS.md).
- **Width:** the original Q692 pass is preserved with its exact patch,
  stream hash, evaluator hash and score. Ordinary submission generation and
  arithmetic limits remain unresolved for that original version.
- **Submission engineering:** a later Q692 version builds within the tested
  memory budget, but its complete benchmark reports three value failures,
  two phase-failure batches and three ancilla-failure batches. Diagnosis is
  continuing on the same failed inputs.
- **Toffoli reduction:** exact caching rewrites reduce executed gates in paired
  tests. Larger symbolic expressions increase the wider design's saving to
  101.109375 executed Toffolis per shot on both fixed 256-shot packets at
  diagnostic Q1240. They retain inherited correctness failures and have no
  qualified score. [Latest cache evidence](experiments/cache-retention-20261015/STATUS.md).
- **Arithmetic repair:** the tick-104 borrow repair now integrates on B3 and
  fixes the known independent input's value and phase. Its native prototype
  passes 256 fixed independent inputs; other packet and structured failures
  remain. [Repair, local proof and limits](experiments/arithmetic-repair-20261015/REPORT.md).
- **Rail diagnosis:** fourteen of sixteen packet failures now have exact
  forward-rail counterexamples. A widened primitive passes 43,680 exhaustive
  signed cases, but repairing tick 109 exposes another overflow at tick 110;
  the complete candidate remains incorrect. [New evidence](experiments/rail-repair-20261015/REPORT.md).
- **Product:** the completed product-focused cycle produced no qualified
  improvement. Exact savings and unsuccessful width searches are preserved.

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

1. Make the wide lower-Toffoli circuit genuinely correct within its ~7.4K
   Toffoli margin. Keep the nearly free tail smoothing, trace and fix the
   mid-walk rail errors, then localize and repair the 31 failures with no walk-rail event. Gate
   each step with the census; the target is under 0.1 expected failed batches
   per fresh test set. Then retain the exact caching savings and measure the
   complete repaired design. A higher width is acceptable for a new Toffoli
   record.
2. Continue product work independently. Include the full cost of scratch,
   cleanup, phase correction and correctness repairs.
3. Evaluate final source with the unchanged benchmark, retain independent
   checks, verify ordinary packaging and compare with fresh public records.
4. Preserve existing Q692 evidence and failed experiments. Defer width-only
   searches and Q692 submission engineering while the two active objectives
   take priority.

Only `src/point_add/` may change in a contestant submission. We preserve the
harness, scorer, simulator, curve reference, dependencies and toolchain. We do
not search identity-tail nonces or tune hash-derived test packets.
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
