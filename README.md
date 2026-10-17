# ECDSA Circuit Research

**Smaller quantum circuits for secp256k1 elliptic-curve point addition, built
and verified for the public [ECDSA.fail](https://ecdsa.fail/) resource
challenge.**

The challenge scores a reversible circuit that adds a classical point to a
quantum point on Bitcoin's curve, the core subroutine of Shor's algorithm for
elliptic curves. Each entry is scored on three independent resource records:
**fewest logical qubits**, **fewest executed Toffoli gates**, and **lowest
qubit × Toffoli product**. This repository holds our circuits, the tools we
built to verify them, and a dated, reproducible record of every experiment,
including failed ones.

## Results at a glance

| Record | Public best (16 Oct 2026) | Our standing |
|---|---:|---|
| **Fewest executed Toffolis** | **753,721** at 1,468 qubits | **Ours**: officially scored submission [`03be8e19`](https://api.ecdsa.fail/api/submissions/03be8e19-ab3b-45c7-9c62-9d78970c4d95); new local pass **753,694** at 1,556 qubits queued |
| Lowest qubit × Toffoli product | 939,347,948 (761,222 × 1,234) | **939,223,314** (761,121 × 1,234): complete local benchmark pass, queued for submission; see [current work](#current-work) |
| Fewest logical qubits | 676 | A complete local pass at 692 qubits (not submitted) |

![Public Pareto frontier with our officially scored Toffoli record](docs/figures/frontier.png)

The gold step is the officially scored public frontier; leftward means fewer
qubits, downward fewer Toffolis (log scale). The cyan star is our official
Toffoli record. The cyan diamond is a separate 692-qubit circuit that passed
the full local benchmark. Only official scores and complete local benchmark
passes appear in this figure.

### Our Toffoli record

Our circuit lowered the public minimum from **761,156** to **753,771** executed
Toffolis (submission `3f32acd2`, 15 Oct), then to **753,721** (`03be8e19`,
16 Oct), about 1% below the previous state of the art. It deliberately uses
more qubits (1,468, versus 1,235 for the prior leader). This record rewards
fewer gates at any width, so its qubit × Toffoli product is not competitive.

![Fewer Toffolis at higher width: a different trade-off from the best product](docs/figures/record-tradeoffs.png)

How it was built, in short:

- A wider workspace. A stricter allocator returns every freshly allocated wire,
  which lets the modular-inversion walk run with more room. That removes about
  7,400 expected Toffolis.
- Exact repairs to several approximate arithmetic steps inherited from the
  public baseline, plus a smoothed walk-width schedule that removes a cliff in
  the failure rate.
- Exact gate-level caching. The 753,721 version adds 15 verified cache stages
  that reuse repeated AND computations, for 4 extra qubits and about 42 fewer
  Toffolis per shot.

Details, evidence and hashes:
[753,771 entry](experiments/nonce-screen-20261015/STATUS.md) ·
[753,721 entry](experiments/wide15-record-20261016/STATUS.md).

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

- **Product record (benchmark passed, queued).** The leading circuit
  (`4b2ec52f`) plus an exact, universally certified 67-stage cache, at the same
  1,234 qubits. The unchanged benchmark scores **761,121 × 1,234 =
  939,223,314**, 124,634 below the public record, with all 9,024 shots
  passing. It passed its pre-declared failure-rate check (identical
  wrong-answer failures; McNemar p = 0.65; 17.91 vs 17.93 failing batches per
  test set). Nonce 129,023,534, the lowest pass in an ascending search of
  129.2 million. Not yet officially scored.
  [Status](experiments/plain67-final-20261016/STATUS.md) ·
  [note](experiments/plain67-final-20261016/SUBMISSION-NOTE.md).
- **Toffoli record (benchmark passed, queued).** Our wide circuit plus a
  frozen 95-stage exact cache: **753,694** executed Toffolis at 1,556 qubits,
  all 9,024 shots passing; 27 below the current record. Pre-declared gate
  passed against our 753,721 entry (McNemar p = 0.82, identical wrong-answer
  shots). Nonce 294, lowest pass of 379 screened.
  [Status](experiments/wide95-20261017/STATUS.md).
- **Next product step.** A 95-stage cache on the product circuit (PRODUCT95)
  passed its gate (saving 10.6 T over the queued product candidate); its
  nonce search is running. No score until the benchmark confirms it.
- **Qubit record.** The public frontier is at 676 qubits, built on a different
  ring-based design than our 692-qubit circuit.

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
| Wide circuit + 15-stage cache | 1,468 | **753,721** | 1,106,462,428 | Official [`03be8e19`](https://api.ecdsa.fail/api/submissions/03be8e19-ab3b-45c7-9c62-9d78970c4d95) (current Toffoli record) |
| WIDE95 Toffoli candidate | 1,556 | **753,694** | 1,172,747,864 | Local pass, queued; [evidence](experiments/wide95-20261017/STATUS.md) |
| PLAIN67 product candidate | 1,234 | 761,121 | **939,223,314** | Local pass, queued; [evidence](experiments/plain67-final-20261016/STATUS.md) |
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
