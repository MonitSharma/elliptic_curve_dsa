# Independent Toffoli candidate:753721 T at Q1468

Queue mode; no external submission. This targets minimum executed Toffolis,
50 below the refreshed public753771/Q1464. Product1106462428 is worse than the
product record. Extra width is deliberate for the independent Toffoli objective.

The unchanged official benchmark passes all9024 shots and all failure channels
are zero. TotalToffolis6801582636; mean753721.4800531915; rounded753721;
peakQ1468. Public base5a7c390233c72133df9b591c92e43422c5892142.
Only point_add differs:15 fixed exact cache stages and an identity-tail nonce.
Native48tests and original-to-final anchored state/phase reconstruction pass.
All protected files match the base; every pre-tail record is unchanged during
final nonce regeneration. Inherited arithmetic limitations remain disclosed.

Nonce644, ascending from1 and lowest pass.731 nonces screened; all1–643 fail.
Overrun consists of parallel in-flight work. No nonce was selected by resource
count; no circuit content, table or cut was tuned to a test packet.

| Fixed fresh cohort | Shots/source | Parent failed batches | Candidate failed batches | Candidate failures/9024shots |
|---|---:|---:|---:|---:|
| wide-compound-frozen-20261016 |262144|186/4096|178/4096|6.12744140625|
| wide15-final-20261016 |1048576|674/16384|670/16384|5.7659912109375|

Final paired parent rate5.8004150390625/packet. Candidate value-failing shots606;
phase-failing383; dirty0. All rows and failed inputs are retained. Both complete
cohorts meet the paired-parent gate and cap18. The small rate difference is
sampling evidence, not a repair claim. Final paired diagnostic saving41.89634
+/-0.39903 T. Final sample size and label were declared before nonce selection.

Stream SHA256:1d8c05eeee7b43dd694506b5efe963c771461b7e690bc62f409947b2306b7d77.
Patch SHA256:17975d79e80add6befa62a153e1d772fe502dea59f1e940fc47d1014ef431b7f.
Complete source, patch, tests, benchmark, nonce screen, all census rows and hashes
are preserved in evidence.tar.gz and RESULT.json. Reproduce the unchanged
benchmark and refresh public records before eventual submission.
