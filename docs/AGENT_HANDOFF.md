# Agent handoff: start here

Last updated 15 October 2026, 22:10 Singapore. This page is for an AI agent (or
person) continuing the work. It holds the current state, the rules, the tools
and the next steps in order. Details live in the linked reports. Do not copy
numbers from older reports without checking the date.

**Active run, started 22:39 Singapore:** user priority is **product, Toffolis,
qubits**, in that order; submission mode **queue**. See
[`experiments/autorun-20261015-2239/LOG.md`](../experiments/autorun-20261015-2239/LOG.md)
before starting overlapping jobs. Four isolated workstreams cover the
prefilter, exact product savings, unexplained failure localization, and the
wide cache pass. No new result is qualified yet. Public refresh at 22:39
leaves all three records unchanged.

## 1. Read in this order

1. [`AGENTS.md`](../AGENTS.md): binding project rules, including the
   **disclosed-failure-rate standard** for nonces.
2. This page.
3. [`experiments/nonce-screen-20261015/STATUS.md`](../experiments/nonce-screen-20261015/STATUS.md):
   how our official Toffoli record was made, with the screener and census.
4. [`experiments/product-tip-20261015/STATUS.md`](../experiments/product-tip-20261015/STATUS.md):
   why the product record is blocked, with search-cost figures.
5. [`docs/research-plan.md`](research-plan.md) (newest entries first) and
   [`docs/results-status.md`](results-status.md) as needed.
6. [`docs/SERVER_HANDOFF.md`](SERVER_HANDOFF.md) for server directories of
   older experiments.

To run continuously, use the cycle and backlog in
[`docs/AUTONOMOUS_PROMPT.md`](AUTONOMOUS_PROMPT.md) (paste it with `/loop`).

## 2. State of the three records

Refresh first: `.venv-research/Scripts/python.exe scripts/analyze-leaderboard.py --refresh --plot`
(writes `docs/data/latest-leaderboard.json`, `docs/frontier-results.md` and
`docs/figures/frontier.*`).

| Record | Public best (22:07 refresh) | Ours | Strict next target |
|---|---|---|---|
| Min executed Toffolis | **753,771 at Q1464 — ours** (`3f32acd2`, source `5a7c3902`) | Official | T ≤ 753,770 |
| Min Q × T | 939,347,948 = 761,222 × 1,234 (jackylee0424, `85d067da`, source `4b2ec52f`) | None | T ≤ 761,221 at Q1234; T ≤ 760,605 at Q1235 |
| Min qubits | 679 (jackylee0424, `80fe2050`) | Local Q692 pass only, unsubmitted | Q ≤ 678 |

The user's priority (15 Oct, night): improve any of the three records, each
judged independently, in long unattended runs
([AUTONOMOUS_PROMPT.md](AUTONOMOUS_PROMPT.md)). The Q679/Q680 sources are on
the upstream branches `submissions/80fe2050-…` and `submissions/ebf0b736-…`.

## 3. Rules that shape every decision

- Only `src/point_add/` may differ in a submission. The harness, evaluator,
  simulator, curve reference, Cargo files and toolchain stay byte-identical.
- **Nonces.** Screen an identity-tail nonce only on a **frozen** circuit
  whose **fresh-input census** shows failed batches per 9,024-shot packet at
  or below those of the record it beats, and never above 18. Pre-declare the
  policy (we use: ascending from 1, lowest pass). Never pick a nonce for its
  T, never tune circuit content to a packet, and never cut gates that trade
  correctness for T. Publish the nonce, the census and the number screened.
- Submitting is outward-facing, so ask the user first. The `ecdsafail` CLI
  is installed and authenticated on the server at
  `/home/hclau/.local/bin/ecdsafail`. Never handle or commit credentials
  (`.env` is ignored).
- README plots show only officially scored or complete locally passing
  results. Diagnostic figures stay in experiment reports.

## 4. Key facts learned (use these numbers)

