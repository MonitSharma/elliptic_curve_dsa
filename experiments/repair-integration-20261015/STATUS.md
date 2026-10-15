# Combined arithmetic repair and exact phase counterexample

15 October 2026. Terminal research experiment; no qualified Toffoli or product
record, official benchmark run, submission, or new plot point.

## Combined source

The isolated B3 checkout combines the prior +3 interior rail margin, two extra
walk rounds (140 total), tick-104 repair, cap1267 planner allowance, and the
previously proved exact square repair. Protected files are byte-identical to
B3 `b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7`. Square source and its three test
files are byte-identical to the prior cap1267-tested integration.

| Preserved input packet | Shots | Wrong values | Phase failures | Dirty batches |
| --- | ---: | ---: | ---: | ---: |
| Known counterexamples | 15 | 7 | 5 | 0 |
| Independent | 256 | 0 | 0 | 0 |
| Structured | 256 | 128 | 134 | 0 |
| Old candidate packet | 9024 | 5 | 3 | 0 |

The square repair and longer walk coexist without losing either previously
observed value improvement. All zero-slope values pass; all 128 P=-2A
zero-multiplicand values still fail. Arithmetic changes move measurement
events, so phase frequencies and executed counts are not event-aligned savings.
The 15-shot batch's raw executed count includes inactive lanes.

Optimized stream SHA256:
`f736dd5f70aa765ef973f6ede7086409a6ca74b4a4964d42ec055f30ceb2dea8`.
Raw observation stream:
`3bb21936eaf3f077a22d030b4a13c581904cc1794348bd417904adb6b8d4c8c9`.

## Residual arithmetic certificates

The raw pre-Y33 observer matches every quantum wire, classical bit, phase and
executed count of the unchanged simulator on all 9551 fixed inputs. Raw and
optimized old-packet wrong-value sets agree. All five residual failures have
exact signed-integer rail certificates, with exact division at each substep
and unchanged source rails:

| Shot | Phase | Tick | Target error |
| ---: | --- | ---: | ---: |
| 562 | multiply | 92 | +2^96 |
| 720 | divide | 125 | -2^30 |
| 2777 | divide | 119 | +2^42 |
| 3447 | divide | 123 | -2^34 |
| 8322 | multiply | 135 | -2^9 |

[Exact certificates](analysis.json) diagnose signed truncation. They are not a
universal envelope proof; no new widths were fitted to these five inputs.

## Full-stream phase counterexample

This experiment uses the **previous square-room stream**, SHA256
`48e2f0d8ad9bdc492415ec2700fe5dda9edc0e6f1b3a21eb935ef61ecc3953a4`,
and the first fixed zero-slope structured input (shot 1), replicated into 64
lanes. It does not qualify the combined source above.

The instrumented algebraic-normal-form checker reaches its unchanged XOR cap
at operation 769894, Hmr, measurement count 45319. Its prior maximum phase
support was 16 terms and quantum support 3 terms. This result is inconclusive.

The unchanged, previously validated decision-diagram kernel completes on the
same full stream and proves a nonzero final phase expression. A read-only
path extractor then finds this native-verified assignment (indices zero-based):

- Every measurement outcome is zero except measurement **542827**, set to one.
- This measurement is Hmr at stream operation **6999605**, qubit **1191**,
  classical bit **515**.
- All-zero outcomes give phase zero and correct output values.
- Flipping that single outcome gives phase `0xffffffffffffffff` across all 64
  replicated lanes, still with correct output values.
- The protected simulator independently confirms the counterexample.

The isolated frozen-kernel build passes all five existing tests. The extractor
build passes those tests plus a truth-table/garbage-collection witness test.
The kernel's saturated `size_bound` diagnostic is not a node count or an error;
the graph still completes and its concrete witness validates natively.

Two initial observer variants failed compilation (scope and ownership errors,
exit101); both sources and logs are retained. The first nominal BDD invocation
reused the ANF binary through a shared Cargo target and is explicitly invalidated.
Its identical binary hash and wrong four-test suite exposed the reuse. The
accepted BDD and witness builds each use a fresh, isolated target directory.
Use separate targets for future independently prepared variants.

## Evidence and next work

All jobs are terminal: integration PID3102572, corrected observer PID3107247,
fresh BDD PID3108109, and witness PID3110384 exited0. Failed observer PIDs3102573
and3106434 exited101. [Local verification](local-verification.json) checks all
122 archived artifacts, both candidate patches, and the external-crates patch.
[Receipt](evidence/receipt.json) records revisions, protected-file hashes,
stream hashes, tests, packet hashes, failure sets, and invalidated output.

Next trace the witnessed Hmr cleanup to its source primitive and establish a
general phase correction with an independent contract. Then address the
zero-multiplicand precondition and justified rail bounds. Retain the previously
proved caching savings for later integration. Only a complete unchanged official
benchmark on the final source can establish a resource result; refresh public
records before that comparison.
