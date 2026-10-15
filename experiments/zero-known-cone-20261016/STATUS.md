# Querying only certifiable outputs: negligible reduction

The mask-bound 49-output cone passes 512 actual protected input comparisons,
the previous nested-scope/overwrite fixture and its missing-live-gate negative
control. The 49 selected roots are decoded from the exact frozen v3 mask;
all 463 other roots are constant1 dependency and can never certify rejection.
No input port is removed or renumbered. Only queried final outputs differ.

The resulting fixed-zero-measurement program contains 7,909,293 operations,
versus 7,944,811 in the full-coordinate cone: 35,518 operations removed,
only 0.447%. This is a small component reduction, not a circuit resource
result or established full-pipeline speed gain. No further integration or
production replacement is planned from this bounded experiment.

The same conservative reverse-liveness rule preserves every operand and
captured scope needed by the selected outputs. Actual-input comparisons
check only those 49 outputs; the remaining outputs are explicitly unqueried.
The full original and simplified zero-MR evaluators still match every
quantum/classical word against the protected simulator in the retained test.
No arbitrary-measurement claim follows from zero-MR slicing itself.

New program SHA256:
`595a516bb83d2addd1d46b881ad9c4690d928a9597ee47840e5d9d96cdc5d93f`.
Mask SHA256:
`560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d`.
The complete source generator, native test source, logs, binary hash and
server location are retained. No nonce was selected and rejection stayed
disabled. Original source, programs and selected runtime remain unchanged.
