# CPU-server handoff — 14 October 2026

**Historical local handoff.** On 17 October, MonitSharma's public results lead
the product (939,223,314) and Toffoli (753,694) objectives, with four current
Pareto points. See [current results](leaderboard-results.md). The local source,
scores, reproduction evidence and next tasks below describe the older checkout;
they are not the source or evidence for those later submissions.

## Read this first

The objective is to establish improvements on **three separate fronts**: minimum
logical qubits, minimum mean executed Toffolis, and minimum qubit-Toffoli product.
They can require different circuits. As of this **14 October local handoff**,
there was no new qualified result of our own and no public submission.

We have reproduced the public Q1235/T761156 baseline and the newer
Q1234/T761658/product939885972 baseline. A compact reciprocal component fits a
693-wire fixture and saves 104 Toffolis per tested V-form call. It has **not**
been integrated into a complete 693-qubit point-add circuit.

The three separate agent checkouts already exist, but the delegated agents were
blocked by account usage limits. The primary agent did the recorded research.
There are no background agents to wait for. CPU-server access removes the local
memory constraint; it does not automatically remove an AI account usage limit.

## Transfer the complete workspace

The transfer archive is created at:

```text
handoff/ecdsa-server-handoff-20261014.tar.gz
handoff/ecdsa-server-handoff-20261014.tar.gz.sha256
```

It contains the four checkouts' source, their Git metadata and shared source cache,
all documentation, uncommitted experiments, public records/notes, saved operation
streams, compact `.u32` diagnostic streams, proof slices/results, logs and scores.
It excludes `.tools`, `.venv`, all compiled `target/` directories and Python caches.
The `.tools` exclusion also omits the local CLI credential/config directory.
Important first-iteration logs were copied to `research-output/iteration-1-logs`
so they survive that exclusion.

If files change after this handoff, regenerate it from the root with:

```bash
python3 scripts/create-handoff.py
```

Do not transfer only a Git push: many evidence files and all separate working
copies are untracked or ignored. Do not copy only one shared clone: its Git
objects depend on the source cache and primary object store. The complete archive
preserves all of them. It has not been uploaded to any remote machine.

After copying the archive and its checksum to the destination:

```bash
sha256sum -c ecdsa-server-handoff-20261014.tar.gz.sha256
mkdir -p ~/work
tar -xzf ecdsa-server-handoff-20261014.tar.gz -C ~/work
cd ~/work/ecdsa
python3 scripts/verify-handoff.py
python3 scripts/relocate-handoff.py
```

Run file verification **before** relocation or editing. Relocation deliberately
changes the hashed Git `alternates` files. It replaces the old absolute Mac
object paths with relative paths and checks Git connectivity in all three tracks.
It does not reset the source or discard changes. The activation files also now
resolve their paths relative to the workspace.

## Hardware and scheduling

The Mac used for this work has 36 GiB RAM and 12 logical CPUs. The Q694 baseline
contains 1,138,443,186 operations. At 56 bytes per operation its vector alone is
59.4 GiB. Allocation growth, temporary buffers, compiler processes and the OS need
additional room.

**Plan for 128 GiB RAM for the first full low-qubit run**, preferably with spare
disk space for diagnostics and operation streams. This is a conservative planning
recommendation, not a measured peak or guarantee. Record actual RSS with
`/usr/bin/time -v`. Start the large low-qubit benchmark alone; do not run three
memory-intensive full benchmarks simultaneously merely because three agents exist.
The Q1234/Q1235 streams have about 11.5–11.7 million operations and are much smaller.

Compilation and independent experiments can use multiple CPU cores. The current
scorer applies its 141 batches of 64 shots in one process and does not expose
automatic multi-core distribution of one benchmark. More cores alone do not make
the billion-op verification cheap. Use independent build targets and coordinate
RAM admission between agents. Start with `CARGO_BUILD_JOBS=2`; increase it after
observing memory use. Avoid changing the protected scorer to claim an official win.

## Recreate the environment on Linux

Linux execution is **not yet verified** by this campaign. These commands are the
handoff procedure inferred from the unchanged setup/harness scripts and pinned
versions. Preserve the source snapshots while resolving machine setup problems.

1. Install Git, Python 3.13 with venv support, and a working C compiler/linker
   through the server's normal software provisioning process.
2. From the workspace root, run the official `./setup.sh`. It installs/selects the
   pinned Rust 1.93.0 toolchain, fetches Cargo dependencies, and prepares Linux
   sandbox support. It may invoke the system package manager/sudo for prerequisites.
3. Recreate Python, then activate the workspace:

```bash
cd ~/work/ecdsa
./setup.sh
python3.13 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-research.txt
source ./activate.sh
rustc --version
cargo --version
python -c 'import numpy, z3; print(numpy.__version__, z3.get_version_string())'
```

The versions recorded here are Rust1.93.0, Python3.13.7, NumPy2.5.4 and
Z3-solver5.1.0.0. The full Python requirements also pin plotting/notebook packages.
Python 3.13 and platform-compatible wheels are recommended for that lockfile.
If a wheel/version cannot be installed on the server, record the exception rather
than silently calling the environment identical. No Cargo dependencies may change.

