# CPU server: ECDSA research handoff

**Public result update · 17 October, 12:36 Singapore.** MonitSharma now holds
the product record (939,223,314) and Toffoli record (753,694), with four current
Pareto points. See [official results and provenance](leaderboard-results.md).
The dated operational checkpoints below remain preserved; this documentation
refresh does not launch, stop, or change any server research.

## STOPPED: 16 October 2026, 09:07 Singapore

User requested stop/candidate review. No further launches or automatic resume.
Verified SIGSTOP groups:628797(product25, post-verifier642195),595517/595518/
595519/606954(ALL70chain/watchers),627572(PRESEED10),572494(ALL74). Unrelated
jobs untouched. Rootwide probe/fresh census and original product search are
terminal; affine query naturally exited before STOP. Product benchmark passed
Q1234/T761171/product939285014 before pause; final fresh census NOTRUN.
Read [stop checkpoint/process resume requirements](../experiments/autorun-20261015-2239/STOP-20261016-0907.md).
Do not blindly CONT timed jobs: elapsed wall deadlines need inspection first.

## Latest: 16 October 2026, 08:55 Singapore

The original48-thread product25 search ended cleanly at08:43. All four old
workers have exited; do not relaunch them. The08:53 terminal full-row audit
passes:lowest47,449,113, completeprefix47,452,160. Final source/benchmark now
belongs to product_savings in product25-final-20261016. Root's final census
will use the predeclared label/range with4workers/source after those gates.
Terminal receipt remains product25-operational-20261016/ROOT_TERMINAL_AUDIT.json.

08:53 preflight: LHC-104-070, approximately258GiB available; unrelated lattice
jobs untouched. Seed candidate census548566 uses4workers, ALL70/ALL74 chains
one core each, root current-parent4096 native one core. Plain67 cost pilot
is terminal and releases4cores. New PRESEED10 native build up to4cores then
one proof/generation core; resource check and dedicated nohup/PID/log/exits
remain mandatory. Do not change chemistry or frozen search/runtime artifacts.

## Active research:16 October2026,08:15Singapore

Original product25 four48-thread workers/PIDs3893465,3893466,3893468,3893469
unchanged, verified08:10:46 snapshot42,586,112 distinct rows/lower42,184,704,
no pass signal. Never audit active JSONL as terminal. Seed fixed32768/source
census parentPID427621/coordinator412785 uses4workers, then same candidate;
exact logs seed-restore-20261016/seed-fresh/{parent,candidate}.log. No resampling.

product-exact-20261015/all70-cache67-20261016 has complete native ALL70 base
06cdc5de/all17 protected files unchanged. Fresh fixed67 stage chain uses ONE
core/24GiB, cache-chain.log emits only universally admitted stage receipts.
Final native port uses at most2buildcores, then declared sole32768/source gate
with1worker/source. Prefilter all70-mask-feasibility-20261016 independently
queries the new base,1core/24GiB/all512outputs/cap32/900s; no old mask transfer.

Root wide15-retained4096-20261016 PID518734 is a separate source-only one-stage
probe on current official Toffoli source1d8c05ee,1core/64GiB/2700s. Preflight
228GiB minimum and own-only stop below110GiB. Not an oldwide95 changed-limit
retry. No census/nonce launched by this study. Leave all unrelated jobs alone.

Preparation profile and scalar-window studies are terminal; no production
changes. Old repaired67 source proposal stays disabled. A separate persistent
worker cost-only study may be prepared within spare8cores after mask query;
the user's affordability criterion is about1day on64threads, while the old
proposal imposed its own stricter8thread gate. No search authority from a
program-timer projection; distinguish measured amortization and64thread estimates.

Latest availability246GiB at mask launch, registeredresearch~56cores. Recheck
CPU/memory/processes before every launch. Latest pushed backup4f5b7ab.

## Active research:16 October2026,07:43Singapore

Original product25 four48-thread workers/PIDs3893465,3893466,3893468,3893469
remain unchanged. Verified07:44 snapshot has38,182,912 distinct rows, lower
prefix37,810,176/no pass. Never treat active JSONL as terminal evidence.

Both repaired67 disabled runtimes and the bounded8thread cost are TERMINAL.
Cost PID409263 exited0, all65536rows match, strict declared cost gateFAILS;
no second search. Eight timing cores released. Optional fused binaryab8cf13c
is frozen; no production change. Next profile may use at mosttwo isolated
cores, with its own source declaration/rows/startup and preparation timers.

