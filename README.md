# ECDSA.fail · Pareto-leading circuit research

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

## Reproduce or refresh the plots

The figures, counts, highlights and record comparisons are generated from the
saved official data. Both high-resolution PNG and editable SVG versions are
available in `docs/figures/`; the original `research-output/` figure paths are
updated at the same time.

```bash
source ./activate.sh
python scripts/analyze-leaderboard.py           # reproduce offline
python scripts/analyze-leaderboard.py --refresh # fetch and analyze new public data
```

The script verifies snapshot hashes, official Q × T products, and agreement with
benchmark metadata before plotting. See [snapshot provenance](docs/data/leaderboard/README.md).
The dated README and narrative result report record this snapshot; review them
when refreshing to a later leaderboard.

## Local research checkout · 14 October archive

The published records above come from the official service. This Mac checkout
still contains the earlier research and reproduced baselines; this documentation
refresh does not import the newer winning source or rerun its circuit benchmark.
The local `score.json` and track sources retain their measured provenance.

| Folder | Purpose | Local state recorded on 14 October |
|---|---|---|
| Workspace root | Earlier Q1235 work | Exact implication cleanup prototype; disabled after a failed official packet |
| `agents/qubits` | Minimum-width Scheme G | Compact reciprocal tested in a 693-wire component frame; complete circuit still Q694 |
| `agents/toffoli` | Minimum-gate track | Phase-reader prototype passes fixtures; zero savings on the incumbent stream |
| `agents/product` | Product track | Q1234/T761658 reproduced; missing guard recovery unqualified |
| `agents/source-cache.git` | Shared public Git storage | Required when transferring shared clones; repair paths with the relocation helper |

For another machine or a CPU server, start with [the server handoff](docs/SERVER_HANDOFF.md).
It covers transferring uncommitted code and ignored evidence, repairing shared Git
paths, recreating the environment, memory planning, verification, and next tasks.
Its circuit baselines and the [campaign report](docs/parallel-campaign.md) describe
the 14 October local state and predate the public records above.

The compact-reciprocal lead remains a component result: two tested layouts save
104 Toffolis per V-form call, but a complete 693-qubit integration was unfinished
in that local campaign. See the campaign report for its proof limits.

## Running locally

The current Mac environment is project-local. Activation resolves script-relative
paths and supports a recreated server environment.

```bash
source ./activate.sh
python scripts/prove-compact-reciprocal.py
source agents/qubits/activate-track.sh
cargo test --release --locked --offline --bin build_circuit \
  tests_midg_k24 -- --nocapture
```

Use separate terminals for separate tracks. Track activation changes directory and
selects its own `target/`, while sharing the installed Rust/Python dependencies.
For an integrated candidate on suitable hardware, use the unchanged script:

```bash
./benchmark.sh --note "Describe the candidate and its verification"
```

The older bare `cargo run --release` instruction is ambiguous: this checkout has
separate `build_circuit` and `eval_circuit` binaries. The script builds offline,
confines the builder, runs the trusted scorer, writes a score for a passing run,
and appends `results.tsv`. A failed or missing score must not be replaced with an
old score or a claimed estimate.

## Scoring and validation

The circuit overwrites quantum `(x, y)` with its secp256k1 sum with classical offsets.
The current score is **rounded mean executed Toffolis × peak logical qubits**.
It is not circuit depth and not the emitted Toffoli count alone.

The scorer checks 9,024 Fiat-Shamir-derived inputs for outputs, phase garbage and
ancilla garbage. It does **not** implement the forward/reverse identity test claimed
in the archived upstream README. Separate inverse checks supplement it. A passing
packet does not prove universal correctness: inherited leading circuits contain
approximate arithmetic and their authors report failures on other packets.

Changing a gate changes the canonical packet. Measure real improvements on independent
and paired inputs, preserve phase/measurement semantics, and benchmark final source.
The 14 October local campaign did not search nonces or submit publicly. The later
public submissions disclose identity-tail nonce searches and fresh-input failure
measurements; see [the current result notes](docs/leaderboard-results.md).

Only `src/point_add/` is eligible contestant code. Preserve the harness, simulator,
scoring programs, Cargo files and toolchain specification. Bound tables must reject
mismatched prefixes; regeneration requires new proofs, not forced hash edits.
Local documentation and research helpers are outside submission scope.

## Server resources

The local machine has 36 GiB RAM and 12 logical CPUs. The Q694 baseline has
1,138,443,186 operations: its 56-byte operation vector alone is **59.4 GiB**.
Plan for **128 GiB RAM** for the low-qubit full benchmark as a conservative operating
recommendation, not a measured peak or guarantee. Run it alone and measure memory.
More cores help compilation and independent experiments; this scorer does not
automatically distribute one benchmark across CPU cores.

Recreate Rust **1.93.0**, a C linker, Python **3.13**, and a new virtual environment.
Do not reuse the Mac `.venv`, Rust/Bun binaries or compiled `target/` on Linux.
Linux execution has not yet been verified here. See [SERVER_HANDOFF.md](docs/SERVER_HANDOFF.md).

## Documentation and evidence

- [Server handoff and continuation plan](docs/SERVER_HANDOFF.md)
- [Three-track campaign](docs/parallel-campaign.md)
- [Current Mac setup](LOCAL_SETUP.md)
- [Verified baseline provenance](docs/setup-verification.md)
- [First failed qualification attempt](docs/optimization-iteration-1.md)
- [Updated research proposal and historical analysis](docs/optimization-proposal.md)
- [Current public results and attribution](docs/leaderboard-results.md)
- [Current Pareto frontier](docs/frontier-results.md)
- [Reproducible leaderboard snapshot](docs/data/leaderboard/README.md)
- [User-supplied background writeup](docs/user-writeup.md)
- [Archived upstream README](docs/upstream-readme.md)

Historical local campaign status: `research-output/parallel-20261014/campaign-status.json`.
Each track has `research-output/track-result.json`. Logs, source snapshots, compressed
streams, solver inputs/results and submission notes accompany the source in the handoff.
Much of this evidence is ignored by Git; pushing tracked files alone loses it.

Official sources: [site](https://ecdsa.fail/),
[repository](https://github.com/Layr-Labs/ecdsafail-challenge),
and [benchmark API](https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74).