| Fact | Value | Source |
|---|---|---|
| Official packet | 141 batches × 64 shots; inputs and measurement randomness come from a SHAKE256 hash of the whole op stream | `src/bin/eval_circuit.rs` |
| Pass probability on a fresh packet | (1 − f)^141, where f = census batch-failure fraction (**not** e^−λ when f is large) | census |
| Exact screener speed | about 0.25 s per 64-shot batch per thread (wide 0.236, tip 0.249, B3 0.277) | screen logs |
| Search practical with the exact screener | ≤ 10 failed batches: < 1 h on 32 threads; ≤ 13.85: < 1 day on 64 threads; 17.7: about 58 days on 64 threads | `experiments/product-tip-20261015/figures/search-cost.png` |
| Product tip `4b2ec52f` | failure rate 17.69, fresh mean 761,221.70 T, packet SD of mean T 6.2 | product-tip report |
| Our official entry | failure rate 5.47 (B3: 17.73), fresh mean 753,763.5 T | nonce-screen report |
| One qubit at Q1234 is worth | about 617 T of product | 761,222 / 1,234 |
| Width-free exact cache saving | about 4 T on B3, **2.2 ± 1.2 T on the tip**; failure rate unchanged | cache-idle, product-tip |
| Cache with about 5 extra qubits | about 101 T at diagnostic Q1240 | cache-retention |
| Tail smoothing (walk rows 137/138) | +37 T for about −1.4 failed batches (wide circuit) | widen-walk |
| Failure anatomy (wide circuit, traced) | about 84% of value failures in leapfrog walk rails; about 1.1 batches outside the walk, unlocalized | trace-value, widen-walk |

## 5. Tools (all on `smu_server` under `/home/hclau/ecdsa_research`)

Before any launch, check `uptime`, `free -g` and the top processes (two large
`python` jobs from the separate chemistry project usually use about 35 cores;
leave them alone). Use `nohup`/`setsid`, dedicated logs and PID files.
Defaults: `CARGO_BUILD_JOBS=4`, `RAYON_NUM_THREADS=1`; 32 screener or census
threads have been fine.

| Tool | Path | Usage |
|---|---|---|
| Fresh-input census | `failure-census-20261015/target/release/failure_census` | `failure_census OPS LABEL 0 4096 32 out.jsonl` → 262,144 shots in about 35 s. Failure rate = 141 × (failed batches / 4096). The same LABEL on two streams gives **paired** inputs. |
| Nonce screener | `nonce-screen-20261015/screen/target/release/nonce_screen` | `nonce_screen OPS FIRST COUNT THREADS out.jsonl` (lowest passing nonce ≥ FIRST, then a verbatim `run_tests` re-check); `nonce_screen OPS @official` replays the stream's own packet. Source: [`experiments/nonce-screen-20261015/screen`](../experiments/nonce-screen-20261015/screen). |
| Official benchmark | `./benchmark.sh` in a candidate tree | Appends a row to `results.tsv`; revert that before committing. Template: `experiments/nonce-screen-20261015/run-benchmark.sh`. |
| Stream cache rewriter (external) | `cache-idle-20261015/target/release/product_paired_diagnostic` | `CACHE_ATOM_CAP=32 CACHE_PRODUCT_CAP=200000 product_paired_diagnostic IN.bin OUT.bin`. For **measurement only**: a submission must generate the stream itself, so port the pass into `src/point_add`, as `experiments/toffoli-readiness-20261015/prepare.py` / `prepare-wide.py` do (`lazy_cache.rs` plus `ops = lazy_cache::optimize(ops);` before the nonce tail). |
| Public challenge clone | `toffoli/` (origin = Layr-Labs/ecdsafail-challenge) | `git fetch origin <sha>`, then `git worktree add ../<exp>/tip <sha>`. |
| Product tip source | public commit `4b2ec52f` | Removed from the server on 15 Oct. Recreate: `git -C toffoli fetch origin 4b2ec52fc55da796aa8f5ef851290297e8706424 && git -C toffoli worktree add --detach ../<exp>/tip 4b2ec52f`, then `cargo build --release --locked --offline --bin build_circuit` and run `build_circuit` (about 2 min) to get `ops.bin` (SHA-256 `2a522394…`). |
| Official-entry source | patch `experiments/nonce-screen-20261015/evidence/candidate-7ff2ba53.patch.gz` (also `nonce-screen-20261015/candidate-7ff2ba53.patch` on the server) | Worktree and branch removed on 15 Oct. Recreate: `git -C toffoli worktree add --detach ../<exp>/cand b3c9fdd6` and `git -C ../<exp>/cand am <patch>`. Rebuilt stream must hash to `01aad987…`. The scored copy is `5a7c3902` on the public challenge repo. |

Locally, use `.venv-research/Scripts/python.exe` (there is no `python` on
PATH). Run `scripts/test_leaderboard.py` and `scripts/test_frontier_plot.py`
after touching the data or plots.