Square4 census terminalPASS4175->4173, +16T/Q0; no workers remain. New frozen
seed-restore-20261016 census uses4workers sequential parent/candidate, label
public4b-all-seed-dropped-control-restore-independent-20261016-v1; parent
PID427621. Native/protected/hash-pinned prefix proofs PASS. Keep full32768
cohort unchanged; no subset, resampling, caches or nonce search. Failure
observer uses at mostone extra core on preserved431/413contexts.

Latest launch had262.90GiB available; recheck before every new job. Keep
research<=64threads and>=100GiB available, unrelated lattice jobs untouched.
Root latest remotely verified backup092b536a; current checkpoint awaits push.

## Active research:16 October2026,06:54Singapore

Current authoritative state is [AGENT_HANDOFF.md](AGENT_HANDOFF.md); the dated
sections below preserve older runs. Host LHC-104-070 has263GiB available in the
latest preflight. Leave unrelated two18-thread lattice jobs and all foreign
submission work untouched. ECDSA root is /home/hclau/ecdsa_research.

product25-operational-20261016 remains active with48threads across PIDs3893465,
3893466,3893468,3893469. No binary/source/library/affinity changes. The06:45:59
immutable checkpoint has28,557,312 complete distinct rows/no pass, lowerprefix
28,446,720. Do not apply terminal-log acceptance to active JSONL files.

repair67-conditional-filter-20261016 is a separate DISABLED validation,2build/
runtime threads,24GiB cap; continuation PID287229. Original prerequisite/build
failures are preserved before evaluation; same15prepared tool source files are
rechecked. No production authority or nonce search is granted by its theorem.
failure-census-20261015's square parent PID163483 uses4workers, then the frozen
candidate on the same sole32768batches. The failure agent owns its continuation.
N2-loan source-family diagnosis uses at mostoneadditional core. Product endpoint
and prefilter proof jobs are terminal; their full archives are verified locally.

No chemistry changes, external submissions, active-search restarts or resampling.

## Current work separation — 15 October 2026

**Start with [AGENT_HANDOFF.md](AGENT_HANDOFF.md)** for state, tools and next steps.

**Product-tip feasibility is terminal (22:00 Singapore):**
`/home/hclau/ecdsa_research/product-tip-20261015/` holds `tip/`, a detached
worktree of the public product record `4b2ec52f` (built; stream `2a522394…`),
the tip census (17.69 failed batches), a 256-nonce screener timing and the
width-free cache rewrite (`cache/32-200000.bin`, 2.2 ± 1.2 T saving). Launcher
`run-tip.sh` exited; no jobs remain. No search was started.
[Report](../experiments/product-tip-20261015/STATUS.md).

**Official submission complete, 19:19 Singapore:** the clean candidate
(commit `7ff2ba53`, formerly the `nonce-screen-20261015/candidate` worktree on
branch `research/toffoli-smooth-n375`) was uploaded as `3f32acd2`. On
15 October at night that worktree, its branch and `product-tip-20261015/tip`
were removed at the user's request. The source survives as
`nonce-screen-20261015/candidate-7ff2ba53.patch` (and in the repository
evidence), and the scored copy is `5a7c3902` upstream. The server clone now has
only `main`.
Official metrics match the local pass: **Q1464/T753,771/product 1,103,520,744**.
Official candidate source is `5a7c3902`. The rejection reason is only
`score did not improve current best`; this is the lowest publicly scored T,
with no product promotion. Preserve the frozen source, note, nonce 375 and
failure census. Do not resubmit it merely because the scalar product lost.
[Current result and saved receipts](../experiments/nonce-screen-20261015/STATUS.md).
The CLI is installed at `/home/hclau/.local/bin/ecdsafail` and authenticated.
The local `.env` is ignored; no credential belongs in source or handoff archives.

The entries below preserve earlier experiment checkpoints and their own source
versions. Their pending/failed descriptions do not override the official result.

**Equal-division cycle is terminal:**
`/home/hclau/ecdsa_research/equal-division-20261015/` has observer-b3 and fold-b3.
PIDs3199075/3201429 exited0;64 artifacts and two patches are locally verified.
Without wrapper flags, y=x reproduces the same non-unit division result. First
ordinary tick divergence is120; uniform forward fold57 doubles its error.
Exact integer analysis gives a negative fold representative−856, consistent
with both window-wrap outputs. Next instrument internal fold quotient/borrow
and derive an exact boundary repair. Payload1 andp−1 failures are also preserved.
No jobs remain here; keep unrelated census/sweep workloads untouched.
[Evidence](../experiments/equal-division-20261015/STATUS.md).