`activate.sh` uses project-local Rust when it exists; on the recreated server it
uses the server's rustup installation and pins `RUSTUP_TOOLCHAIN=1.93.0`. It selects
the root `target/`. Each `activate-track.sh` then selects its own track `target/`.
The benchmark expects binaries under that track's `target/release` path, so do not
override `CARGO_TARGET_DIR` to an unrelated location.

Do not reuse Mac `.venv`, Rust/Bun executables or release binaries on Linux.
The official CLI is optional for local research: `./benchmark.sh` does not need it.
If needed for public submission, install the official Linux CLI and authenticate
on the destination separately. Credentials are not part of this handoff.

## Track selection and source provenance

| Track | Base source SHA | Baseline | Objective |
|---|---|---|---|
| Root | `b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7` | Q1235 / T761156 / product940027660 | Preserve earlier failed cleanup and exact-equivalence evidence |
| `agents/qubits` | `4ef906688f6dfb422aa8dd10d3d07265839e2f3c` | Q694 / T336751889 / product233705810966 | Complete a verified Q≤693 circuit |
| `agents/toffoli` | `b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7` | Q1235 / T761156 / product940027660 | Rounded T≤761155, preferably with a substantial margin |
| `agents/product` | `c5bb1ec876db859a3f9f8a9052c140a145df834e` | Q1234 / T761658 / product939885972 | Product<939885972 |

Use separate terminals, initially in the workspace root:

```bash
source agents/qubits/activate-track.sh
# OR, in another terminal:
source agents/toffoli/activate-track.sh
# OR, in another terminal:
source agents/product/activate-track.sh
```

These are independent code and build folders with shared immutable dependency
installations. Do not reset a track to main: its uncommitted research is the work
being handed off. Refresh public results separately and record new baseline SHAs
before porting research onto a newer revision.

The API snapshot lives in `research-output/parallel-20261014/submissions.json`;
leaders and their full notes are saved alongside it. It has 1,558 records. The
older `research-output/all-submissions.json` has 1,557 and is retained for historical
reproduction. Both are historical. The updated plot script now defaults to the
hashed 17 October snapshot in `docs/data/leaderboard/`; it reproduces the current
figures and can refresh public data with `--refresh`.

## Resume the qubit track first

Relevant files in `agents/qubits/src/point_add`:

- `midg.rs`: new `stage1_v_compact`; production `middle` still uses the old path.
- `tests_midg_k24.rs`: generalized 276/277-ring component fixtures, the first
  693-wire experiment, compact reciprocal test and component gate prices.
- `pointadd_frogdrop.rs`: production N277/K18/KP24/QB23/EMAX22 constants.
- `frogdrop_col.rs`: 13-lane pool, switch flag and map-stage sharing.
- `frogdrop.rs`: compare/conditional-subtract primitives supporting the compact step.

Run the fast checks before changing integration code:

```bash
# Root terminal:
source ./activate.sh
python scripts/prove-compact-reciprocal.py

# Qubit-track terminal:
source agents/qubits/activate-track.sh
CARGO_BUILD_JOBS=2 cargo test --release --locked --offline --bin build_circuit \
  tests_midg_k24 -- --nocapture
```

Recorded outcome: 12 tests pass, one existing explicit research test is ignored.
The compact fixture covers 512 cases, 903,168 independent measurement-phase
coefficients, and forward/inverse comparisons. It saves 104 Toffolis in both
representative V-form calls (columns10 and85). The earlier noncompact 693-wire
fixture covers 768 cases but consumes six SX remainder owners.

The arithmetic proof is universal within `D` odd, high bit set, `0≤R<D`; it covers
widths2–8,16,24 and detects a missing-overflow negative control. The native fixtures
are finite checks. Neither is a complete point-add correctness proof or a verified
minimum-qubit record.

**Next integration work:** a 276-lane ring moves q18..q23 outside the ring. SX6 is
the gate-on accumulator and cannot hold q23 during other quotient iterations. The
compact reciprocal releases SX6 during reciprocal execution, but that does not
solve its lifetime between calls. Keep all seven crossing-reserve lanes. Investigate
a derived-switch-flag owner or exact recomputation schedule, including delayed
crossing payload padding; prove the complete lifetime before changing N/K/EMAX.
Do not just shrink constants or lose precision to make a narrow fixture appear to work.

For eventual complete verification, use `./benchmark.sh` unchanged. The low-qubit
builder's `LOWQ_EXACT_STREAM_PATH` is a research-only streaming diagnostic: it
returns an empty in-memory vector and is not a substitute for the official builder
contract. Unset it for an official benchmark:

```bash
unset LOWQ_EXACT_STREAM_PATH
/usr/bin/time -v ./benchmark.sh --note "Describe the complete width change" \
  > research-output/official-candidate.log 2>&1
```

## Resume the Toffoli and product tracks

The late prototype `cond_pass::phase_readers` extends phase-only AND analysis to
CZ readers. It follows original values through holders/affine forms, adds CZ/CCZ
phase terms, accounts for added Toffoli cost and rejects nonpositive or conflicting
sites. Its ordinary early-pass behavior is preserved. It is not called by the
default build in either track.

