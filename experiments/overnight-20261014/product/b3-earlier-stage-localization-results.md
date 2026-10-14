# B3 failures are already present in the emitted arithmetic

Status: completed source-bound native diagnostics, failures preserved, no scored or globally exact claim.

The versioned pristine B3 observer adds two earlier dumps: the complete raw point-addition body before any postpass, and the input immediately before Y42Bound. It retains the four later dumps, every source assertion and the unchanged identity tail. The full builder completes exit0; its final stream remains byte-identical to clean B3 (`0f10de57f45349c89163faf6e5ab0694aec3d3bfa720f10ee8b185a9fb2914ce`). Four later stream hashes also exactly match the earlier observer.

All fifteen point tuples from the candidate's official failures already have wrong y in the **raw emitted body**. The256 independent points retain their one failing value there too. Every one of the271 observed x/y value pairs is identical across all six stages in this private MR domain. Thus these observed value obstructions precede Y42Bound, SquareGuard and the preceding postpass chain; this does not establish that every pass is globally correct.

| Stage | Ops | Q / classical slots | R+Hmr | Selected15: x / y failures | Independent256: value failures |
|---|---:|---:|---:|---:|---:|
| Raw emitted body | 11,253,570 | 1235 / 1623 | 902,830 | 13 / 15 | 1 |
| Immediately before Y42Bound | 11,258,786 | 1235 / 2456 | 902,830 | 13 / 15 | 1 |
| After Y42Bound, before SquareGuard | 11,444,335 | 1235 / 11,843 | 905,316 | 13 / 15 | 1 |
| After SquareGuard | 11,668,788 | 1235 / 26,973 | 906,324 | 13 / 15 | 1 |
| After LinearRestore | 11,668,895 | 1235 / 26,973 | 906,327 | 13 / 15 | 1 |
| Final | 11,668,991 | 1235 / 26,973 | 906,327 | 13 / 15 | 1 |

MR transcripts are not aligned between stages. Selected15 phase totals are9/9/8/8/7/7 and are preserved as diagnostics, not as evidence that a pass introduced or removed phase errors. These fifteen known points are repacked into one batch; both they and the exact official candidate packet/transcript have13 x failures and15 y failures. An earlier report wrongly generalized the y-only firstshot249 to all fifteen; that count and its MR/lane sensitivity inference are corrected. The fixed-domain and official-domain evidence remain separate. The raw stage produces exactly the same wrong y for first249 as the official failure, but fixed-domain tests are finite and do not prove measurement independence.

Raw stream SHA256 `ada7ef5264de0d6e600707c2e0672593014006038e454c24e6c74b19b7ca5e10`; pre-Y42 stream `321fab59f362a0462807eabd1bacf0d0a0768b648533a6ef69ce9cf4ff73dc5a`. [b3-earlier-stages-receipt.json](b3-earlier-stages-receipt.json) preserves the observer source-only patch and protected-file hashes. [b3-earlier-stage-replay-receipt.json](b3-earlier-stage-replay-receipt.json) binds the dedicated diagnostic source, native binary, exact packets, all six profiles and logs. Both jobs completed exit0; evidence is in `product-evidence/b3-earlier-stages` and `product-evidence/b3-earlier-replay` under `/home/hclau/ecdsa_research/overnight-20261014`.

Next diagnosis should examine the emitted arithmetic/borrow-seed handoff, not rebind a table header to hide these failures. The uniform+2 producer repair remains separate. An initial rough hypothesis that ordinary failures arise from frequent16-bit zero leaves was retracted after auditing the actual64/65 recursion thresholds: installed policies produce32/33-bit triangular leaves or larger. No ordinary-input failure-density explanation or repair is inferred from that estimate.
