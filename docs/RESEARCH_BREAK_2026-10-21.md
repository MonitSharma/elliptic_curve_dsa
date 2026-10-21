# Research break and next-agent handoff — 21 October 2026

**Status: PAUSED at the human's explicit request. Do not start experiments,
resume jobs, screen nonces, submit candidates or push changes automatically.**
The human requested a break and documentation of what worked and failed.
Resume only after a subsequent human instruction. The global product objective
is unfinished; it has not been declared achieved. No scheduled automation exists.

This is the current entry point. Earlier dated sections elsewhere are history;
their ACTIVE, pending-submission and running-job descriptions are superseded here.
Machine state: [CURRENT-ACTIVE.json](../experiments/autorun-20261020-breakthrough/CURRENT-ACTIVE.json).
Chronological work: [LOG.md](../experiments/autorun-20261020-breakthrough/LOG.md).
Local checkpoint before this break: `6369e69cead4e2e3123fd718969646412a852121`.
The break itself is saved in a later local commit; inspect `git log -1`.
Only root commit `41f769ec44e40c915c3149d8332c15b10bca71f8` was explicitly
approved and pushed previously. That approval is already fulfilled. Newer
commits remain local; do not treat it as permission to push a later HEAD.

## Official results and public comparisons

Latest read-only public refresh: **2026-10-21 03:50:56 UTC**, 1,719 submissions.
See [snapshot](../experiments/breakthrough-assessment-20261020/snapshots/20261021T035054Z/)
and [refresh script](../experiments/breakthrough-assessment-20261020/refresh.py).
Refresh again after a future human resume and before comparisons/submissions.

