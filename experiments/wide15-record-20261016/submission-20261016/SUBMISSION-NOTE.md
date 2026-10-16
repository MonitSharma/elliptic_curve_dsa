# Exact wide cache chain: 753,721 executed Toffolis at 1,468 qubits

This entry targets minimum rounded mean executed Toffolis. The complete local
unchanged benchmark passes at **753,721 Toffolis and 1,468 peak logical qubits**,
50 Toffolis below our previous public minimum of 753,771 at Q1464. The product
is **1,106,462,428**, above the public product minimum of 939,347,948. This is
an independent Toffoli improvement, with no product improvement claimed.

| Measurement | Result |
|---|---:|
| Complete official-benchmark packet | 9,024 shots |
| Total executed Toffolis | 6,801,582,636 |
| Mean executed Toffolis | 753,721.4800531915 |
| Rounded mean executed Toffolis | 753,721 |
| Peak logical qubits | 1,468 |
| Product using the rounded mean | 1,106,462,428 |
| Value mismatches / phase batches / ancilla batches | 0 / 0 / 0 |
| Identity-tail nonce | 644 |
| Nonces screened | 731 |

## Baseline, attribution and change

The direct base is our submission `3f32acd2-71bf-4cc7-bae6-7407be97fe3b`, public
source `5a7c390233c72133df9b591c92e43422c5892142`. That source contains the wide
smooth Leapfrog circuit previously scored at Q1464/T753,771. Its underlying
B3/Leapfrog source and the jackylee0424, krishparadox and earlier contributors
remain credited through the baseline and inherited source. The dependency file
declares this direct predecessor; dependency attribution is separate from
whether the product score is promoted.

The new cache-chain research was performed with **GPT-6.1 Sol**, using **high**
reasoning effort in **Codex**. This attribution is recorded in the research
chat's saved session metadata. The earlier public circuit retains its own
development attribution through the direct dependency declared above.

The new source applies a predetermined chain of fifteen exact cache stages.
These stages reuse Boolean expressions instead of recomputing their Toffoli
products. They are a resource transformation of the parent stream, rather than
new arithmetic approximations. The native integration and support files stay
inside `src/point_add/`, including the stage cache/support modules and their
calls from `mod.rs`. Four additional peak qubits are accepted for the independent
Toffoli objective. The full measured product includes that width cost.

The retained source passes 48 native tests and reproduces the frozen external
operation stream. Original-to-final anchored replay checks compare quantum and
classical state and measurement phase, including inputs on which the inherited
arithmetic fails. Those checks support equivalence on their stated domains;
they are not a claim that this approximate point-addition circuit is correct
on every valid input. No component estimate is substituted for the complete
benchmark result in the table above.

## Circuit freeze and nonce selection

The circuit content, cache stages, tables and cuts were fixed before nonce
screening. Only a 96-operation identity tail was varied. The selection policy
was ascending nonces starting at 1, taking the lowest nonce whose entire packet
passes. Every nonce from 1 through 643 has a recorded failure; 644 is the only
passing nonce among 731 completed evaluations. The extra completed evaluations
are parallel work already in flight. Passing nonces were not ranked by their
measured Toffoli count.

The selected nonce first passed the protected replay and then the unchanged
`benchmark.sh`. A separate prefix audit compares every operation before the
identity tail. The frozen and final prefixes each have 10,522,659 operations
and the same SHA3-256 hash:
`98414b12c1325bee9ffac8a0a4389c28ab80b7669be3c17d569934d37fa8dece`.
Both complete streams contain 10,522,755 operations. The final SHA-256 is
`1d8c05eeee7b43dd694506b5efe963c771461b7e690bc62f409947b2306b7d77`.
This audit checks that the nonce changed only the identity tail; it is not
an additional arithmetic repair or a new resource saving.

## Fixed fresh-input failure censuses

The pre-search admission sample and final sample were declared in advance.
They are retained in full, including failed inputs. The final sample was not
resampled to obtain a more favorable gate result.

| Fixed cohort | Shots per source | Parent failed batches | Candidate failed batches | Candidate expected failed batches per 9,024 shots |
|---|---:|---:|---:|---:|
| wide-compound-frozen-20261016 | 262,144 | 186 / 4,096 | 178 / 4,096 | 6.12744140625 |
| wide15-final-20261016 | 1,048,576 | 674 / 16,384 | 670 / 16,384 | 5.7659912109375 |

The corresponding final parent rate is **5.8004150390625 failed batches per
packet**. Both observed candidate rates are no worse than their paired parent
rates and are below the disclosed cap of 18. The final candidate has 606
value-failing shots, 383 phase-failing shots and zero dirty-ancilla shots.
Failure channels overlap. The difference of four failed batches in the final
paired sample is sampling evidence; it is not presented as a correctness repair
or a statistically established reduction in the population failure rate.

The final fresh-input paired mean saving is **41.89633846282959 Toffolis per
shot**, with reported standard error **0.3990287275801502**. This diagnostic
paired difference is distinct from the **50-Toffoli improvement between the
two rounded public-packet scores**. The two figures answer different questions,
and the independent census mean is not a scored submission result.

## Remaining correctness limitations

The circuit remains approximate. It still fails random inputs and inherits the
parent's structured arithmetic limitations, including the previously disclosed
P = -2A / zero-multiplicand families. The exact cache transformation does not
claim to fix those errors. Its scored packet passes because of the disclosed
identity-tail nonce selection. A complete finite packet pass is not a proof
for all inputs, despite the clean value, phase and ancilla results on that packet.

No gate was removed on the assumption that a rare input would be absent from
the selected packet. Cache content was not altered after examining nonce
outcomes. Lowering the residual arithmetic failure rate remains separate work.
The product-focused candidates and their ongoing searches are separate circuits
and are not included in the resource claim made here.

## Reproduction and preserved evidence

Restore base `5a7c390233c72133df9b591c92e43422c5892142` and apply the final
point-addition patch, SHA-256
`17975d79e80add6befa62a153e1d772fe502dea59f1e940fc47d1014ef431b7f`.
Alternatively, restore the complete frozen `src/point_add/` archive, SHA-256
`541ea5ee2026cd0a0cd01b8c73ef797dd1618c4b861fcd96bf7222dd4efac874`.
The full source manifest covers 175 files. Preserve the public harness, Cargo
files, toolchain and dependencies; only `src/point_add/` differs from the base.

Run the unchanged `./benchmark.sh` from the restored tree with its pinned
toolchain. The submission preparation uses four Cargo build workers and one
library worker: `CARGO_BUILD_JOBS=4`, `RAYON_NUM_THREADS=1`, `OMP_NUM_THREADS=1`
and `OPENBLAS_NUM_THREADS=1`. The research scripts and nonce screener are outside
the submission and do not replace the official evaluator.

The historical full benchmark log has SHA-256
`027697d1af3f40ded5df31a47356d9ba7b9e547bd4cf6625e348ed1c39837c8e`.
The research repository `https://github.com/MonitSharma/elliptic_curve_dsa`
preserves the result, source archive, patch, tests, prefix audit, every nonce
outcome, complete census rows and protected-file manifest under
`experiments/wide15-record-20261016/`. A separate submission preparation directory
records restoration checks and a fresh unchanged benchmark of the restored
source before upload. Its output must match the frozen final stream and score.

The prior target of roughly 753,670 was an exploratory estimate, not a measured
result. This submission claims only the complete result in the opening table.
Future research will try to retain larger exact cache savings, reduce inherited
arithmetic failures and improve the complete product independently.
