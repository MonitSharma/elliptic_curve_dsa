# Approved PLAIN67 and WIDE95 submissions, 17 October 2026

The researcher explicitly requested both submissions and specified the research
model **Claude Opus 5.5**. The harness attribution is **Claude Code**, consistent
with the research workflow and earlier Claude entry. Effort is unspecified.

Both pre-upload audits passed. Binary Git patches match the final benchmark
patches, protected tracked files match the exact baseline, no extra untracked
point-addition files are present, and operation-stream hashes match the passing
receipts. PLAIN67 also matches every source-file hash in its final freeze.
Public records freshly queried on the server remained product 939,347,948 and
Toffolis 753,721. No circuit source was changed during submission preparation.

## PLAIN67

Submitted: [`d7f69382-4716-4b86-9fac-151c8bc581e4`](https://api.ecdsa.fail/api/submissions/d7f69382-4716-4b86-9fac-151c8bc581e4).
**Official status: accepted. Official product: 939,223,314 (Q1234/T761121).**
The service's measured result matches the unchanged local benchmark.
The direct dependency is public record `85d067da-f7c5-485b-9a61-53b0e58f281e`,
source `4b2ec52fc55da796aa8f5ef851290297e8706424`.

## WIDE95

Claimed result: Q1556/T753694, product 1,172,747,864. The direct source dependency
is `3f32acd2-71bf-4cc7-bae6-7407be97fe3b`, source `5a7c3902...`.
**Submitted:** [`b99c9678-5a68-49e8-a8b7-91fc6c383e37`](https://api.ecdsa.fail/api/submissions/b99c9678-5a68-49e8-a8b7-91fc6c383e37).
Current official status: **validating**, with no official score yet.

The first upload received a definite account-limit conflict before any submission
was created: only one submission may be in flight. `finish-wide95.py` waits for
PLAIN67 to finish before preserving that failed attempt and invoking one retry.
The retry ran the full source and current-record audit again and succeeded after
PLAIN67 was accepted. The original failed attempt remains in
`WIDE95/attempt1-slot-conflict/`. The continuation exited successfully.

The server workspace is `/home/hclau/ecdsa_research/submission-approved-20261017`.
Long-running continuations use nohup, dedicated logs and PID records. Upload
responses, status snapshots, source audits, model attribution, public notes and
dependency declarations are saved in each candidate's subdirectory. No API
credentials are read into this research archive. WIDE95 official scoring is pending.