**Parallel Claude agent: walk-widening variants are terminal; next run staged.**
`/home/hclau/ecdsa_research/widen-walk-20261015/` holds five private wide-b3
copies, each with only the leapfrog steps table changed. All built, generated
and censused with exit 0. The first park-row attempt is archived in
`superseded-park/`, and the mis-fed `trace-mid2-smooth` is moved to `superseded/`
by `run-next.sh`. `run-next.sh` (smooth-only variant, then a trace of its own
failures with the fixed `prepare.py`) is uploaded locally but **not yet
launched**: the server was unreachable at 15 October ~17:00 Singapore.
[Widening](../experiments/widen-walk-20261015/STATUS.md).

**Parallel Claude agent: value-failure trace is terminal.**
`/home/hclau/ecdsa_research/trace-value-20261015/observer-b3` is a private
gate-inert observer copy of wide-b3. PID 3203337 exited 0, and its final stream
is byte-identical to `95e771ba`. It attributes 155 of 186 value failures to the
leapfrog walk rails, whose envelope was fitted with a 0.00077-per-walk drop
budget. [Trace](../experiments/trace-value-20261015/STATUS.md).

**Parallel Claude agent: census and guard sweep are terminal.**
`/home/hclau/ecdsa_research/failure-census-20261015/` holds the census and
replay tools (`target/release/failure_census`, `failure_replay`), plus results
for 29 streams. `/home/hclau/ecdsa_research/guard-sweep-20261015/` holds a
private copy of wide-b3 with a research-only `GUARD_SWEEP_OVR` hook, and 11
variants. PIDs 3156126, 3161513, 3163097 and 3192716 have all exited.
Neither directory touches other experiments' checkouts.

To gate a stream (about one minute):
`failure_census OPS LABEL 0 4096 16 out.jsonl`, then
`python3 analyze.py out.jsonl`. To replay failing scalars under 32 seeds, use
`failure_replay OPS inputs.tsv 32 16 out.jsonl`.
[Census](../experiments/failure-census-20261015/STATUS.md) ·
[sweep](../experiments/guard-sweep-20261015/STATUS.md).

**Zero-payload cycle is terminal:**
`/home/hclau/ecdsa_research/zero-payload-20261015/` holds control-b3, wrapped-b3
and observer-b3. PIDs3179293/3179294/3188447 exited0/101/0. Wrapped generation
and all fixed replays completed; its phase-witness runner aborted on wrong
point values. Helper phase proofs pass, but the integrated oracle returns a
non-unit value for y=x. The raw interface observer matches the protected
simulator and records a nonzero flag before release. All81 artifacts verified.
Next use a no-held-flag equal-input control, then locate first divergence.
No job remains here. Preserve the separate census and guard-sweep workflows.
[Evidence](../experiments/zero-payload-20261015/STATUS.md).

**Y15 carry-source cycle is terminal:**
`/home/hclau/ecdsa_research/y15-carry-source-20261015/` contains origin-b3 and
state-b3. PIDs3165882/3169457 exited0. The origin stream is byte-identical to
Y15-unseeded wide; the raw observer uses all Hmr/R random reads to disambiguate
reused wire IDs and validates the selected bit. Reverse tick1 needs borrow1,
opposite the forward witness. All57 artifacts are locally verified. No jobs
remain here. Next inspect actual arithmetic/seam contracts for the exact
zero-payload divide/multiply wrapper model; zero multiplier and rails remain
separate. Preserve all parents and the unrelated failure census.
[Evidence and design](../experiments/y15-carry-source-20261015/STATUS.md).

**Y15-unseeded cycle is terminal:**
`/home/hclau/ecdsa_research/y15-unseeded-20261015/` holds narrow-b3 and wide-b3.
PIDs3158520/3158521 exited0. Both preserve all earlier value-failure sets and
retain phase counterexamples; no resource score qualifies. All57 artifacts
and both patches are locally verified. Next source target: wide Hmr qubit135 /
bit1555 at operation9553940, measurement780824. Keep parent sources intact.
The separate `failure-census-20261015` process was active at preflight; inspect
its live status before resource allocation and do not alter its work.
[Evidence](../experiments/y15-unseeded-20261015/STATUS.md).

