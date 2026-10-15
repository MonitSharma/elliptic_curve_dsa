# Wide four-stage candidate: complete unchanged benchmark pass

**16 October 2026, 00:09 Singapore:** the unchanged official benchmark passes
all 9,024 shots, with zero value, phase or ancilla failures. Rounded mean
executed Toffolis: **753,745 at Q1464**, 26 below our public Toffoli record.
Total: 6,801,794,152; mean: 753744.919326. Product: 1,103,482,680, which does
not improve the product record. This is a **complete local pass**, not an
official submission. **Final fixed census passes; queued and not submitted.**
No external submission is permitted in this run: mode is **queue**.

Nonce **92** is the lowest pass from 1; **164** nonces were screened because
parallel workers finish some higher nonces. All 1 through 91 fail. Selection
did not consider T. Protected official replay agrees with the full benchmark.
Final stream SHA256:
`ba9bd28402c5821e5dcb36795003f3ee5fe729bc2a071a9942567ce875ed02be`.

Final fixed census: 16,384 batches /1,048,576 shots per source, all rows kept.
Candidate674 failed batches (5.8004150390625 per packet), parent678
(5.8348388671875); zero dirty shots. Wrong-value shots588, phase shots366.
Paired diagnostic saving23.065684 +/-0.398086 T. Sampling differences are
not a claimed failure-rate repair. Both pre-search and final paired gates pass.
[Submission note](SUBMISSION-NOTE.md) · [Result receipt](RESULT.json).

Parent: our public Toffoli record, revision
`5a7c390233c72133df9b591c92e43422c5892142` (753,771 T / Q1464).
Four predetermined exact passes retain symbolic expressions and cache
repeated products using existing clean scratch. Aligned whole-stream replay
finds 23.03515625 T saved at unchanged Q1464. Native generation must reproduce
the frozen stream `77b7fd4a760b0b639d36a7a28bac0c81af616aea205e1d7030f8bb29e97bbace`
and all 21 native tests pass. Only the identity-tail nonce changed afterward.

Fresh paired census: fixed label `wide-frozen-four-stage-20261015`, 4,096
batches / 262,144 shots per source. Both sources have 155 failed batches,
5.335693359375 expected per 9,024-shot packet, zero dirty shots. Paired saving
is 23.56068 +/- 0.79034 T; candidate mean is 753740.65722 T. These means are
diagnostic, not scored. The candidate passes the pre-search failure gate.

Policy: freeze all circuit content before screening; screen ascending from
1 and select the lowest complete pass, without considering T. Limit 20,000
nonces, 16 workers. After the unchanged official benchmark, re-census both
the final candidate and parent on a **predeclared fixed 16,384 batches each**,
label `wide-four-stage-final-20261015`, including every row. Do not stop early
or change labels based on rates. Publish all samples, selected nonce and
screened count. Final record comparison requires another public refresh.

Candidate tree: `/home/hclau/ecdsa_research/product-exact-20261015/wide-candidate-final`.
Qualification logs: `/home/hclau/ecdsa_research/wide-record-20261015`.
All candidate source changes are confined to `src/point_add/`. The launcher
hash-checks every tracked protected file before and after the benchmark and
preserves the full point-add patch and source/stream hashes.
