# PRODUCT95 product candidate: gate PASS, search chain running

17 October 2026, Singapore. **No score yet; queue mode; no submission.**
PRODUCT95 is the public product record's circuit (`4b2ec52f`, Q1234) with
the predeclared fixed 95-stage exact cache (the PLAIN67 chain plus 28
further stages frozen on 16 Oct, `product-to95-rank-20261016`). It keeps
1,234 qubits.

| Step | Result |
|---|---|
| Native source port (`product95-native-20261017`) | 3 `src/point_add` paths; 4 binding tests pass; generated stream byte-identical to frozen `ba87b9ce…` (20,275,836 ops) |
| Universal equivalence, stages 68–95 | all 28 appended stages PASS; composed certificate covers 95 stages, 332,059 leases, 758,134 replaced uses, no sampled inputs |
| Declared gate `product95-gate-20261017-v1` | **PASS** against both parents (below) |
| Filter qualification, acceptance, control, ascending search | running as one chain (`plain95-operational-20261017/chain.sh`) |
| Finalization | watcher armed (`plain95-final-20261017/watch.sh`): audit, nonce freeze, native receipt, tail invariance, unchanged benchmark |

## Failure-rate gate (declared in `GATE-DECLARATION.json` before running)

32,768 batches (2,097,152 shots) per source, identical inputs.

| | Public record `4b2ec52f` | PLAIN67 final | PRODUCT95 |
|---|---:|---:|---:|
| Failing batches | 4,179 | 4,176 | 4,165 |
| Failed batches per packet | 17.98 | 17.97 | 17.92 |
| Value-failing shots | 3,614 | 3,614 | 3,614 |
| Dirty shots | 0 | 0 | 0 |
| Fresh mean T | 761,223.29 | 761,120.62 | **761,110.07** |

McNemar (newly failing / newly passing): 161 / 175, p = 0.79 against the
record; 161 / 172, p = 0.74 against PLAIN67. Paired saving 113.22 ± 0.44 T
against the record and 10.55 ± 0.44 T against PLAIN67. Expected product at
the fresh mean: 761,110 × 1,234 ≈ 939.21M (the packet's own mean varies by
about ±6 T with the nonce, which is not chosen by T).

Expected nonces to a pass: (1 − 17.92/141)^−141 ≈ 2.1×10⁸, similar to PLAIN67
(which found its pass at 129M after 12 h on 56 threads).