**Joint-carry cycle is terminal:**
`/home/hclau/ecdsa_research/joint-carry-20261015/` holds four isolated attempts.
PIDs3147702/3148110 exited1/101 during preparation/build;3150016 exited0 but its
intended measurement flip was misaligned and is explicitly invalidated.
Corrected PID3152831 exited0, verifies the selected measurement and agrees
with the protected simulator. Both generated raw streams are byte-identical.
Tick124's reconstructed carry is correct, while its comparison seed causes
the verified phase error. All83 artifacts are locally verified; no jobs in
this cycle remain active. Next test the uniform Y15 comparison-policy change.
[Evidence](../experiments/joint-carry-20261015/STATUS.md).

**Wide-phase observer is terminal:**
`/home/hclau/ecdsa_research/wide-phase-20261015/origin-b3` reproduces the wide
dynamic-pool stream byte for byte. PID3142012 exited0. The first launcher failed
on CRLF before workload execution and is preserved. All 35 evidence artifacts
are locally verified. The witness traces to division's Y21 top-cut carry cleanup;
next capture exact carry/compare operands. No jobs in these two newest cycles
remain active.
[Attribution and evidence](../experiments/wide-phase-20261015/STATUS.md).

**Dynamic-pool cycle is terminal:**
`/home/hclau/ecdsa_research/dynamic-pool-20261015/` contains control-b3 and
wide-b3. PIDs3135762/3135763 exited0. The repair retains ownership checks,
passes six tests and leaves the narrow stream byte-identical. The wide stream
builds and reduces diagnostic T, but fails values and phase; no score qualifies.
All55 artifacts and both source patches are locally verified. The next source
observer belongs in `wide-phase-20261015`; check its PID/status before relaunch.
[Evidence](../experiments/dynamic-pool-20261015/STATUS.md).

**Latest carry-frame cycle is terminal:**
`/home/hclau/ecdsa_research/carry-frame-20261015/` holds four isolated checkouts.
Origin3122971, state observer3126032 and unseeded candidate3128221 exited0.
The cap1536 control3130991 exited101 at `y42_alloc_set`'s free-wire-set invariant,
with no stream. All91 artifacts are locally verified. No job in this cycle
remains active. Preserve the failed allocator state; next distinguish fresh
returned qubits from a true leak before allowing the larger-width control.
[Terminal evidence](../experiments/carry-frame-20261015/STATUS.md).

**Latest phase-origin cycle is terminal:**
`/home/hclau/ecdsa_research/phase-origin-20261015/` holds origin-b3, terminal-b3
and frame-proof-b3. Source3114272, combined phase3116092, candidate3117084 and
proof3118818 all exited0. The origin stream matches its parent byte for byte.
The candidate enables exact terminal overflow cleanup at derived cap1283 but
retains a new phase witness, five rail errors and128 zero-multiplicand errors.
The primitive passes174760 finite cases and2732 all-measurement proofs. All71
artifacts are verified locally; no jobs from this cycle remain active.
[Evidence and next boundary repair](../experiments/phase-origin-20261015/STATUS.md).

**Latest integration cycle is terminal:**
`/home/hclau/ecdsa_research/repair-integration-20261015/` contains combined and
raw-observer checkouts. Integration3102572, corrected observer3107247,
fresh BDD3108109 and witness3110384 exited0. Observer3102573/3106434 exited101;
their sources and logs remain preserved. The first shared-target BDD invocation
reused the wrong binary and is invalidated; fresh isolated builds confirm a
single-measurement phase counterexample on the prior square-room stream.
Combined source passes independent256, with five old-packet rail errors and
128 zero-multiplicand failures. All 122 artifacts are locally verified. No job
from this cycle remains active; inspect resources before further launches.
[Evidence and next repair](../experiments/repair-integration-20261015/STATUS.md).

**Latest control/repair cycle is terminal:**
`/home/hclau/ecdsa_research/rail-control-20261015/` contains five isolated
checkouts. +3 interior margin and two extra rounds leave five old-packet
failures; square integration separately fixes all zero-slope values. All
independent256 checks pass; structured and phase failures block qualification.
Control 3086738, observer 3086739, square 3090482, expansion 3093742 and phase
audits 3098264/3100124 exited 0. The first phase runner 3096286 exited 101 at
compilation. Both successful phase-audit processes were mathematically
inconclusive (XOR term cap), not proofs. All 143 artifacts and source patches
are verified locally. No job in this directory remains active.
[Results and next actions](../experiments/rail-control-20261015/STATUS.md).

