# ECDSA Circuit Optimization

**Building smaller, cheaper reversible arithmetic for secp256k1.**

This project studies the quantum circuit at the heart of the
[ECDSA.fail challenge](https://ecdsa.fail/): adding an elliptic-curve point to
another point. Our aim is to advance three resource records—**logical qubits**,
**Toffoli gates**, and their **product**—through reproducible circuit design,
mathematical proofs and measured experiments.

> **Verified status · 14 October 2026:** we have reproduced a public circuit at
> **Q1234 / T761,658 / Q × T939,885,972**, with all 9,024 benchmark shots passing.
> **We have no original submission-ready improvement in any of the three tracks.**
> Failed and unfinished experiments are documented separately in
> [experiment outcomes](docs/experiment-outcomes.md).

[Objectives](#our-three-objectives) · [Verified frontier](#where-the-public-frontier-stands) ·
[Verified results](#what-we-have-verified) · [Next steps](#next-steps) ·
[Reproduce](#explore-and-reproduce)

## Why point addition matters

ECDSA is a digital-signature scheme used in many systems, including
cryptocurrencies. A sufficiently capable fault-tolerant quantum computer could
use Shor's algorithm to solve the underlying elliptic-curve discrete-logarithm
problem. That algorithm repeatedly performs elliptic-curve arithmetic, so making
one of its central operations cheaper can reduce the resources of the larger
computation.

Our circuit implements the in-place operation **`P → P + A`**, where `P` is a
quantum point and `A` is a classically supplied point on secp256k1. It must retain
quantum coherence, return temporary storage to its initial state and avoid
unwanted relative phase. Ordinary classical arithmetic that gives the right
number is not sufficient.

We build and simulate these circuits on ordinary computers. This repository
contains a point-addition research kernel; it does not implement a complete
private-key recovery system or require physical quantum hardware.

## Our three objectives

| Resource | Plain-language meaning | Goal |
|---|---|---|
| **Q: peak logical qubits** | The largest amount of quantum storage used at once | Use fewer qubits |
| **T: mean executed Toffolis** | The average number of costly three-bit reversible gates executed per input | Use fewer expensive gates |
| **Q × T** | The challenge's score, balancing storage and gate cost | Minimize the product |

A logical qubit is an error-corrected computational resource, not one physical
qubit. The scorer uses rounded **mean executed** Toffolis, including conditional
execution; this differs from the number of Toffolis written into a circuit.

The smallest circuit and the cheapest circuit can be different designs. We
therefore maintain separate qubit, Toffoli and product tracks. The platform
promotes the best scalar product; its Pareto frontier also exposes useful
tradeoffs between width and gate count.

## Where the public frontier stands

![Public resource frontier and the product race](docs/figures/frontier.png)

*Only officially scored public circuits and our complete passing baseline replay
appear here. The outlined square is that reproduction, not our own improvement.
Left: the storage/gate tradeoff, with a logarithmic gate axis. Right: the product
leaders. The dashed line marks the best public product.*

Latest snapshot: **1,560 submissions, 1,219 eligible official records and 43
Pareto points**, refreshed on 14 October 2026.

| Objective | Current public record | Our strict target |
|---|---:|---:|
| Minimum qubits | **693**, at T336,852,456 | **Q ≤ 692** |
| Minimum Toffolis | **761,156**, at Q1235 | **T ≤ 761,155** |
| Minimum product | **939,681,128**, at Q1234/T761,492 | **Q × T ≤ 939,681,127** |

At Q1234, a product improvement now needs T ≤ **761,491**. At Q1235 it needs
T ≤ **760,875**. These targets change as other participants improve the record.
The new product record supersedes the Q1234/T761,658 circuit we reproduced.

Sources: [full frontier](docs/frontier-results.md),
[dated data and source revisions](docs/data/latest-leaderboard.json), and
[public submission records](https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74/submissions).
The public Q693 circuit belongs to another contributor and has an official
T336,852,456 result. Its submission was rejected **only because its product did
not beat the scalar leader**, not for a correctness failure. It is a public
comparison point, not a circuit independently reproduced by us. Accepted records
and these explicit score-only rejections are included; failed, pending and
claimed-only records are excluded. Platform validation is a benchmark result,
not a proof of correctness for every possible input.

**Q693 and T761,156 belong to different circuits.** We have not shown a circuit
combining those two records. Our failed Q693 modification is absent from this
plot and all README result tables.

## What we have verified

| Circuit | Peak Q | Mean executed T | Q × T | Evidence |
|---|---:|---:|---:|---|
| Reproduced public baseline `c5bb1ec8` | **1,234** | **761,658** | **939,885,972** | All **9,024 shots passed** |

The unchanged benchmark reported zero classical mismatches, phase-garbage batches
and ancilla-garbage batches. Its generated stream hash matches the earlier
recorded reproduction. This establishes a working environment and a reproducible
starting circuit. It is an existing public design, not a new contribution,
a reproduction of the latest leader, or a new official platform evaluation.
[Exact source, score and verification receipt](docs/data/server-verification.json)

The baseline is valid on its complete benchmark packet, but its product is worse
than today's leader. Re-submitting it would not advance the challenge. We have
**zero original submission-ready candidates** for minimum qubits, minimum
Toffolis or minimum product, and have made no new challenge submission.

All candidate costs, component checks, unsuccessful runs and synthesis
opportunities are in [experiment outcomes](docs/experiment-outcomes.md) and
[the detailed research notes](docs/research-plan.md). They are excluded from
README performance plots and result tables until a complete candidate passes
validation and its exact source, stream and score are preserved.

## Server workflow

The baseline reproduction and the failed experimental evaluation are complete.
At the last inspection, neither ECDSA evaluation remained running. ECDSA work
uses `smu_server` in `/home/hclau/ecdsa_research`. Before each launch we inspect
available CPU and memory and check active jobs. Long calculations use **`nohup`**,
a dedicated log and a saved PID. See [server operations](docs/SERVER_HANDOFF.md)
for commands, resource limits and preserved run evidence.

## Next steps

We keep all three objectives active, with separate designs where needed.
Our first optimization work should start from the **passing Q1234 baseline**:
its full benchmark replay took about four minutes, making gate experiments much
faster to verify than the low-width circuit.

1. **Toffolis and product:** optimize the complete fold construction and cleanup
   together, rather than the isolated correction tables, whose fixed interfaces
   already meet their AND-count lower bounds. At Q1234, T ≤ **761,491** beats
   today's product; T ≤ **761,155** beats both the Toffoli and product records.
   Each replacement must include its scratch, cleanup and phase-repair cost.
2. **Qubits:** first replay the failed compact-reciprocal inputs against the
   unmodified public source and locate the first state divergence. Repair and
   fully validate the change before using it as the basis for a **Q692** design.
   Prove register ownership throughout the full circuit before sharing another
   lane. This remains a separate width track.
3. **Qualification:** run relevant component tests, paired and independent input
   checks, then the unchanged full benchmark on the final source. Preserve its
   passing log, source and stream hashes, valid score and fresh public comparison.
   Only then add a candidate to the README and prepare it for submission.

Only `src/point_add/` belongs in a contestant submission. We preserve the harness,
simulator, scorer, reference curve, dependencies and toolchain. We do not search
identity-tail nonces to select a passing test packet. Passing a finite packet
remains distinct from an all-input correctness proof.

## Explore and reproduce

| Location | Contents |
|---|---|
| `agents/qubits/` | Public Q693 base plus our compact-reciprocal working changes |
| `agents/toffoli/` | Public minimum-Toffoli base |
| `agents/product/` | Reproduced `c5bb1ec8` product base; latest public record is tracked in the data |
| `src/point_add/` | Earlier Q1235 implementation and inactive root research |
| `experiments/` | Reapplicable patches and exact source provenance |
| `scripts/` | Analysis, plots, proofs, audits and server helpers |
| `docs/data/`, `docs/figures/` | Compact evidence and generated plots |
| `research-output/` | Ignored raw snapshots, logs and large generated artifacts |

Initialize the public source tracks, then use Python for analysis:

```bash
git submodule update --init --jobs 3
python -m pip install matplotlib==3.11.2 z3-solver==5.1.0.0
python scripts/audit-workspace.py
python scripts/test_leaderboard.py
python scripts/analyze-leaderboard.py --refresh --plot
python scripts/prove-compact-reciprocal.py
python scripts/analyze-fold-core.py
```

Use an isolated Python environment; platform-specific commands are in
[local setup](LOCAL_SETUP.md). Circuit compilation uses pinned **Rust 1.93.0**,
locked dependencies and the Linux benchmark harness. To reproduce our candidate
in a fresh public checkout, follow [the experiment instructions](experiments/qubits/README.md).

Earlier uncommitted helpers and ignored evidence were absent from the transferred
workspace. Their reports are marked historical; see [the recovery audit](docs/data/workspace-audit.json).
The active source includes have been checked. A root Git commit cannot preserve
uncommitted submodule changes, which is why the experiment patch is tracked here.

## Research foundations and credits

This project builds on the public challenge and its contributors' circuits.
Public reproductions are credited to their source revisions; our local changes
are separated in experiment patches.

- [Official challenge source](https://github.com/Layr-Labs/ecdsafail-challenge)
  and [challenge rules](https://ecdsa.fail/terms).
- [Optimized point-addition circuits](https://arxiv.org/html/2606.02235v1):
  Euclidean decision recording, coefficient replay and specialized modular arithmetic.
- [Efficient record-and-replay arithmetic](https://arxiv.org/html/2609.28882v1):
  compressed decisions, ping-pong GCD and fused replay.
- [Space-efficient point addition](https://arxiv.org/html/2607.13816v2):
  register sharing and explicit circuit-level constructions.
- [Temporary logical ANDs](https://arxiv.org/abs/1709.06648) and
  [controlled add/subtract multiplication](https://arxiv.org/html/2410.00899v1).

For what worked, what failed and what remains unproven, read
[experiment outcomes](docs/experiment-outcomes.md) and
[the research plan](docs/research-plan.md). Licensing and attribution information
is preserved in [NOTICE](NOTICE); this workspace does not replace the upstream
terms or claim ownership of reproduced public designs.
