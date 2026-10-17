# WIDE95 Toffoli candidate: officially scored, 753,694 T (current record)

**17 Oct 2026, 16:43 refresh:** submission
[`b99c9678`](https://api.ecdsa.fail/api/submissions/b99c9678-5a68-49e8-a8b7-91fc6c383e37)
has official metrics Q1556 / T753,694, matching the local benchmark, and is the
public minimum-Toffoli entry. Its status reads "rejected: score did not improve
current best" only because the board ranks by product. The submission-time
account below is kept as history.

## Submission history (17 Oct morning)

The researcher authorized submission with **Claude Opus 5.5** / **Claude Code**
attribution. The first upload was declined before creation because PLAIN67 is
using the account's single validation slot. A guarded continuation on the server
waits for PLAIN67's terminal status, preserves the conflict response, refreshes
the public record and rechecks source identity before the WIDE95 upload.
After PLAIN67 was accepted, the continuation uploaded WIDE95 successfully as
[`b99c9678-5a68-49e8-a8b7-91fc6c383e37`](https://api.ecdsa.fail/api/submissions/b99c9678-5a68-49e8-a8b7-91fc6c383e37).
Its current status is **validating**, with no official score yet.

Expanded public note, dependency declaration and receipts:
[`../submission-approved-20261017/WIDE95/`](../submission-approved-20261017/WIDE95/).
The queue-mode account below is historical.

## Historical readiness: unchanged benchmark PASS, 753,694 T (queued)

**Result (17 Oct 2026, 08:19 Singapore).** Unchanged `benchmark.sh` on the
final source: **Q1556, rounded mean 753,694 executed Toffolis**, all 9,024
shots pass, zero classical, phase and ancilla failures. This beats the public
Toffoli record 753,721 (ours, `03be8e19`). **Queue mode: not submitted;
awaiting the user.** Note: [SUBMISSION-NOTE.md](SUBMISSION-NOTE.md).

| Step | Evidence | Result |
|---|---|---|
| Native port (`wide95-native-20261017`) | `evidence.tar.gz` (native-tests, generate, build logs) | 4 binding tests pass; stream byte-identical to frozen `7c0ac958…` |
| Gate (declared in `GATE-DECLARATION.json`, committed before running) | `GATE.json`, `gate-rows.tar.gz` | PASS vs record `1d8c05ee` (p = 0.82, 1,337 vs 1,343 failing batches, value shots 1,174 = 1,174) and vs `5a7c3902` (p = 0.50) |
| Ascending exact screen | `evidence/screen.*`, `selection.json` | nonce 294; 379 screened; all lower fail |
| Benchmark | `BENCHMARK_RESULT.json`, `evidence/benchmark.log` | PASS, 753,694 |
| Final source check | `evidence/verify-final.log` | only `src/point_add` changed; protected files intact; pre-tail identical; tail encodes 294 |

Server: `/home/hclau/ecdsa_research/wide95-native-20261017` (candidate tree
`candidate/` is the submission source; patch `evidence/final-candidate.patch`,
8.6 MB, SHA-256 `f23f8d69…`, kept on the server).

Sibling verdicts (WIDE67, WIDE95+cap2048) failed under the older strict rule
and are disclosed, not re-judged.
