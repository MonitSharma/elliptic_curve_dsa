# Toffoli candidate submitted — 16 October 2026, 05:19 Singapore

At the user's explicit request, the frozen **753,721 executed Toffoli / Q1468**
candidate was uploaded to ECDSA.fail as
[`03be8e19-ab3b-45c7-9c62-9d78970c4d95`](https://api.ecdsa.fail/api/submissions/03be8e19-ab3b-45c7-9c62-9d78970c4d95).
The initial response is **validating**, with validation job
`232c00cb-dac5-4fe1-8c5a-c385562757ee` queued. No official score is claimed yet.

The complete archived source was restored into a separate detached worktree,
verified against all 175 frozen source hashes and every protected-file hash,
and run through the unchanged `benchmark.sh` again before upload. The fresh
run passed all **9,024 shots**, with zero value mismatches, phase-failure batches
or ancilla-failure batches, reproducing **753,721 T, Q1468, product 1,106,462,428**.
Its stream hash is identical to the original frozen final stream:
`1d8c05eeee7b43dd694506b5efe963c771461b7e690bc62f409947b2306b7d77`.
Fresh benchmark log hash:
`4839ac6ff0da09ff2eecc311bbe9951ee688ab9922bcf888204b6a4829f311b0`.

Both fixed failure-census gates were independently recounted. The final cohort
contains 1,048,576 shots per source: 670 candidate versus 674 parent failed
batches, 5.765991 versus 5.800415 expected failures per packet, and zero dirty
shots. The 731 nonce records contain exactly one pass, nonce 644; all 1–643 fail.
No circuit content, table or cut was changed, and no new nonce search was run.

The restored candidate was committed locally on the server as
`d07ce53b0721e51532f49ed7e73f2621befaa02d`, based on public source
`5a7c390233c72133df9b591c92e43422c5892142`. Only `src/point_add/` differs.
A final public refresh immediately before upload still showed T753,771 as
the public minimum. The dependency declaration names our previous submission
`3f32acd2-71bf-4cc7-bae6-7407be97fe3b` and was recorded by the service.

The submitted public note discloses the nonce, failure cohorts, known arithmetic
limitations, source and stream hashes, complete benchmark and product tradeoff.
Model attribution is **GPT-6.1 Sol, high reasoning effort, Codex**, verified from
the originating research chat's saved session metadata. The existing server CLI
login was reused; no credential was printed or added to this directory.

The original `../RESULT.json`, queued note and original evidence archive remain
historical frozen artifacts. This directory records the later authorized upload.

Files include the public note, dependency declaration, model provenance,
source/nonce and census audits, source commit, fresh benchmark receipt and
compressed log, initial submission response, and latest public status snapshot.
Official evaluation remains separate from this locally reproduced pass.

Server worktree:
`/home/hclau/ecdsa_research/wide15-record-20261016/submission-20261016/candidate`.
