# Submission inventory at the research pause

**Update, 09:19 Singapore:** the user subsequently authorized final verification
of PRODUCT25 only. Its benchmark/source checks PASS, but its final predeclared
fresh census FAILS:4,139 candidate versus4,118 parent failing batches/32,768.
It is **not eligible for submission under the agreed standard**. No resampling
or submission; other research stays paused. The pending-gate assessment below
is historical and superseded by the [terminal verification report](../product25-final-20261016/VERIFICATION.md).

16 October 2026, 09:10 Singapore. This is an assessment of preserved evidence,
not authorization to resume work or submit. Research workloads are reversibly
paused; unrelated server workloads were left alone.

## Refreshed public targets

The public API snapshot was refreshed during this review and retained in the
ignored `research-output/submission-inventory-20261016/submissions.json`.
Eligible scores include official evaluations rejected solely because their
product did not improve; other rejection reasons are excluded.

| Objective | Current official score | Next strict improvement |
|---|---:|---:|
| Toffolis | 753,721 at Q1468, our submission `03be8e19` | T <= 753,720 |
| Product | 939,347,948 = Q1234 x T761,222, submission `85d067da` | Product <= 939,347,947 |
| Qubits | 677, submission `18912d63` | Q <= 676 |

Official submissions: [our Toffoli result](https://api.ecdsa.fail/api/submissions/03be8e19-ab3b-45c7-9c62-9d78970c4d95),
[product leader](https://api.ecdsa.fail/api/submissions/85d067da-f7c5-485b-9a61-53b0e58f281e).

## Candidate decisions

| Candidate | Evidence at pause | Submission assessment |
|---|---|---|
| PRODUCT25, Q1234 | Unchanged full benchmark passes all 9,024 shots: rounded T761,171, product939,285,014; zero value, phase or ancilla failures | Closest new record candidate. Product improves by62,934, about0.0067%. Final fresh census and post-benchmark packaging remain unfinished. |
| Plain67 product, Q1234 | Paired fresh-input saving102.13839 T; native/proof gates and its original fresh gate pass | Larger measured saving, but no selected nonce or full benchmark. These are diagnostic savings, not a score. |
| Repaired67 product, Q1234 | Paired fresh-input saving49.55103 T; native/proof and original fresh gates pass | No selected nonce or full benchmark. Its separate arithmetic source and filter qualification must remain separate. |
| Product95, Q1234 | Fixed comparison saving112.47266 T | Earlier-stage diagnostic result; native port and fresh qualification incomplete. No submission score. |
| Wide15 + retained4096, Q1473 | Native/anchored qualification and fixed fresh gate pass; paired saving2.99464 T | Potential next Toffoli result. No nonce search, final native selected source, full benchmark or final nonce census. |
| Wide15, Q1468/T753,721 | Already officially evaluated as submission03be8e19 | Already submitted; no repeat needed. Score-only product rejection does not invalidate its official Toffoli metrics. |
| Earlier Q1464/T753,745 | Preserved complete local benchmark pass | Lower-width alternative; improves none of the three current extreme records. Not a priority submission. |
| Original Q692 | Preserved complete local benchmark pass | Does not beat current public Q677. Width engineering remains deferred. |

ALL70, ALL74 and PRESEED10 are incomplete cache/proof pipelines, not submission
candidates. Their partial outputs are preserved. The seed-only restoration's
fresh gate failed the18-batch cap and must not be resampled into eligibility.

## PRODUCT25: remaining requirements

The benchmark completed immediately before the pause. Exact executed Toffoli
total is6,868,802,834 /9,024 =761,170.526817..., rounded761,171. The lowest passing
nonce is47,449,113. The complete operational search covered47,452,160 distinct
nonces, including3,047 after the first pass. Preliminary repeated attempts have
separate accounting; they must be disclosed without inflating the distinct count.

The selected native stream hash is
`93122ce2668fe2861eba894b1520d3e44552c2094487337dd92300c2aa9d57d2`.
The server candidate is
`/home/hclau/ecdsa_research/product25-final-20261016/candidate`.

Before submission, finish the paused post-benchmark verification and the
already declared final cohort `product25-final-nonce-20261016-v1`:
32,768 batches /2,097,152 shots per source, all rows included, candidate failed
batches no greater than paired parent and no greater than18 per9,024 shots,
zero dirty ancillas. That final cohort has NOT run. Earlier passing fresh
tests do not substitute for this predeclared gate. A failed gate is terminal
under the current no-resampling policy.

Then preserve the final receipt/source hashes and benchmark outputs, restore
the benchmark-appended historical `results.tsv` after saving its exact delta,
verify submission changes are confined to `src/point_add/`, and finalize the
submission note, attempt ledger, dependencies and GPT-6.1 Sol / Codex attribution.
The current candidate's appended result is preserved at the pause; do not
submit it as an extra tracked-file change.

If PRODUCT25 becomes the public product record, future product candidates must
meet the failure-rate standard against the record they would then beat; their
earlier original-parent gates do not establish that comparison.

## Preserved evidence and pause records

- PRODUCT25: [benchmark log](../product25-final-20261016/benchmark-at-stop.log), [score](../product25-final-20261016/score-at-stop.json), [native receipt](../product25-final-20261016/NATIVE_RECEIPT.json), [stop checkpoint](../product25-final-20261016/STOP-CHECKPOINT.md).
- Search accounting: [prefilter stop checkpoint](../prefilter-20261015/STOP-CHECKPOINT.md).
- New Toffoli probe: [fixed fresh census](../wide15-retained4096-20261016/FRESH_RESULT.json), [unlaunched final protocol](../wide15-retained4096-record-20261016/DECLARATION.json).
- Other paused work: [ALL74](../census-all74-fixed67-20261016/STOP-CHECKPOINT.md), [PRESEED10](../census-preseed10-fixed67-20261016/STOP-CHECKPOINT.md); ALL70 process groups are in the PRODUCT25 stop checkpoint.

Recommendation: keep research paused. If proceeding later, finish only
PRODUCT25's existing final qualification and submission packaging first.
No new record candidate is fully submission-ready at this pause, and no
submission was made during this review.