**Latest continuation is terminal:** rail-headroom diagnosis in
`/home/hclau/ecdsa_research/rail-margin-20261015/` finished. PID 3081279,
`run-room.sh`, exited 0. At diagnostic Q1267, the variant passes independent
256 and leaves 10 wrong values on the preserved 9024-input packet (previously
16); known15 leaves 11 and structured256 leaves 189. No score qualifies.
The first uniform variant, PID 3079263, exited 101: insufficient scratch at
forward tick 128; it produced no stream. All 38 artifacts and both patches are
verified locally. No job from these four latest experiment directories remains
active. Check process identities before any future workload action.
[Results and next control](../experiments/rail-margin-20261015/STATUS.md).

Complemented-cache and idle-cache continuations are terminal, both exit 0.
Complemented controls add no measured savings; larger expression retention on
idle wires regresses from 4.015625 to 3.0625 saved Toffolis per shot. Preserve
the simpler wider 101.109375-saving construction and the old narrow one.
[Complemented-cache evidence](../experiments/cache-polarity-20261015/STATUS.md) ·
[Idle-cache evidence](../experiments/cache-idle-20261015/STATUS.md).

The preceding symbolic-retention experiment is terminal, both exits 0.
At diagnostic Q1240 it saves 101.109375 executed Toffolis per shot in each
fixed packet, while preserving inherited failures. Its 39 archived artifacts
are verified locally; there is no scored result.
[Completed evidence](../experiments/cache-retention-20261015/STATUS.md).

**Latest user priority:** direct new work toward lower executed Toffolis and
lower Q × T. Defer width-only searches and Q692 submission engineering;
preserve existing evidence. This priority update does not establish live job
status or authorize stopping another chat's jobs. Historical width diagnostics
below are reference material for a later resumption.

The latest rail cycle in `/home/hclau/ecdsa_research/rail-repair-20261015/`
is terminal. Eight isolated source checkouts, seven launch outcomes, native
primitive proofs and complete fixed replays are preserved. The widened tick
109 passes its local arithmetic but exposes a tick-110 overflow; full source
remains incorrect. Use the supported dynamic-allocation baseline for broader
repair research, not the failed candidate as a qualified result.
[Rail report and terminal receipt](../experiments/rail-repair-20261015/REPORT.md).

The earlier Toffoli/product repair cycle in
`/home/hclau/ecdsa_research/arithmetic-repair-20261015/` is terminal. Its checked
scratch-order adapter integrates the finite B3 tick-104 borrow repair. The
ordinary unbound variant builds and passes 256 independent fixed inputs;
known packet/structured failures remain and there is no qualified score.
All source patches, failed builds, fixed-input comparisons and the local phase
proof are archived in [the repair report](../experiments/arithmetic-repair-20261015/REPORT.md).

The original Q692 local pass remains frozen. The separate submission-preparation
chat owns `/home/hclau/ecdsa_research/q692_readiness_20261015/`. Its normal v6
benchmark failed with 3 value, 2 phase-batch and 3 ancilla-batch failures;
subsequent diagnosis must use those same failing inputs. Do not alter that
chat's checkout or stop its jobs.

The product and Toffoli cycles in `product-focus-20261015/` and
`toffoli-readiness-20261015/` have finished. Their paired gate savings do not
qualify as records; their original jobs are terminal. Read
[the current result summary](results-status.md) before using older job-status
notes below. Always inspect live process identities before acting on saved PIDs.

**Terminal update, 15 October 2026, 06:12 Singapore:** bank-swap v2 completed
exit 0, all 9,024 shots passing, Q692/T1,481,382,858. The original queue and
evaluator are terminal. Read-only review rechecked the exact source, stream,
protected binary, failure channels and score. No duplicate evaluation is needed.
[Result, paths and limits](../experiments/followup-20261015/bankswap-terminal/RESULT.md).
The older pending-job descriptions below are historical snapshots.

