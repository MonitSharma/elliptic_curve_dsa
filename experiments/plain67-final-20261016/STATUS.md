# PLAIN67 product candidate: unchanged benchmark PASS, 939,223,314 (queued)

**Result (16 Oct 2026, 22:09 Singapore; recorded 17 Oct 07:35).** The search
found its lowest pass at nonce **129,023,534**; the watcher audited every
lower row and ran the unchanged `benchmark.sh` on the frozen source:
**Q1234, rounded mean 761,121 T, product 939,223,314**, all 9,024 shots pass,
zero classical, phase and ancilla failures. This beats the public product
record 939,347,948 (refreshed 17 Oct 07:30). **Queue mode: not submitted;
awaiting the user.** Note: [SUBMISSION-NOTE.md](SUBMISSION-NOTE.md).

| Step | Evidence (in `evidence/`) | Result |
|---|---|---|
| Search | `RESULT.json`, `passes/` | lowest protected pass 129,023,534; 129,245,184 unique rows |
| Terminal audit | `ROOT_TERMINAL_AUDIT.json` | every row checked; complete prefix 129,052,672 |
| Source freeze | `SOURCE_FREEZE.json` | only `TAIL_NONCE` changed |
| Native receipt | `NATIVE_RECEIPT.json` | pre-tail byte-identical to `268aefe2…` |
| Tail invariance | `TAILCHECK.json` | 512/512 gate batches identical |
| Benchmark | `BENCHMARK_RESULT.json`, `score.json`, `final-logs.tar.gz` | PASS, 939,223,314 |

Large files stay on the server (`/home/hclau/ecdsa_research/plain67-final-20261016`);
hashes in `evidence/LARGE-FILES.sha256`. The candidate tree for submission is
`/home/hclau/ecdsa_research/plain67-final-20261016/candidate`.

---

# PLAIN67 automatic finalization: armed, dry run passed

16 October 2026, 10:07 Singapore. **No score yet; queue mode; never submits.**
A watcher on the server (`watch.sh`, PID file `watch.pid`, log `watch.log`)
checks every 10 minutes for the end of the
[PLAIN67 search](../plain67-operational-20261016/STATUS.md). When the search
reports a pass, it runs the following without waiting for anyone:

1. **Complete terminal audit** (`audit-terminal.py`, Product25's auditor
   rebound to PLAIN67's acceptance `7637b249…`, binary `f86c5616…` and 14
   threads per worker). Every row of every lane is checked for range,
   uniqueness, disposition and pass consistency; the lowest pass must lie
   inside the complete global prefix. → `ROOT_TERMINAL_AUDIT.json`.
2. **Source freeze** (`finalize.py prepare`): a detached worktree of
   `4b2ec52f`, the frozen native PLAIN67 source (archive `428f0806…`) with
   only the `TAIL_NONCE` literal changed, plus the patch and file hashes.
3. **Native tests, build and generation**; then `finalize.py native` proves
   the pre-tail stream is byte-identical to the frozen `268aefe2…` stream and
   the 96-op tail encodes the selected nonce.
4. **Tail invariance** (`finalize.py tailcheck`): 512 batches of the final
   stream under the gate's label must equal the gate's candidate rows. This
   shows the gate verdict applies to the selected stream.
5. **Unchanged `benchmark.sh`**; `finalize.py benchmark` validates its log
   and score, restores `results.tsv`, and refreshes the public API to check
   whether the score beats the then-current product record.
   → `BENCHMARK_RESULT.json`, `WATCH_RESULT.json`
   (`READY_FOR_USER_REVIEW` only if every step passed and the score beats
   the record).

If the search stops without a pass, the watcher writes `NO_FINALIZATION`.

## Dry run (nonce 12,345, fake audit, benchmark skipped)

All steps through tail invariance pass (`dryrun-evidence/`):

| Step | Result |
|---|---|
| Source freeze | only the nonce literal changed; 168 files hashed |
| Native tests | 4 passed |
| Build / generation | 17,891,821 ops; 4 min 14 s; 4.2 GB peak |
| Native receipt | pre-tail byte-identical to `268aefe2…`; tail encodes 12,345 |
| Tail invariance | 512/512 batches identical to the gate's rows (simd_census_v2 `790e9226…`) |
| Audit row checks | the 4,096 lane-0 control rows pass `audit_lane` |

Two bugs surfaced and were fixed in the dry runs, with failed attempts kept
on the server: `dryrun-attempt1` (workspace path relative to the script) and
`dryrun-attempt2` (the PLAIN67 archive carries directory entries).

## After `WATCH_RESULT.json` says READY_FOR_USER_REVIEW

Write `SUBMISSION-NOTE.md`. It must cover:
- the nonce and the operational count, plus the 4,096 control nonces, disclosed
  separately;
- the gate table from the search STATUS;
- the paired saving of 102.14 ± 0.44 T;
- the benchmark result;
- credit to jackylee0424's 4b2ec52f lineage.

Then ask the user to submit (queue mode). Remove the `candidate` worktree once
it is submitted or abandoned.
