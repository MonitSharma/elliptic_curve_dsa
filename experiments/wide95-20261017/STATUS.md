# WIDE95 Toffoli candidate: unchanged benchmark PASS, 753,694 T (queued)

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