**Completed ten-hour cycle with live calculation handoff:** [final report](overnight-final-report.md) and
[exact handoff receipt](../experiments/overnight-20261014/coordinator/final-handoff.json)
supersede the historical setup below. No original submission-ready improvement
has qualified. N275-v2 completed with value, phase and ancilla failures; N274-v4
has a known arithmetic counterexample. Preserve their streams and failed evidence.

Headflag-v1 native2662310 completed exit1 after all9,024 shots, with four
value failures, one phase-garbage batch and four ancilla-garbage batches.
Collector2740181 completed exit0, source/stream/protected-binary checks intact;
its receipt has no qualified score. Both PIDs are terminal.
HT25-v9 generation2785256 completed exit0 with a parser-admitted diagnostic
stream, no score. Bank-swap-v2 generation2802421 completed exit0 with a parser-admitted
692-reference-width stream. The guarded pipeline2805813 and native benchmark2812595 are active,
with no aggregate result; it never allocates the giant operation vector or
invokes a scorer. Its frozen source, exact log and collection commands are in
the final report. Missing exit markers mean pending. Check process identities
and markers, rather than assuming a recorded PID is live.

```bash
ssh smu_server
cd /home/hclau/ecdsa_research/overnight-20261014
python3 /home/hclau/ecdsa_research/server-preflight.py
ps -p 2805813,2812595 -o pid,etime,rss,%cpu,args
tail -30 qubits/evidence/headflag-v1-official-eval.log
cat coordinator-headflag-collection-watch-v1/run.exit
cat coordinator-headflag-v1-terminal/receipt.json
tail -30 qubits/evidence/ht25-v9-full-build.log
cat qubits/evidence/ht25-v9-full-build.exit
cat qubits/evidence/ht25-v9-parser-admission.json
```

The detached collector waits at most24hours. Wait for its exit before starting
manual collection. If it fails, preserve its log and diagnose the failure;
then `python3 collect-overnight-qubit-result.py headflag-v1` collects existing
terminal evidence without rerunning the evaluator. Collectionexit0 is not a
correctness pass: inspect all channels, full9024 admission, source/stream hashes
and score validity. Independent arithmetic failures remain an explicit limitation.

Before any further full evaluation, require exact final source and protected
harness bindings, native/phase checks, serializer equality, full stream hash,
parser count≤4billion and refreshed sufficient available memory. Hold the
sole-large-job lock and wait for the existing giant evaluator to terminate.
Generation and component passes are not scores. Do not kill useful jobs at the
end of the reporting window or repeat a completed benchmark.

Guarded bank-only queue2805813 has passed generation and admits exactly one
unchanged full benchmark only if source/native/phase/parser/width and refreshed
memory guards pass. It holds the shared sole-large-job lock at allocation.
Read `qubits/evidence/ht25-bankswap-v2-official-cycle.log/.exit`, the eventual
`official-eval-native.pid`, and `official-terminal-receipt.json`. During the
wait there is no benchmark PID or result. Nativepass still requires score and
all9,024 failure-channel review; no automatic record claim is made.

## Historical setup

Verified on 14 October 2026 via SSH alias **`smu_server`**. Hostname:
`LHC-104-070`. ECDSA work is isolated at **`/home/hclau/ecdsa_research`**.
The pre-existing `/home/hclau/quantum_chemistry` checkout and active jobs were
inspected and left untouched.

Guarded bank-only queue2805813 has passed generation and admits exactly one
unchanged full benchmark only if source/native/phase/parser/width and refreshed
memory guards pass. It holds the shared sole-large-job lock at allocation.
Read `qubits/evidence/ht25-bankswap-v2-official-cycle.log/.exit`, the eventual
`official-eval-native.pid`, and `official-terminal-receipt.json`. During the
wait there is no benchmark PID or result. Nativepass still requires score and
all9,024 failure-channel review; no automatic record claim is made.

## Historical setup capacity and limits

Observed: 144 logical CPUs, 503 GiB RAM, approximately 277 GiB available, 4.7 TiB
free disk, and load around 35–36. Two active jobs each use about 18 CPU threads
and together roughly 210 GiB RAM. Neither Slurm's `squeue` nor `qstat` was found.
These are observations, not permanent reservations; refresh before each launch.

Use four build threads initially and one numerical-library thread. The product
baseline's full benchmark peaked at about **4.03 GiB RSS** under a 16 GiB process
virtual-memory limit. The Q693 stream has 1,128,700,062 operations; its 56-byte
vector alone is approximately **58.9 GiB**, before copies and builder overhead.
Use one low-width full benchmark at a time, plan conservatively for 128 GiB and
measure actual memory. The official scorer is sequential across its batches.