In either track:

```bash
CARGO_BUILD_JOBS=2 cargo test --release --locked --offline --bin build_circuit \
  tests_phase_readers -- --nocapture

# Saved final.u32 exists in the handoff; search only, without changing defaults:
CARGO_BUILD_JOBS=2 cargo test --release --locked --offline --bin build_circuit \
  research_probe::search_final_phase_readers -- --ignored --nocapture
```

Recorded result: two native fixtures pass, including changed controls, preserved
measurements and a stale-control fault. Full-stream scans in both tracks find
**zero sites and zero savings**. The narrow phase-box search also found zero
positive candidates. Do not repeat these scans expecting a record without a new
hypothesis. A broader complete fold-core synthesis or shared phase-repair prefix
is a better next Toffoli lead; see the proposal for tested lower-bound limits.

For product, the leader omitted 1,008 extra square carry guards from Q1235. Our
partial transplant experiment found five matching blocks covering130 deleted-AND
entries. Four local equivalence checks have counterexamples under their boundary
assumptions; one has an unmatched condition pop. No transplant qualified or was
installed. These are incomplete/local failures, not a disproof of the whole guard
construction. Complete regeneration needs measurement correspondence, live classical
outputs, full guard lifetimes and phase twins; never bypass existing binding checks.

Saved checkpoints make the proof screening reproducible from the root:

```bash
python scripts/track-known-prefix.py
python scripts/prove-track-slice.py
```

The matching/extraction was performed as an inline research calculation; its
outputs are archived in `proof-candidates.json`, `square-match-blocks.json`, and
`proofs/*-original.u32` / `*-candidate.u32`. There is not yet a complete production
table-regeneration tool. These checkpoints bind to the saved streams; after source
changes, regenerate and revalidate them rather than reusing old indices/hashes.

Optional final-stream regeneration in either track:

```bash
CARGO_BUILD_JOBS=2 cargo test --release --locked --offline --bin build_circuit \
  research_probe::export_stream_stages -- --ignored --nocapture
```

This overwrites `research-output/pre-extra-guards.u32` and `final.u32`. Preserve
historical copies before exporting after changes. The dumps are diagnostics,
not official scores. `scripts/find-phase-boxes.py product|toffoli` reads these dumps.

## Earlier root experiment: preserve it, do not enable it blindly

`src/point_add/final_cleanup.rs` and the implication mode in `truth_simplify.rs`
save about1.493462 executed Toffolis on a paired candidate packet at Q1235.
The modified canonical packet fails11 classical checks and9 phase batches; the
incumbent fails identically on that packet. Ancilla failures are zero. The exact
rewrite does not repair inherited approximate arithmetic. `EXPERIMENTAL_FINAL_CLEANUP`
is false; the root default remains the passing baseline.

To replay the archived tests from the root:

```bash
source ./activate.sh
cargo test --release --locked --offline --bin build_circuit \
  point_add::final_cleanup::tests -- --include-ignored --nocapture
```

The ignored tests require `research-output/optimization-baseline/ops.bin` and
`research-output/cleanup-v1-ops.bin`, both included in the archive. The tests compare
forward/reverse states; they do not prove the approximate incumbent universally exact.

## Evidence and qualification rules

The product's official source replay gave Q1234, roundedT761658 and score939885972.
Its compressed `ops.bin` SHA256 is
`49b35cf7640ebd529d76894eb8bef93ebf57e7e970fe14b3c27c8c5feb6e73e4`.
The later default compact stream rebuild matches the saved final.u32 hash.
Do not compare a compact `.u32` hash to the compressed `ops.bin` hash.

Important evidence includes:

- `agents/product/score.json` and `research-output/official-baseline.log` in that track.
- Product `default-byte-rebuild.log`, `default-byte-identity.log`, and the saved SHA file.
- Qubit `k24-compact-tests.log`, `compact-step-arithmetic-proof.json` and `.log`.
- Both gate tracks' `phase-readers-combined.log` and saved candidate diagnostics.
- Root `canonical-inheritance.json`, first-iteration snapshots and preserved logs.
- `research-output/parallel-20261014/campaign-status.json` plus per-track result JSONs.

The current scorer checks forward output, ancillas and phase on9,024 hash-derived
inputs. It does not implement the archived README's inverse-identity claim.
Leading source circuits contain approximation; reported author population failures
are not our independent universal-correctness result. Keep expected gate-list cost,
paired mean cost, rounded official cost and peak width separate in reports.

Only `src/point_add/` changes belong to a contestant submission. Leave simulator,
scorer, harness, Cargo dependencies and toolchain files untouched. The harness may
append `results.tsv`; do not edit its measurements manually. Documentation and
environment helpers are outside contestant scope. No public submission or login
was performed, and no API credentials are included in this transfer.

Before proposing a record, refresh public baselines, prove the new identities and
lifetimes, test independent/paired inputs and deliberate faults, rebuild from exact
source, run the unchanged official benchmark, preserve logs/stream hashes, and compare
the final metrics with the intended objective. A component count or passing unit
test is not a qualified leaderboard result.