| Independent objective | Public best at refresh | Submission / source |
|---|---:|---|
| Executed Toffolis | **Q1464, T746089, product1092274296** | Our [8d704a6b](https://api.ecdsa.fail/api/submissions/8d704a6b-659c-4d67-9bd0-f6862de9f617), source `ba04b1bd550e34351273331ddd886fb03328b3dc` |
| Product | **Q1234, T755314, product932057476** | [1829986e](https://api.ecdsa.fail/api/submissions/1829986e-675c-4fbf-bb28-22f2f95246c4), source `3eefcf216ca37cba0ae3f56212d6b1302844a249` |
| Peak qubits | **Q669, T585844476** | [1df8adee](https://api.ecdsa.fail/api/submissions/1df8adee-0c79-4278-b225-7d3bf3076326), source `4c1c31407892ef4bfaae3fe0a0ac25bae06132c2` |

The Toffoli submissions below were officially reproduced, but their API status
is `rejected` solely because **“score did not improve current best”**: the
challenge promotes product improvements. They are verified independent
Toffoli improvements, not new global product records. Attribution is
**GPT-6 sol / Codex**. Do not submit either again.

| Submission | Complete unchanged benchmark and official metrics | Provenance |
|---|---|---|
| [cb2253eb](https://api.ecdsa.fail/api/submissions/cb2253eb-7318-416b-8c9e-af9a28bda867) | **Q1467/T746099**, all9024 shots PASS; totalT6732798936, mean746099.1728723404 | [final evidence](../experiments/breakthrough-recycle-final-20261021/), local source `6cbb689761d26b2f63399e73b0703efc74351ec2`, public `90c5d46f8394eb584ab15b6d0bc2969a66f86b17` |
| [8d704a6b](https://api.ecdsa.fail/api/submissions/8d704a6b-659c-4d67-9bd0-f6862de9f617) | **Q1464/T746089**, all9024 shots PASS; totalT6732706015, mean746088.8757757092 | [final evidence](../experiments/breakthrough-borrowed-recycle-final-20261021/), local source `5d3383c9242c801c18c0faccfdbe84e16959e6b4`, public `ba04b1bd550e34351273331ddd886fb03328b3dc` |

Both published commits were independently checked against **all207 selected
source files and17 protected files**, byte for byte. `CREATED-PR-URLS.json`
is empty for both; there is no new PR to attach. Preserve older Q692 evidence.

### What produced those improvements

The three-cache candidate preserves the original measurement count/order and
reuses three original zero-effect measurements to discharge cached products,
with exact saved-guard phase repair. It adds3 quantum wires. Its own final
gate `ffe20-exact-measurement-recycle-final-20261021-v1`,32768 batches×64/source,
against exact FFE20 passed: value1116 each, failed batches1147 each,
4.935516357421875/packet, dirty0, paired b=c=0,p=1, exactTdelta−3/SE0.
Lowest nonce1127;1152 production screens, only pass1127. Eight partial controls
1..8 and24 full-state control batches were separately disclosed and repeated
in production. Selected complete9024-shot replay and unchanged benchmark PASS.
Final stream SHA256:
`17f8932644fb5ebf1122a9b5240ff675fd830fc7516f82e667608850c93085a8`.

The stronger candidate caches **13 exact products on original zero wires**.
Every donor is independently proved zero before its first use, has no original
quantum read/write/phase touch during the inclusive loan, and has no overlapping
occupancy. The final target equals the cached product; two CNOTs transfer the
value and restore the donor. No additional quantum wire or measurement is used.
Native21/local–official Rust generation match. Its **own new final gate against
newly official cb2253**, `cb2253-borrowed13-final-20261021-v1`,32768×64/source,
passed: value1151 each, failed batches1166 each,5.01727294921875/packet,
dirty0,b=c=0,p=1, exactTdelta−10/SE0. This gate is not reused from FFE20.
Lowest nonce142;192 ascending production screens, passes142/147, choose142.
Extra8 partial controls/24 full-state batches disclosed. Final stream SHA256:
`e3a9c27c052ee6b6fd93f32906d8567b2cd5346cc16f1508488ce20767421a1b`.

All149 cb evidence archive members and all159 borrowed evidence members were
independently verified locally. Nested files are hydrated, with deterministic
gzip copies of large JSONL. See each `LOCAL-VERIFICATION.json`,
`LOCAL-NONCE-SOURCE-VERIFICATION.json`, `NESTED-HYDRATION.json` and
`PUBLIC-SOURCE-VERIFICATION.json`. Large `final-evidence.tar.gz` files remain
on disk/server and are deliberately excluded from root Git; individual source
archives and evidence are preserved. The sealed cb `FINAL-VERIFICATION.scope`
contains an old “currentde8” template typo; retain it. Its actual gate, source,
dependency hashes and submission note correctly bind FFE20. Do not alter sealed
evidence to hide this historical typo.

## Jobs paused for this break

All local research jobs finished with exit0 before the break. **Two owned
server process trees were suspended using SIGSTOP at04:09:08 UTC**; their
verified state is `T`, not terminated. No automatic restart is configured.
Unrelated chemistry and other users' processes were not touched.

Authoritative [pause receipt](../experiments/research-break-20261021/SERVER-PAUSE.json)
includes each PID's `/proc` start ticks, command, working directory and UID.
Server copy: `/home/hclau/ecdsa_research/RESEARCH-BREAK-20261021-PAUSE.json`.

| Job | Paused processes | Exact state |
|---|---|---|
| Own-gated public semantic nonce search | controller3278347, engine3279048 | 173072 complete unique rows; **complete prefix1..173056**; highest173160; no passes. More rows above the complete prefix are retained; do not mistake highest for contiguous coverage. Original limit1..16777216,16workers,128nonce windows unchanged. |
| Predeclared15-mode exact carry grid | controller3367997, timeout3376539, builder3376540 | Public mode complete and byte exact; cap1234-t21 complete and matches prior local output. Paused during cap1233-r012 generation. Remaining modes not executed yet. |

**Only after human resume:** recheck hostname, branch/status, CPU/memory/jobs,
then verify **every PID's current start ticks and script/cwd** against the
receipt before sending SIGCONT. Never trust a reused PID or signal an entire
unverified process group. Search controller cwd is `/home/hclau`, but its exact
argv is `python3 -u /home/hclau/ecdsa_research/breakthrough-public-semantic-nonce-20261021/run.py`;
this identity was checked before suspension. The engine cwd is its experiment.

**Grid timeout caveat:** GNU timeout uses real elapsed time. Its alarm may be
pending after a long break and may expire immediately on resume. Preserve that
generation interruption/failure; the existing controller records it and can
continue the fixed remaining grid. If reproducing the interrupted mode later,
use separate evidence and the same frozen source, preserving the first failure.
This is generation research, not a statistical gate. Do not erase logs or
pretend the interrupted mode completed. If processes disappeared after a reboot,
do not rerun the nonce controller blindly: qualify an explicit continuation
against all retained rows and its original policy, without duplicates or a
changed search cap. No such restart procedure was implemented in this turn.

Search snapshot raw bytes72296239, SHA256
`b083dcc549cc89278a007c1e294c84ecabbf8d75beddf0b3dbb65c8f042785dc`;
no partial JSON tail. Raw remains on server; exact deterministic gzip is local.
The67-member server break archive was independently hash verified and hydrated.
Archive SHA256 `2ce2b0c1c5fd5b56da37e5316d929924336f661e60a24865e1efb5503f97cc26`.
See [local verification](../experiments/research-break-20261021/LOCAL-EVIDENCE-VERIFICATION.json).

## Research ledger: what worked and what did not

All entries below are **component, diagnostic or verifier work**, except the
two official submissions above. A generated gate count or proxy is never a
complete benchmark score. Every source, source freeze, native test log, run log,
failure and result lives in the linked experiment. Preparation/launch helpers
are under `experiments/autorun-20261020-breakthrough/`.

| Experiment directory under `experiments/` | Outcome and qualification | Interpretation / next use |
|---|---|---|
| `breakthrough-global-product-inventory-20261021` | Native5;59 public repeated exact-product pairs,13 FFE pairs, zero triples | Complete effective guard is part of the product proof. Expression IDs are local, never reusable as proofs in another graph. |
| `breakthrough-raw-product-inventory-20261021` | Native6;150 public raw-product groups:100 pairs/50triples/377occurrences;13FFE pairs | Read-only nominations exclude guards; not eligible rewrites without a new guarded proof. |
| `breakthrough-recycle-zero-measurements-20261021` | Compile failure: report helper used after move | Preserved; no native generation/gate. |
| `breakthrough-recycle-zero-measurements-v2-20261021` | Native11; whole-stream adapter allocated old qubit count | Qualification adapter failure, not a gate verdict. |
| `breakthrough-recycle-zero-measurements-v3-20261021` | Native11/full48 protected comparisons PASS;12 public/3FFE leases | Exact original measurement reuse works, but standalone extra width is not a product record. |
| `breakthrough-recycle-zero-measurements-v4-20261021` | Native12/full48 PASS; original-wire phase-Z alias adds0 leases | Useful tested rule, no added gain. |
| `breakthrough-recycle-zero-measurements-v5-20261021` | Native14/full48 PASS;59 public/13FFE unitary cleanups, all immediately after final target | Enables original-wire cleanup; extra-wire version alone has no product gain. |
| `breakthrough-recycle-finished-20261021` | Compile failure from unneeded report/serde helper | Preserved before any gate. |
| `breakthrough-recycle-finished-v2-20261021` | Native14, official byte match, own gate PASS | Successful three-cache official cb lineage. Initial local test selector chose0 tests and correctly stopped; corrected runner selected14 on the same frozen source. Both logs preserved. |
| `breakthrough-recycle-unitary-finished-20261021` | Native17, local/official generation PASS, Q1477 | Wider13-pair control retired before gate after Q1464 donor version succeeded. No nonce or benchmark on this control. |
| `breakthrough-borrowed-recycle-20261021` | Native18/full48 PASS; public0/59 donors, FFE13/13 | Successful zero-width donor rule; led to official8d704a6b. |
| `breakthrough-borrowed-recycle-finished-20261021` | Native21/crosscompiler stream exact; own gate and final benchmark PASS | Finished source for official8d, source207/protected17. Development, final gate, nonce and final evidence are separate sibling directories. |
| `breakthrough-conditional-borrowed-recycle-20261021` | Native21/full48 PASS; public0,FFE13 | Baseline XOR cache with disjoint guarded touches is valid; no additional donors/gain. |
| `breakthrough-future-target-recycle-20261021` | Native18/full48 PASS; public0,FFE10 | Early transfer into untouched future target works but offers fewer savings than13 donors. Same Q/T combination must not be created merely to reroll a nonce. |
| `breakthrough-moving-recycle-20261021` | Native18/full48 PASS;0 eligible both parents | Greedy first-free moving zero donors gain nothing. Complete provisional loan rollback is tested. |
| `breakthrough-moving-recycle-v2-20261021` | Native18/full48 PASS;0 eligible both | Farthest-next-touch choice also gains nothing. |
| `breakthrough-implicit-classical-guards-20261021` | Native10/full48 PASS, completed exit0,0 additional guards | V1 eventually finished; its bounded cache was slow, not a remaining job. |
| `breakthrough-implicit-classical-guards-v2-20261021` | Native10/full48 PASS,0 additional guards | Cache-flush/current-classical-factor priority improves runtime; no circuit gain. |
| `breakthrough-compact-context-alias-20261021` | Native15/full48 PASS; Q1233:1CCX→CX+2zero CCX; Q1234:4CCX→CX+1zero | Fresh exact prefix proofs on cached compact streams; small component gain only. |
| `breakthrough-reset-reference-inventory-20261021` | Native18; public1 post-target reference, compact1233/1234/FFE0 | Read-only proposal to replace a CCX with HMR+phase repair+reference copy. No emitter was implemented and no savings claimed. |
| `breakthrough-compact-generic-repeat-20261021` | Native10; repeated inherited passes complete, small further reductions | Diagnostic proxies Q1233:754678,Q1234:753974.5. No new gate/benchmark. mabsorb and zero-force found0 on these inputs; do not claim arbitrary original-RNG equivalence from generic wrapper alone. |
| `breakthrough-current-cap11-20261021` | Native14/full144 PASS, both inputs | Independent original512-row control9 equals expanded2048-row compat9. Cap11 equals control9 on both whole streams: **no extra gain**. Earlier cap11 no-gain on a different old source also remains preserved. |
| `breakthrough-associative-prefix-20261021` | Native19/full96 PASS; compact1233:1CCX→CX, compact1234:0, public:0, oldFFE:1CCX→CX+1CCX→X | Exact bounded AND/XOR associativity over8 terms/literals,64visits,500k full-key cache flush. Overflow retains original expressions. FFE component removes2 native Toffolis, proxy2; not yet applied to current8d finished source, not gated or scored. Public normalization loses the old single alias proof; no public gain. |
| `breakthrough-current-compact-grid-20261021` | Native9 PASS; official1.93 public control exact and cap1234-t21 exact |15 modes predeclared before generation/inputs; now PAUSED. No fresh point development/gate/nonce on new modes. |

Finished sources, gates, nonce and final records also have their own sibling
directories. Never infer final eligibility from a component PASS. Earlier
automatic review rejected premature queuing before a candidate had its own
gate PASS; this was resolved using the actual completed gate and local evidence
verification. Both official uploads are complete; no permission request remains.

## The unfinished product candidate and an important estimate correction

Current public port source is frozen in
`breakthrough-public1829-width-port-local-v4-20261020`. Only three modes were
previously generated there. The current server grid reuses **unchanged source**
and expands its already supported exact resource layouts. Old bound tables are
omitted for changed constructors; generic passes independently rederive proofs.
No old table is transported by suppressing a stream hash guard.

Fresh context caches in `breakthrough-public1829-context-audit-20261020`:
115 leases/Q1234,114 leases/Q1233. The old development comparison
`breakthrough-public1829-local-development-v2-20261020` **already used these
cached streams** (confirmed by PLAN and REPLAY-FREEZE hashes). Its512×64 samples:
parent mean755308.7080, cached Q1234 mean755341.0235, cached Q1233 mean756053.1765,
paired Q1233 delta+744.4685/SE4.5679. Values match parent on all sampled outputs;
phase differences are retained; no dirty shots. This is development, not a gate.

**Do not subtract114 cached Toffolis a second time.** An earlier working summary
misread this comparison as uncached and understated the remaining gap.
Q1233 must have rounded T≤755926 to beat932057476 (ratio755926.5823).
The measured cached candidate is about127T above that allowance on its old
development sample, before the few new simplifications. It is not yet a verified
product improvement. Differences between labels/rounding also require margin.

Old `breakthrough-public-best-drop-finished-20261020` stream61927788 has its final
gate and exhausted1..65536 search preserved. It is **retired**. Never resume,
extend or re-judge it. Its old proxy was not its executed mean. The currently
paused semantic search is a different own-gated finished circuit, not that trial.

### Next research options, only after the human resumes

1. Inspect/resume paused jobs safely and collect their results. Preserve all
  15 grid modes and failures, then apply fresh cache proofs to promising exact
  layouts. Use real development counts, not the guard-depth proxy.
2. Consider applying the new associative-prefix rule to the **current official
  T stream**, with new source qualification. The old FFE2-native reduction is
  component evidence only; it does not establish a new finished8d improvement.
3. An **unimplemented** idea discussed immediately before the break: combine
  `CCX(a,b,t); ...; CCX(a,c,t)` into a guarded CNOT–CCX–CNOT sandwich at the later
  site, removing the first gate. Require the same captured effective guard,
  unchanged earlier controls and no intervening target reads/writes/phase.
  An analogous two-CCZ factorization may use a shared operand pair and unchanged
  phase operands. Prove commutation, guard snapshots, restore every temporary
  CNOT, prevent overlapping/reused plans, test faults and full absolute phase.
  **No code, inventory, tests or result exists for this idea.**
4. Moving-donor compression/rank profiles remain unimplemented. Opaque AND terms
  treated as independent give an upper rank bound, never proof of independence.
  Do not present a rematerialization plan as an emitted width record.

## Non-negotiable protocol and environment

Read root `AGENTS.md`, README, research plan and `docs/AUTONOMOUS_PROMPT.md`.
The explicit break overrides unattended-run instructions until human resume.
User previously authorized automatic official submission of any **complete
verified strict improvement** and requested GPT-6 sol/Codex attribution.
Keep Q,T,product objectives independent; preserve Q692 and all historical evidence.

Submissions may alter **only `src/point_add/`**. Preserve17 protected files,
Cargo/toolchain/harness/scorer/simulator/curve and historical result files.
Fresh final gate: declare one label and≥32768×64/source before running, compare
exact current public parent on paired fresh inputs. Candidate value failures≤
parent, one-sided exact McNemar p≥.05,≤18 failed batches/9024-shot packet, dirty0.
Verdict final: no relabel, resample, extend or later re-judgment. Product25 remains
ineligible. Only finished frozen own-PASS sources may screen identity nonces;
ascending from1, lowest pass, disclose all controls/screens/overrun, never choose
by T or tune tables/cuts to a packet. Run unchanged9024-shot benchmark, restore
historical results, verify source/evidence hashes locally, refresh records, then
officially submit only a strict current independent record improvement.

Server: SSH alias `smu_server`, hostname `LHC-104-070`, workspace
`/home/hclau/ecdsa_research`; chemistry stays separate and untouched. Check CPU,
available memory, scheduler, jobs, branch/status before workload changes.
Use nohup/dedicated log/PID for long work, default build4/library1,≤64 own
threads,≥100GiB available. Last preflight had~180GiB available/144CPU.
Unrelated heavy chemistry PIDs2204577/2202397 must never be stopped.
Server lacks `rg`; use its available equivalent. Base `toffoli` checkout is
detached atb3c9fdd6 and clean. Exact public reproduction is under **parent/**,
not candidate/: `breakthrough-public1829-reproduction-20261020/parent/ops.bin`.

Windows root: `C:\Users\monitsharma\Downloads\elliptic_curve_dsa`.
Python `.venv-research/Scripts/python.exe`, set `PYTHONUTF8=1`.
Local WSL Ubuntu uses direct
`/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo` (Rust1.99),
not `/root/.cargo/bin/cargo` (proxy would download1.93). Server official cargo:
`/home/hclau/.cargo/bin/cargo +1.93.0`. Shared local protected dependencies and
target are under `breakthrough-value-guard-fusion-audit-20261020/`; never modify
protected sources or overwrite an active shared binary. All local jobs are now
complete. New tool source archives are saved and rehashed before checkpoint.

Preserve pre-existing user changes in README/docs/data/figures and nested
`agents/qubits` / `agents/toffoli`. Root commits do not preserve nested working
files; keep diffs under experiments. Stage only owned evidence and documentation
prefixes, not user plots/data or whole submodules. Prefix staging uses HEAD base
plus new text while preserving the user's working suffix. Large raw ops, build
targets, candidates and final evidence archives are deliberately excluded.
For many paths use Git NUL stdin pathspecs to avoid Windows command-line limits.
No new subagents, user-owned threads, automation or PR were created this cycle.