## Installed and reproduced

- Rust **1.93.0**, installed alongside the pre-existing stable toolchain.
- GCC and Python **3.12.3**; isolated `.venv` with Z3 **5.1.0.0**.
- Independent public worktrees: `product` (`c5bb1ec8`), `toffoli` (`b3c9fdd6`),
  `qubits` (`c95b9325`), sharing the `upstream` Git repository.
- Unchanged product benchmark: **Q1234/T761,658/product939,885,972**, all 9,024
  shots passing, stream SHA256
  `49b35cf7640ebd529d76894eb8bef93ebf57e7e970fe14b3c27c8c5feb6e73e4`.
- Public Q693 focused K24 suite: 14 passing tests, one existing ignored test,
  before adding the new experiment.

That reproduced product base is now historical: the refreshed public leader is
`143731ef`, Q1234/T761,492/product939,681,128. The server worktree remains on the
reproduced c5bb1ec8 source until a deliberate, separately verified rebase.

The server lacks bubblewrap. The unchanged benchmark used its documented local
development fallback; this replay is not an official platform evaluation.
Evidence: [verification receipt](data/server-verification.json). Full logs are
under `research-output/server-20261014/` locally and `logs/` on the server.

## Inspect and resume

```bash
ssh smu_server
cd /home/hclau/ecdsa_research
python3 server-preflight.py
cat logs/product-baseline.exit
cat logs/product-baseline-score.json
tail -30 logs/compact-fixed.log
```

Each long job runs with `nohup`, a dedicated log and a recorded PID. Check both
the process and exit marker; a stale PID alone does not establish a live job.
At the 14 October 2026 17:31 Singapore inspection, the parent job was PID
2277715 and trusted scorer PID2283149. Both were detached from a terminal and
ignored SIGHUP; the scorer used about 59 GiB RSS and one CPU core. It was executing
the unchanged `eval_circuit` over 9,024 shots. It exposes no reliable batch
progress or completion estimate. Check the receipt for the latest observation.
The setup, baseline and compact-candidate jobs are complete. The compact
candidate's build succeeded but full validation **failed** after all 9,024 shots:
6 classical mismatches, 3 phase-garbage batches and 6 ancilla-garbage batches.
Exit status is 1; no valid score was produced. The first mismatch was shot 1170.
The full benchmark took 38:17.50 and peaked at about 59.7 GiB RSS. Its job
processes have exited; no ECDSA calculation is currently running.
The 203-column integration fixture passed with a 64 GiB allocation allowance
(19.2 GiB measured RSS), which is narrower evidence than this failing full run.
New experimental jobs and outcomes are documented in
[the research plan](research-plan.md) and [receipt](data/qubit-experiment.json).
The terminal log, exit marker and stream hash are preserved. The
`ECDSA benchmark follow-up` automation is paused after collecting the result.
The next calculation should diagnose the failed packet against the unchanged
base; do not rerun or submit the current failed candidate as a validated result.

For a new fully prepared candidate, use the unchanged track benchmark after
inspecting jobs, available memory, source revision and working-tree status:

```bash
cd /home/hclau/ecdsa_research/qubits
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH
mkdir -p ../logs
nohup /usr/bin/time -v bash ./benchmark.sh --note "Exact verified candidate" \
  > ../logs/qubits-candidate.log 2>&1 < /dev/null &
echo $! > ../logs/qubits-candidate.pid
```

Do not run another full stream job concurrently or overwrite existing evidence.
An integrated candidate must preserve all quotient owners, delayed-crossing pad
lanes, seven crossing-reserve lanes, precision and measurement phase semantics.
An isolated fixture is not a record.

## Transfer and preservation

The obsolete Mac shared-clone relocation procedure is archived at
`docs/archive/server-handoff-mac-20261014.md`. Fresh recovery uses pinned public
submodules, plus tracked experiment patches. To transfer this working tree and
ignored evidence, use `scripts/create-handoff.py`; runtimes and build caches are
excluded. Research patches, raw logs, stream hashes and compact receipts must
travel with the source. Shell scripts are normalized to canonical LF in the
archive; manifest hashes describe those archived bytes. The source working tree
is not rewritten. Recreate runtimes on the destination.
