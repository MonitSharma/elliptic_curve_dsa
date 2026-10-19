# ECDSA.fail · Pareto-leading circuit research

## New local benchmark · 20 October 2026, 02:11 SGT

The complete unchanged benchmark passes at **1,234 qubits ×
761,077 rounded mean executed Toffolis =
939,169,018**, improving the freshly verified public product by
**23,446 (0.00250%)**.
All 9,024 shots pass. This is a **local reproduction, queued for review**;
it has not been uploaded or officially evaluated. The frozen circuit passed
its independent failure-rate gate; lowest passing nonce 7,614,812 after full
accounting of 7,811,072 production nonces. Inherited approximate arithmetic
remains, so finite-packet success is not a universal correctness claim.

[Source, statistical census and complete nonce accounting](experiments/classical12-final-20261020/SUBMISSION-NOTE.md) ·
[Independent local verification](experiments/classical12-final-20261020/LOCAL-FINAL-VERIFICATION.json) ·
[Complete evidence bundle](experiments/classical12-final-20261020/final-evidence.tar.gz)

**MonitSharma holds the lowest qubit–Toffoli product and the lowest Toffoli count
on [ECDSA.fail](https://ecdsa.fail/), with four points on the current Pareto frontier.**
This repository contains secp256k1 point-addition research, three optimization
tracks, and reproducible public leaderboard analysis.

## Public results · 17 October 2026

Verified against the website and official API. Snapshot retrieved at **12:36
Singapore time**: 1,584 submissions, 1,241 eligible officially scored results,
and **45 nondominated resource pairs**. Each objective below has its own circuit.

| Objective | Qubits | Rounded mean Toffolis | Product | Solver / official submission |
|---|---:|---:|---:|---|
| **Lowest product** | **1,234** | **761,121** | **939,223,314** | **MonitSharma** · [d7f69382](https://api.ecdsa.fail/api/submissions/d7f69382-4716-4b86-9fac-151c8bc581e4) |
| **Fewest Toffolis** | 1,556 | **753,694** | 1,172,747,864 | **MonitSharma** · [b99c9678](https://api.ecdsa.fail/api/submissions/b99c9678-5a68-49e8-a8b7-91fc6c383e37) |
| Fewest qubits | **676** | 490,149,075 | 331,340,774,700 | bulengerk · [42ae2103](https://api.ecdsa.fail/api/submissions/42ae2103-575e-4f95-bbd5-ab2051a994f2) |

The product record improves on jackylee0424’s preceding **939,347,948** by
**124,634 (0.01327%)**, saving 101 rounded Toffolis at the same width. The new
Toffoli record improves on our previous **753,721** by **27 gates (0.00358%)**.
Our Q1464/T753771 and Q1468/T753721 entries also remain nondominated.

![ECDSA.fail resource frontier, highlighting MonitSharma’s four Pareto points](docs/figures/leaderboard-frontier.png)

The API promotes the scalar product. Our product entry is **accepted and promoted**;
the three wider gate-saving entries are officially scored but rejected only because
their product did not improve the incumbent. They are included in the website’s
Pareto view and in this analysis. Pareto membership describes a resource tradeoff;
it does not mean one circuit wins every objective.

![Product record history, with the latest eight records enlarged](docs/figures/product-progress.png)

The full challenge has reduced product **91.27%** from its starting baseline;
that cumulative gain includes many contributors. The product submission adds an
exact repeated-AND cache to jackylee0424’s `4b2ec52f` lineage. The submissions
retain inherited approximate arithmetic and disclose finite-packet testing,
fresh-input failure measurements, and identity-tail nonce searches. Read the
[results, source revisions and attribution](docs/leaderboard-results.md) for scope.

[Full frontier table](docs/frontier-results.md) ·
[Frontier SVG](docs/figures/leaderboard-frontier.svg) ·
[Product-history SVG](docs/figures/product-progress.svg) ·
[Saved source data](docs/data/leaderboard/README.md)

## Reproduce the updated plots

The headline figures use the complete hashed 17 October public snapshot and
regenerate offline, with no ignored research folder required:

```bash
python scripts/plot-leaderboard-records.py
python scripts/plot-leaderboard-records.py --refresh # fetch a newer public snapshot
```

This creates high-resolution PNG and editable SVG files in `docs/figures/`.
It checks snapshot hashes, Q × T consistency and benchmark metadata before
plotting. [Saved data and method](docs/data/leaderboard/README.md).
The existing research analyzer and its tests remain available separately.

## How the benchmark works, and the standard we hold ourselves to

The official evaluator simulates the circuit on **9,024 test inputs derived
from a hash of the circuit itself** and requires every one to produce the
right point, a clean workspace and no stray phase. Change anything, even an
identity gate, and the test set changes.

Every current record circuit, ours and others', uses approximate arithmetic
that fails on a small fraction of inputs. They pass the scored test because
an identity-only "nonce" at the end of the circuit was searched until the
derived test set happened to pass. The community caps this at 18 expected
failing 64-shot batches per 9,024-shot test set.

We disclose this openly and hold our entries to a stricter, pre-declared
standard ([AGENTS.md](AGENTS.md)):

1. **Freeze first.** The circuit is finished before any nonce is searched.
   Nothing about the circuit is tuned to a test set, and no gates are removed
   in ways that trade correctness for score.
2. **Measure the failure rate on fresh inputs.** Run at least 2 million
   independent shots, paired with the record being beaten on identical
   inputs. The candidate must have no more wrong-answer failures, must not be
   statistically worse (one-sided exact McNemar test, 5% level), must stay at
   or below 18 failing batches per test set, and must leave no dirty
   workspace. The test plan is fixed in writing before it runs, and a failed
   check is final: no reruns.
3. **Search transparently.** Try nonces in ascending order from 1, take the
   lowest one that passes, and never pick by score.
4. **Publish everything.** The nonce, the number screened, the fresh-input
   census, and the unchanged official benchmark run on the final source.

For example, our 753,721 entry fails 5.77 batches per test set on fresh
inputs, about a third of the 17.7 measured for the baseline it improved on.
We also reject our own near-misses: a product candidate that beat the record
by 62,934 on the official benchmark was **not submitted**, because its
pre-declared failure-rate check came out marginally worse than the record's
([verification](experiments/product25-final-20261016/VERIFICATION.md)).

## Current work

- **Product record (officially accepted and promoted).** PLAIN67 scores
  **761,121 × 1,234 = 939,223,314**, official submission
  [d7f69382](https://api.ecdsa.fail/api/submissions/d7f69382-4716-4b86-9fac-151c8bc581e4).
  [Research evidence](experiments/plain67-final-20261016/STATUS.md) ·
  [submission note](experiments/plain67-final-20261016/SUBMISSION-NOTE.md).
- **Toffoli record (officially scored, Pareto-optimal).** WIDE95 scores
  **753,694** at **1,556 qubits**, official submission
  [b99c9678](https://api.ecdsa.fail/api/submissions/b99c9678-5a68-49e8-a8b7-91fc6c383e37).
  [Research evidence](experiments/wide95-20261017/STATUS.md).
- **Further product research.** Later cache continuations and their frozen
  experiments remain separate from the official records above. See the
  [agent handoff](docs/AGENT_HANDOFF.md) and dated experiment statuses for
  current research; pending counts are excluded from these result plots.
- **Qubit record.** The public frontier is at 676 qubits, built on a different
  ring-based design than our complete local 692-qubit pass.

## What we have learned

- **Where circuits fail.** Gate-inert tracing places most wrong outputs in the
  bounded-width rails of the modular-inversion walk ("leapfrog" GCD). The rest
  come from truncated folds and merged squaring windows. Widening rails helps
  only up to about 2 bits.
  [Census](experiments/failure-census-20261015/STATUS.md) ·
  [trace](experiments/trace-value-20261015/STATUS.md) ·
  [walk widening](experiments/widen-walk-20261015/STATUS.md)
- **Search cost grows exponentially with the failure rate.** At the product
  record's 17.7 failing batches per test set, an exact gate-level screener
  would need about 58 days on 64 threads. A certified classical prefilter,
  which rejects nonces using proven wrong output bits, makes it about a day.
  This is why lowering failure rates matters as much as saving gates.
  [Measurements and figure](experiments/product-tip-20261015/STATUS.md)
- **Width and gates trade off sharply.** Our 692-qubit circuit passes the full
  benchmark but needs about 1.48 billion Toffolis.
  [Result](experiments/followup-20261015/bankswap-terminal/RESULT.md)

The complete, dated history, including every negative result, is in
[docs/research-plan.md](docs/research-plan.md),
[docs/results-status.md](docs/results-status.md) and
[docs/experiment-outcomes.md](docs/experiment-outcomes.md).

## Complete passing results

Only circuits that passed the complete 9,024-shot benchmark appear here.

| Circuit | Qubits | Rounded mean executed Toffolis | Q × T | Status |
|---|---:|---:|---:|---|
| Wide circuit + 15-stage cache | 1,468 | **753,721** | 1,106,462,428 | Official [`03be8e19`](https://api.ecdsa.fail/api/submissions/03be8e19-ab3b-45c7-9c62-9d78970c4d95) (previous Toffoli record) |
| WIDE95 Toffoli candidate | 1,556 | **753,694** | 1,172,747,864 | Official [b99c9678](https://api.ecdsa.fail/api/submissions/b99c9678-5a68-49e8-a8b7-91fc6c383e37), current Toffoli record; [evidence](experiments/wide95-20261017/STATUS.md) |
| PLAIN67 product candidate | 1,234 | 761,121 | **939,223,314** | Official [d7f69382](https://api.ecdsa.fail/api/submissions/d7f69382-4716-4b86-9fac-151c8bc581e4), current product record; [evidence](experiments/plain67-final-20261016/STATUS.md) |
| Wide circuit + 4-stage cache | 1,464 | 753,745 | 1,103,482,680 | Local pass, [evidence](experiments/wide-record-20261015/STATUS.md) |
| Wide smoothed-walk circuit | 1,464 | 753,771 | 1,103,520,744 | Official [`3f32acd2`](https://api.ecdsa.fail/api/submissions/3f32acd2-71bf-4cc7-bae6-7407be97fe3b) (previous record) |
| Product25 (not submitted) | 1,234 | 761,171 | 939,285,014 | Local pass; failed its own failure-rate check, [verification](experiments/product25-final-20261016/VERIFICATION.md) |
| Bank-swap circuit | 692 | 1,481,382,858 | 1,025,116,937,736 | Local pass, [evidence](experiments/followup-20261015/bankswap-terminal/RESULT.md) |
| Public B3 (reproduction) | 1,235 | 761,156 | 940,027,660 | Others' circuit, [receipt](experiments/overnight-20261014/coordinator/b3-reference-full-receipt.json) |
| Public C5 (reproduction) | 1,234 | 761,658 | 939,885,972 | Others' circuit, [receipt](docs/data/server-verification.json) |

A passing 9,024-shot benchmark is not a proof of correctness on every input;
fresh-input failure rates are reported with each entry.

## Repository layout

| Location | Contents |
|---|---|
| `experiments/<name>-<date>/` | One folder per experiment: `STATUS.md` (result first), scripts, patches, hashes, logs and receipts |
| `docs/` | Results, research plan, public frontier snapshots, figures and the agent handoff guide |
| `scripts/` | Leaderboard analysis, plotting, audits and helpers |
| `agents/{toffoli,product,qubits}` | Git submodules pinned to public challenge commits that served as baselines |
| `src/`, `Cargo.*`, `benchmark.sh` | The challenge harness (simulator, evaluator, benchmark script) used for local scoring |

Submissions change only `src/point_add/` inside a challenge checkout.
Experiment archives larger than 5 MB are not in Git; they are listed with their
SHA-256 in [experiments/LARGE-FILES-MANIFEST-20261016.json](experiments/LARGE-FILES-MANIFEST-20261016.json).

## Reproduce

```bash
git clone --recurse-submodules https://github.com/MonitSharma/elliptic_curve_dsa.git
cd elliptic_curve_dsa
python -m pip install matplotlib
python scripts/test_leaderboard.py
python scripts/test_frontier_plot.py
python scripts/analyze-leaderboard.py --refresh --plot   # refresh public records and figures
```

To re-score a circuit, apply its experiment's `src/point_add` patch to the
named public challenge commit and run the challenge's unchanged
`./benchmark.sh` (Rust 1.93.0, locked dependencies). Each experiment's
`STATUS.md` names the base commit, patch, expected stream hash and score.
Heavy runs used a 144-core Linux server; [LOCAL_SETUP.md](LOCAL_SETUP.md)
covers a workstation setup.

Much of this research was carried out by AI coding agents (Claude and GPT
models) under human direction. [docs/AGENT_HANDOFF.md](docs/AGENT_HANDOFF.md)
and [docs/AUTONOMOUS_PROMPT.md](docs/AUTONOMOUS_PROMPT.md) document how they
are run and how a new agent can continue the work.

## Responsible use

This is resource-estimation research on a public benchmark. Everything here
runs on classical simulators of small, fixed circuits. Nothing in this
repository can recover a private key, and none of it threatens any real
cryptographic system with today's hardware. Results like these help the
community judge how far away such attacks are and plan the move to
post-quantum cryptography. The repository contains no credentials, and none
are needed to reproduce the results.

## License

Original contributions by Monit Sharma are licensed under the
[MIT License](LICENSE). Third-party code, dependencies and submodules retain
their respective licenses. In particular, the reused simulator and curve files
listed in [NOTICE](NOTICE) remain under CC BY 4.0.

## Attribution

This work builds on the [ECDSA.fail challenge](https://ecdsa.fail/) and its
[public source](https://github.com/Layr-Labs/ecdsafail-challenge). It also
builds on the circuits other participants published there, especially the
Leapfrog line by jackylee0424, krishparadox and kaankolcu, credited by
revision in each experiment.

The simulator and curve files are reused under CC BY 4.0 from
[zkp_ecc](https://github.com/tanujkhattar/zkp_ecc); see [NOTICE](NOTICE) and
the [challenge terms](https://ecdsa.fail/terms).

Related methods:
[optimized point-addition circuits](https://arxiv.org/html/2606.02235v1),
[record-and-replay arithmetic](https://arxiv.org/html/2609.28882v1),
[space-efficient point addition](https://arxiv.org/html/2607.13816v2),
[temporary logical ANDs](https://arxiv.org/abs/1709.06648),
[controlled add/subtract multiplication](https://arxiv.org/html/2410.00899v1).
