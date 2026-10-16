All owned work was reversibly paused at the user's request at 09:07:19 Singapore time. No process was killed, no new workload was launched, and no submission was made.

PRODUCT25's unchanged benchmark completed before the stop. All 9,024 shots passed, with zero classical mismatches, phase garbage and ancilla garbage. Its authoritative score is Q = 1,234, rounded T = 761,171, and Q × T = 939,285,014. This improves the standing product of 939,347,948 by 62,934. The exact executed Toffoli total is 6,868,802,834, giving mean 761,170.526817375910. Nonce 47,449,113 is the audited lowest passing operational nonce.

The regenerated stream has SHA-256 93122ce2668fe2861eba894b1520d3e44552c2094487337dd92300c2aa9d57d2, identical to the previously verified selected native stream. Every point_add source file remains frozen. Source freeze and native verification receipts are preserved alongside this file.

The post-benchmark verifier is paused before its final receipt. The scorer appended exactly one OK row to tracked results.tsv; the full file, appended row, score and complete benchmark log are copied under stop-preserved/. The candidate's generated results file has deliberately not been altered during the pause. The final predeclared census of 32,768 batches per source has NOT run. This is a passing benchmark candidate with final qualification pending, rather than a completed submission-ready record.

These process groups are stopped, and every observed member has state T:

- 628797: PRODUCT25 final coordinator and post-benchmark verifier.
- 595517: ALL70 fixed 67-stage cache chain.
- 595518: ALL70 native-generation watcher.
- 595519: ALL70 census watcher.
- 606954: ALL70 terminal-archive watcher.

Full process IDs, commands, hashes and states are in STOP-CHECKPOINT.json.

ALL70 has 19 complete universally checked stages. Stage 20's universal audit is paused; the fixed endpoint remains stage 67. Final native generation and the final census have not started. No intermediate checkpoint has submission authority.

The separate wide15-retained4096-record-20261016 directory contains only the protocol declared before search. No search, source copy, build, benchmark or final census was launched for it. The root-owned frozen probe and its prior passing gate remain preserved separately.

Resumption requires explicit user authorization and fresh verification of process leaders, groups and available resources. Resume only the desired owned group with SIGCONT; waiting native, census and archive groups would otherwise launch future phases once their conditions are met. Nothing will resume automatically.
