**Superseded by terminal verification, 16 October 2026, 09:19 Singapore:**
native/source checks and unchanged benchmark PASS (Q1234/T761171/product939285014),
but the predeclared final fresh gate FAILS:4,139 candidate versus4,118 parent
failing batches/32,768. The candidate is not eligible under the agreed standard.
No resampling or submission. [Final verification report](VERIFICATION.md).

The following is the historical pre-verification status.

The selected PRODUCT25 source is frozen for final native verification and the unchanged benchmark. No submission has been made by this run. The separate final fresh census remains parent-owned under the plan declared before the operational search found a passing nonce.

The terminal search auditor passed: the lowest protected passing nonce is 47,449,113, with complete coverage of 47,452,160 distinct operational nonces and 3,047 subsequent nonces from the running workers. Preliminary timing/control attempts are separate and must not be added to this unique operational count.

The candidate is a new detached worktree at baseline `4b2ec52fc55da796aa8f5ef851290297e8706424`. Every archived `src/point_add/` byte matches the prior frozen static PRODUCT25 source except the single `TAIL_NONCE` literal, changed from 1,046,072,871,510 to 47,449,113. All 17 protected files match baseline HEAD. Source, binary patch, selected source archive and exact hashes were saved in `SOURCE_FREEZE.json` before tests or generation.

Native verification requires all 14,142,533 pre-tail canonical operation records to match the audited PRODUCT25 stream exactly, followed by 48 unconditional adjacent XX pairs encoding the selected nonce. The original static-cache blob is unchanged. The benchmark script, generator harness and scorer remain unchanged.

The launched coordinator uses four build threads, one library thread and a 48 GiB virtual-memory bound, with a dedicated process group, log, PID and terminal exit marker. The active ALL70 restoration/cache chain is unchanged.
