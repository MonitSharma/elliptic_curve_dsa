# Final verification: benchmark pass, failure-rate gate failed

16 October 2026, 09:19 Singapore. The user requested verification of the best
preserved product result. Only its paused post-benchmark verifier and its
predeclared final fresh cohort were run. All other research remains paused.
No submission was made.

| Check | Result |
|---|---|
| Unchanged official benchmark | PASS: all9,024 shots; zero value, phase or ancilla failures |
| Rounded executed Toffolis | 761,171 |
| Peak logical qubits | 1,234 |
| Product | 939,285,014;62,934 below refreshed public939,347,948 |
| Exact benchmark Toffolis | 6,868,802,834 total /9,024 =761,170.526817... |
| Native stream and frozen source | PASS; all17 protected files match baseline |
| Final predeclared fresh failure gate | **FAIL: candidate has more failing batches than parent** |
| Independent recount | All65,536 declared raw rows agree with the coordinator |

The selected nonce remains47,449,113, the lowest full protected pass with
complete ascending coverage. Native regeneration preserved all14,142,533
pre-tail operations and the selected96-operation identity tail exactly.
Circuit SHA256:
`93122ce2668fe2861eba894b1520d3e44552c2094487337dd92300c2aa9d57d2`.

The scorer's single appended historical-results row was preserved, checked,
and removed from the candidate's tracked `results.tsv`. Only point_add source
changes remain in the candidate. This does not override the failed fresh gate.

## Final fresh-input result

The fixed label was `product25-final-nonce-20261016-v1`, declared before the
operational nonce search found a pass. Both sources used the same declared
32,768 batches of64 shots, all rows retained, with4 workers per source.

| Metric | Public parent | Candidate |
|---|---:|---:|
| Fresh shots | 2,097,152 | 2,097,152 |
| Failing batches /32,768 | 4,118 | 4,139 |
| Failed batches per9,024 shots | 17.7196655273 | 17.8100280762 |
| Failing shots | 4,390 | 4,413 |
| Value-failing shots | 3,552 | 3,552 |
| Phase-failing shots | 2,580 | 2,606 |
| Dirty-ancilla shots | 0 | 0 |

Failure categories overlap. There are158 newly passing batches and179 newly
failing batches, a net21 additional failing batches. The observed paired mean
Toffoli saving is58.92035 (standard error0.43982); this census saving is not
the official benchmark score.

Both observed failure rates are below the cap of18. The predeclared rule also
requires candidate failed batches <= paired parent. That comparison fails.
This is a terminal policy result for the frozen candidate, not a claim that
the small measured difference establishes a statistically significant
underlying failure-rate increase. Earlier passing cohorts cannot replace the
declared final cohort. Do not resample, choose another nonce or submit this
candidate under the current standard.

## Evidence

- [Benchmark receipt](BENCHMARK_RESULT.json), [source freeze](SOURCE_FREEZE.json), [native receipt](NATIVE_RECEIPT.json).
- [Final census declaration](FINAL-CENSUS-PLAN.json), [launch binding](FINAL_CENSUS_BINDING.json), [complete result](FINAL_CENSUS_RESULT.json).
- [Independent raw recount](FINAL_CENSUS_INDEPENDENT_RECOUNT.json), [archive receipt](VERIFICATION_ARCHIVE_RECEIPT.json).
- `verification-terminal-evidence.tar.gz` contains54 hash-manifested files: both raw JSONL cohorts, logs, selected source archive/patch, protected source, native binaries, census executable/provenance and receipts.

Archive SHA256:
`d06ca5b66e797750bb1cb7f0dabc7f5c1a6ad3520c349cf4c41d513bc7a72d8b`.
The native stream remains separately preserved on the server at
`/home/hclau/ecdsa_research/product25-final-20261016/candidate/ops.bin`.
No circuit source or measurement sample was changed during this verification.