## 6. Next steps, in priority order

1. **Lower our own Toffoli record.** The direct cache transfer was measured
   during the 22:39 run: **6.43 ± 0.75 T**, Q1468, on official source
   `5a7c3902`; it does **not** deliver the 101 T measured on B3. Its first
   census has 161 failed batches versus 159 for its fresh paired parent, so
   screening was not launched. Larger expression limits and additional exact
   public passes are being tested. See
   [wide-cache status](../experiments/wide-cache-20261015/STATUS.md).
   The original proposed recipe was: start from commit
   `7ff2ba53` (recreate it from its patch; see the tools table). Port the larger-expression cache (cache-retention 128/1,000,000,
   about −101 T, about +5 qubits; width is free for this record) into
   `src/point_add` as a final pass before the nonce tail. Then do these in order:
   1. Paired-census it against the official stream (same label) to confirm T
      and an unchanged failure rate.
   2. Freeze it and screen nonces from 1.
   3. Run `benchmark.sh` and write the report and note in the style of
      `nonce-screen-20261015`.

   The earlier expected result of about 753,670 T is **not supported by the
   measured direct transfer**. Also consider `mid2-smooth-anch2` (failure rate 4.18, but
   +4.7K T, so worse for T).
2. **Unblock the product record with a classical value-failure prefilter.**
   Model the leapfrog GCD walk (`src/point_add/leapfrog.rs`, steps table in
   `leapfrog_data/`) with the record's rail envelope. Use a fast secp256k1
   scalar multiplication (the evaluator's `curve.mul` is slow). Cost target:
   ≤ 10 µs per shot. Validate it on census failures: it must flag the tip's
   known failing inputs (the census jsonl stores k1/k2 per failing shot) with
   essentially no false passes. Run the exact screener only on prefilter
   survivors. It must not change which nonce the lowest-pass policy selects;
   the prefilter can only skip nonces that would fail anyway.
3. **Find exact width-free T savings of ≥ 12–15 T on `4b2ec52f`.** Only then
   is a product attempt worth its search: the fresh mean is 761,221.70
   against a threshold below 761,221.5, with a packet SD of 6.2.
4. **Win back failure rate cheaply** (each batch removed cuts the search
   about e-fold). The non-walk floor of about 1.1 batches is unlocalized;
   the payload-fold boundary work (`trace-audit-20261015/FOLD-BOUNDARY.md`) is
   the lead.

## 7. Pitfalls already hit

- **Git hygiene (user preference):** keep only the `main` branch, locally, on
  GitHub and in the server clone. Use detached worktrees for experiments,
  save each experiment's patch under `experiments/`, and remove the worktree
  when the experiment ends. The three submodules are pinned (detached, no
  branches) and fetch only upstream `main`. About 48 older detached
  worktrees from 14–15 October remain in the server clone (`git -C toffoli
  worktree list`); check for unsaved source edits before removing any.

- **Windows shell:** the Bash tool runs Git Bash. Long heredocs inside
  `ssh '...'` can fail to parse; write files with an editor tool and `scp` them.
  Server scripts must use LF line endings.
- **Background SSH:** `nohup ... &` inside `ssh` keeps the session open; use
  `(setsid nohup ./run.sh > log 2>&1 < /dev/null &)`.
- **Dirty submodules:** `agents/qubits` and `agents/toffoli` carry uncommitted
  edits from 14–15 October that are not ours to discard. Stage only the files
  you changed.
- **Poisson shortcut:** e^−λ underestimates search cost by about 3× at a
  failure rate of 18. Use (1 − f)^141.
- **Paired T noise:** paired census T differences have a batch SD of about
  80 T, because measurement-dependent cleanup diverges. Use all 4,096 batches
  and report the standard error.
- **Scored vs diagnostic:** census means and paired savings are diagnostic.
  Only a `benchmark.sh` pass or an official evaluation is a result.

## 8. Checklist for each experiment

Create `experiments/<name>-YYYYMMDD/` with a `STATUS.md` (result first; then
method, evidence, caveats and server paths) and the launchers. Keep an
`evidence/` folder with stream SHA-256s, protected-file hashes, logs (gzip
anything large), patches and census jsonl. Keep failed runs, clearly
labelled. Update `README.md` (only for scored or complete local passes),
`docs/research-plan.md` (newest entry on top), `docs/results-status.md` and
this page.
