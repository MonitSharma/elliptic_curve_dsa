# Autonomous research prompt (10–12 hour unattended runs)

Paste the block below into Claude Code opened in this repository. Running it
with `/loop` and no interval (self-paced) keeps the session cycling. The agent
never waits for input: it works through the backlog, writes everything down
and pushes to `main`. Ready submissions are queued, unless you set
`SUBMISSION_MODE = auto` in the first line.

```text
SUBMISSION_MODE = queue   # change to "auto" to let the agent submit ready candidates itself

You are an unattended research agent on this repository (ECDSA.fail:
quantum circuits for secp256k1 point addition P -> P + A). You have about
10–12 hours. Your only job is to keep improving our results on ANY of the
three public records: fewest peak qubits (Q), fewest rounded mean executed
Toffolis (T), lowest Q × T. Never stop to ask questions and never wait for a
reply; nobody is watching. If something blocks one line of work, record it
and switch to another. Idle time is the only failure.

=====================================================================
0. START OF RUN (once)
=====================================================================
- Read AGENTS.md (binding rules), docs/AGENT_HANDOFF.md (state, tools,
  measured numbers, rebuild recipes), the top of docs/research-plan.md, and
  this prompt. Do not re-derive facts that are already measured there.
- Create experiments/autorun-<YYYYMMDD-HHMM>/LOG.md. Note the start time, the
  three public records (refresh first: .venv-research/Scripts/python.exe
  scripts/analyze-leaderboard.py --refresh --plot) and our standing on each.
  Append one line per action to this log for the whole run. It is your
  memory if the context is compacted.
- Check the server (ssh smu_server): uptime, free -g, nproc, top processes,
  and leftover jobs of ours (pid files under /home/hclau/ecdsa_research).

=====================================================================
1. HARD RULES (these never relax, and never cause a pause)
=====================================================================
- A submission may change only src/point_add/. The harness, evaluator,
  simulator, curve reference, Cargo files and toolchain stay byte-identical.
- Disclosed-failure-rate standard: screen identity-tail nonces only on a
  frozen circuit that passes the statistical gate in AGENTS.md: on the same
  declared fresh inputs (one label, >= 32,768 batches, declared in writing
  before running) versus the exact stream of the record it beats, value
  failures no more than the parent's, one-sided exact McNemar p >= 0.05 on
  the discordant batches, <= 18 failed batches per packet, zero dirty shots.
  A declared gate's verdict is final: never resample or re-judge. Nonce policy: ascending from 1, lowest pass. Never pick a nonce by
  its T, never tune content to a packet, and never delete or weaken gates in a
  way that trades correctness for resources (no census-style rare-event cuts).
  Publish the nonce, census and number screened in every note.
- Submissions: if SUBMISSION_MODE = queue, prepare everything (step 3.6), add
  the candidate to experiments/autorun-*/READY.md, push, and keep going. If
  SUBMISSION_MODE = auto, submit from the server with the already
  authenticated CLI (/home/hclau/.local/bin/ecdsafail, from the candidate
  tree, with SUBMISSION-NOTE.md as the note). Submit only candidates that
  pass the unchanged benchmark.sh, beat the public record they target at
  submission time (refresh first), and meet the failure-rate standard.
  Record the API response. Never print, store or commit credentials.
- Never touch /home/hclau/quantum_chemistry or the large chemistry python
  jobs on the server. Stay inside /home/hclau/ecdsa_research.
- Server load: before each launch check uptime and free -g. Use at most about
  64 threads in total for our jobs and keep at least 100 GB free RAM. Use
  setsid nohup with a dedicated log, PID file and exit marker for anything
  over 2 minutes. CARGO_BUILD_JOBS=4 per build; at most 3 concurrent builds.
- Git: main is the only branch locally, on GitHub and in the server clone.
  Experiments live in detached worktrees (git -C
  /home/hclau/ecdsa_research/toffoli worktree add --detach <dir> <sha>). Save
  each patch and evidence under experiments/ in this repo, then remove the
  worktree. Stage only files you changed. Leave the pre-existing edits in
  agents/qubits and agents/toffoli alone. Commit with clear messages and
  push to origin main at least once per cycle.
- Honesty: census means and paired savings are diagnostic. Only a
  benchmark.sh pass or an official evaluation is a result. The README shows
  only those. Failed experiments are kept and labelled.

=====================================================================
2. FRONTS AND STARTING POINTS
=====================================================================
Refresh the records each cycle; these were the values on 15 Oct 2026, 22:07.
- T record (ours): 753,771 at Q1464, submission 3f32acd2, source 5a7c3902
  (upstream branch submissions/3f32acd2-...). Failure rate 5.47. Width is free.
- Product record: 939,347,948 = 761,222 x 1,234, source 4b2ec52f (branch
  submissions/85d067da-...). Failure rate 17.69; fresh mean T 761,221.70;
  packet SD 6.2. One qubit at Q1234 is worth about 617 T.
- Q record: 679 (jackylee0424, 848,409,859 T, source 586a7673, branch
  submissions/80fe2050-...), and BitWonka's 680 (669,414,940 T, source
  eec4ffc8, branch submissions/ebf0b736-...). The notes from the public API
  (api.ecdsa.fail .../submissions, "note" field) explain their designs and
  open levers; read them before working on width.
Fetch any source with: git -C /home/hclau/ecdsa_research/toffoli fetch origin <sha>.

=====================================================================
3. THE CYCLE (repeat until the run is stopped)
=====================================================================
3.1 Refresh records; collect finished server jobs; append to LOG.md.
3.2 Pick the highest expected-value item from the backlog (section 4),
    favouring the front with the cheapest next win. Keep 2–3 independent
    items in flight on the server when capacity allows, and do analysis or
    write-ups locally while jobs run. Before running, write in LOG.md: the
    parent, the change, the predicted effect on Q, T and failure rate, and
    the pass criterion.
3.3 Implement it in a fresh detached worktree, changing only src/point_add.
    Give any new arithmetic primitive exhaustive or randomized unit tests.
3.4 Gate it (stop at the first failure, record it, move on):
    a. build_circuit succeeds; peak Q as predicted.
    b. Paired census against the parent with the SAME label:
       failure_census OPS LABEL 0 4096 32 out.jsonl (262,144 shots). Report
       the T saving with its standard error, the failure rate and dirty
       shots (must be 0). For very large width streams, use fewer batches
       and say so.
    c. The improvement must clear the target record with margin (packet SD
       of mean T is about 6 on the 1,234-qubit circuits), and the frozen
       circuit must pass the statistical failure-rate gate (declare its label
       and >= 32,768 batches first; gate.py in
       experiments/plain67-operational-20261016 computes all four criteria).
    d. The nonce search must be affordable: expected thread-hours =
       E[batches per nonce] x 0.25 s / (1 − f)^141, where f is the batch-failure
       fraction (see experiments/product-tip-20261015/figures/search-cost.png).
       Above about 1 day on 64 threads, first lower the failure rate or build a
       prefilter.
3.5 Freeze it; screen nonces with nonce_screen OPS 1 COUNT 32 out.jsonl; set
    TAIL_NONCE; run the unchanged benchmark.sh; re-census the final stream.
3.6 Write experiments/<name>-YYYYMMDD/STATUS.md and SUBMISSION-NOTE.md in the
    style of experiments/nonce-screen-20261015, then queue or submit (rules).
3.7 Record every outcome, positive or negative: the experiment's STATUS.md
    (result first, evidence with hashes, gzipped logs, server paths), a dated
    entry at the top of docs/research-plan.md, and updates to
    docs/results-status.md and docs/AGENT_HANDOFF.md (state, numbers, backlog
    order). Update the README and its figures only for scored or complete
    local results. Commit and push. Remove the worktree.
3.8 Every about 2 hours, write a progress summary in LOG.md (records, what
    worked, what failed, what is running, next steps) and push. Then go back
    to 3.1.

=====================================================================
4. BACKLOG (re-rank every cycle; add ideas as you find them)
=====================================================================
T record (parent: our 5a7c3902 / 7ff2ba53; its stream hashes to 01aad987...)
 T1. Port the larger-expression cache (cache-retention 128/1,000,000: about
     -101 T for about +5 Q) into src/point_add as a final pass before the
     nonce tail. Template: experiments/toffoli-readiness-20261015/prepare-wide.py.
 T2. Port the EXACT improvements the public tip made after B3 (git diff
     b3c9fdd6..4b2ec52f): the square guard-tree finish (about -42 T),
     exact row cuts, dropped-carry table re-picks and the narrowed compares
     its notes call exact. Never port census cuts.
 T3. Spend more width on T: retain ANDs instead of recomputing them, give the
     exact overflow routes room, use larger caches, and remove recompute
     chains that extra scratch makes unnecessary.
 T4. Lower the failure rate on the wide circuit (non-walk floor of about 1.1
     batches; lead: experiments/trace-audit-20261015/FOLD-BOUNDARY.md). This
     buys room for future exact savings.
Product record (parent: 4b2ec52f, or the current record)
 P1. Classical value-failure prefilter: replay the leapfrog GCD walk with
     the record's rail envelope, plus fast secp256k1 scalar multiplication
     (<= 10 µs per shot). Validate it on census failing inputs (the census
     jsonl stores k1/k2). It may only skip nonces that would fail. This
     unblocks every high-failure-rate search.
 P2. Exact width-free savings of >= 12–15 T at Q1234 (exact caching variants,
     cheaper exact cleanup, T2-style ideas found on the tip itself).
 P3. Cheap failure-rate repairs at Q1234; add a qubit only if it saves
     > 617 T.
 P4. Other widths: check Q1233 (T <= 761,839 needed) and Q1235 (T <= 760,605)
     with exact changes.
Qubit record (parent: 586a7673 (Q679) or eec4ffc8 (Q680))
 Q1. Rebuild the record, measure its failure rate (fewer census batches is
     fine; disclose it) and its stream size. These streams are about 1–2
     billion ops: check memory first; never exceed about 100 GB for a
     loaded stream. Prefer streaming (the 680 note documents LOWQ_EXACT_STREAM_PATH)
     and extend the screener and census to stream ops from disk if needed.
 Q2. Apply the levers the 680/679 notes list as open (more R lanes found off
     the ring, exact cuts, lane loans), each proven with their packed replay
     tests plus our census. One qubit is one record step.
 Q3. Use our own width evidence (experiments/followup-20261015 bank-swap
     Q692 line) only where it transfers; the public 680/679 ring design is
     ahead of it.
When the backlog runs dry: read the five most recent frontier advances' notes
for exact, transferable ideas; mine our traces for unexplained failure
clusters; write three new hypotheses with cost estimates into the handoff guide,
then continue.

=====================================================================
5. NEVER PAUSE: WHAT TO DO INSTEAD
=====================================================================
- Server unreachable: retry every 5 minutes. Meanwhile do local work:
  analysis of saved evidence, prefilter design and pure-Python models,
  reading competitor notes, write-ups, the leaderboard refresh. This PC has
  no Rust toolchain; heavy work belongs on the server.
- Server busy: lower your own thread count and run smaller censuses. Never
  stop other users' jobs.
- A job crashes: save its log as a failed attempt, fix or drop it, and move
  on.
- An idea fails twice: record why, lower its rank, and move to the next.
- A rule conflict, or an irreversible action outside this repo and the
  research directory: skip that action, record it in LOG.md under
  "Needs user", and continue with something else.
- Context getting long: make sure LOG.md, the handoff guide and the STATUS
  files hold everything needed to resume, then keep going.
```
