# PLAIN67 product candidate: gate passed, ascending nonce search running

16 October 2026, 09:36 Singapore. **No score yet; queue mode; no submission.**
PLAIN67 is the public product record's circuit (`4b2ec52f`, Q1234) with a
universally certified 67-stage exact cache chain. It keeps 1,234 qubits and
saves **102.14 ± 0.44 executed Toffolis per shot** on 2,097,152 paired fresh
shots, against the record's 761,222. A pass would give about 761,120 × 1,234 ≈
939.22M, against the public 939,347,948. The stream is SHA-256 `268aefe2…`;
the native source port (three files in `src/point_add`) reproduces it byte
for byte (`product67-native-20261016`).

## Failure-rate gate (statistical rule, AGENTS.md, 16 Oct)

The gate was evaluated on the cohort declared before it was run
(`product67-frozen-20261016`, 32,768 batches per source, parent = the exact
record stream `2a522394`). No new sample was drawn (`gate.py` → `GATE.json`).

| Criterion | Parent | PLAIN67 | Result |
|---|---:|---:|---|
| Value-failing shots | 3,622 | 3,622 | ✓ no more than parent |
| Failing batches | 4,168 | 4,162 | — |
| Discordant batches | — | 155 newly failing / 161 newly passing | one-sided McNemar p = 0.65 ✓ |
| Failed batches per packet | 17.93 | 17.91 | ✓ ≤ 18 |
| Dirty-ancilla shots | 0 | 0 | ✓ |

PLAIN67 also passed the older rule (candidate ≤ parent). Product25 stays
ineligible under the verdict of its own declared gate; it is not re-judged.

## Search runner

The runner reuses the reviewed Product25 operational design: four interleaved
ascending lanes of 4,096-nonce windows, certified wrong-value rejection from
the original-source mask transferred by PLAIN67's universal cache certificate,
exact full-packet fallback, a protected 9,024-shot confirmation of every
pass, and a stop after the lowest pass once every lower window is complete.

- `prepare.py` and `search.rs` apply Product25's operational patches to the
  PLAIN67-qualified filter tool (`product67-filter-20261016`, qualified binary
  `12fb482e`). `audit_tool_diff.py` → `TOOL_DIFF_AUDIT.json` proves the resulting
  source equals Product25's operational source plus exactly the
  qualification-tool edits (candidate hash, op count, certificate paths and
  hashes, optional dispatch library) and the candidate binding in `search.rs`.
- `accept.py` → `ACCEPTANCE.json` (SHA-256 `7637b249…`) binds the stream,
  mask, certificate, transfer, libraries, gate and cost.
- `control.py` → `CONTROL.json`: lane 0 on nonces 1–4,096 reproduces all 4,096
  qualified rows exactly (after dropping the operational-only flags); no pass
  in that range. Operational binary SHA-256 `f86c5616…`.
- `coordinator.py` / `run-search.sh`: 4 workers × 14 threads, count cap
  134,217,728 per lane, **48-hour wall cap**, lowest pass from 1, no selection
  by T. Started 2026-10-16 01:36:40 UTC (09:36:40 Singapore).

Expected nonces to a pass: (1 − 17.909/141)^−141 ≈ **2.08×10⁸**. At the
pilot's 55.8 nonces/s/thread on 56 threads, that is about **18.5 h** (ideal
linear model). The wait is roughly exponential, so a pass within 48 h has
about a 93% chance. The first 90 s covered about 209,000 nonces.

Two harness bugs in the first two preparation attempts are preserved under
`attempt1/` and `attempt2/` on the server: a relative build exit marker and an
over-short diff anchor, then an unhandled intended `search.rs` binding. Neither
touched the search code.

## When the search finishes

**Automated (10:07):** a watcher in
[plain67-final-20261016](../plain67-final-20261016/STATUS.md) runs steps 1–3
automatically, plus a tail-invariance check, and writes `WATCH_RESULT.json`. Its
pipeline passed a full dry run. Only step 4 (the note, and asking the user)
remains manual.

1. Read `RESULT.json`. If its status is `PASS_AWAITS_COMPLETE_LOG_AUDIT_AND_UNCHANGED_BENCHMARK`,
   run a complete JSONL audit of every lower nonce (adapt
   `product25-operational-20261016/audit-terminal.py`).
2. Set `TAIL_NONCE` in the native source
   (`product67-native-20261016/product67/candidate`, in a fresh detached
   worktree of `4b2ec52f` plus `native-candidate.patch`). Confirm the pre-tail
   stream is unchanged.
3. Run the unchanged `benchmark.sh`. The scored product must be below the
   then-current public record; refresh first.
4. Write `SUBMISSION-NOTE.md` with the nonce, nonces screened, the gate table
   above and the paired saving. Queue it for the user.

If the public product record changes before then, the gate must be repeated
against the new record's stream, with a newly declared label.

## Monitor

```bash
ssh smu_server 'cd /home/hclau/ecdsa_research/plain67-operational-20261016 && cat worker*-progress.json; ls passes; cat search.exit RESULT.json 2>/dev/null'
```

Stop cleanly (keeps every log) by writing `0` to `stop-after-nonce.txt`.
