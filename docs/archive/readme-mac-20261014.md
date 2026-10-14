# Archived pre-recovery document

This describes the earlier Mac workspace. Referenced ignored artifacts and uncommitted track changes were not transferred. Use the current root README and setup documentation.

# ECDSA.fail optimization workspace

This workspace contains the official secp256k1 point-add challenge, local research,
and three separate optimization tracks. **No original improvement has yet passed
the full official benchmark or been submitted to the platform.**

For another machine or a CPU server, start with [the server handoff](docs/SERVER_HANDOFF.md).
It covers transferring uncommitted code and ignored evidence, repairing shared Git
paths, recreating the environment, memory planning, verification, and next tasks.

## Recorded results — 14 October 2026

These are saved public records. Refresh [ECDSA.fail](https://ecdsa.fail/) before
comparing or submitting; the live leaderboard may advance.

| Objective | Qubits | Rounded Toffolis | Product | Source revision |
|---|---:|---:|---:|---|
| Minimum qubits | **694** | 336,751,889 | 233,705,810,966 | `4ef906688f6dfb422aa8dd10d3d07265839e2f3c` |
| Minimum Toffolis | 1,235 | **761,156** | 940,027,660 | `b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7` |
| Minimum product | 1,234 | 761,658 | **939,885,972** | `c5bb1ec876db859a3f9f8a9052c140a145df834e` |

The website and supplied screenshot show **694**, not 684, as the minimum width.
The latest saved API snapshot has 1,558 submissions and 42 derived frontier points.
The website inspection showed 1,040 historical frontier advances. The official
scalar score promotes the lowest product; the Pareto view shows different width/gate
tradeoffs, including correctness-passing score-only rejections.

We reproduced Q1235/T761156 in the main checkout and Q1234/T761658 in the product
checkout through the unchanged official benchmark, with all 9,024 shots passing.
The product stream was rebuilt byte for byte after adding the research helpers.
Reproduction is not an original leaderboard improvement.

## Code and research status

| Folder | Purpose | Current state |
|---|---|---|
| Workspace root | Earlier Q1235 work | Exact implication cleanup prototype; disabled because its official packet fails |
| `agents/qubits` | Minimum-width Scheme G | Compact reciprocal tested in a 693-wire component frame; complete circuit still Q694 |
| `agents/toffoli` | Minimum-gate track | Phase-reader prototype passes fixtures; zero savings on the full incumbent stream |
| `agents/product` | Product track | Leader reproduced; missing guard recovery unqualified; default stream unchanged |
| `agents/source-cache.git` | Shared public Git storage | Required when transferring the shared clones; repair paths with the relocation helper |

The three delegated agents hit the account usage limit before starting research.
The primary agent performed this iteration. No agents are continuing in the background.

The strongest lead is `stage1_v_compact` in `agents/qubits/src/point_add/midg.rs`.
It uses 24 remainder lanes plus the existing quotient flag, retaining K24 precision
and TC26. The arithmetic identity is solver-proved in its stated domain. Native
component tests cover values, inverse behavior, dirty passengers and phase corrections.
Two representative layouts save **104 Toffolis per V-form call**.

**This is not a complete 693-qubit result.** The highest external quotient bit competes
with SX6, the gate-on accumulator; the seven-lane crossing reserve must remain valid.
A proved ownership/recomputation schedule is the next task. Read
[the campaign report](docs/parallel-campaign.md) for proof limits and failed approaches.

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
This campaign did not search nonces or submit publicly.

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
- [Latest saved Pareto frontier](docs/frontier-results.md)
- [User-supplied background writeup](docs/user-writeup.md)
- [Archived upstream README](docs/upstream-readme.md)

Machine-readable status: `research-output/parallel-20261014/campaign-status.json`.
Each track has `research-output/track-result.json`. Logs, source snapshots, compressed
streams, solver inputs/results and submission notes accompany the source in the handoff.
Much of this evidence is ignored by Git; pushing tracked files alone loses it.

Official sources: [site](https://ecdsa.fail/),
[repository](https://github.com/Layr-Labs/ecdsafail-challenge),
and [benchmark API](https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74).
