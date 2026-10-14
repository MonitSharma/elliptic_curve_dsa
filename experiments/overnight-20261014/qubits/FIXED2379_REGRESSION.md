The clean c95 source reproduces the arithmetic failure at fixed independent benchmark shot2379, division2, column86. Its Euclidean quotient is22,815,568, requiring25 bits; the public source stores23. This is a native primitive counterexample, not a new full-point benchmark or a proof of complete equivalence between variants.

The valid external replay uses identical arithmetic input state and64 lanes on clean c95, N275-v2, headflag-v1 and N274-v4. Each diagnostic selects exactly one test. Exit0 denotes successful reproduction of the expected failure, never candidate correctness.

| Source | Wrong output | Sampled forward phase | All-wire inverse restores | Inverse phase |
|---|---|---|---|---|
| Clean c95 | Yes |0|Yes|0|
| N275-v2 | Yes |0|Yes|0|
| Headflag-v1 | Yes |0|Yes|0|
| N274-v4 | Yes |f224c16203bcccc0|No|110b508dafccbea6|

Clean c95, N275 and headflag share the diagnosed wrong Q value d4dce6895ac3a82661405f567. Different capacity and precision choices can change other scratch failures. These phase values are sampled native outcomes and do not establish correctness for every measurement result.

The initial preparer stopped on a missing following-test delimiter before simulation. The second launcher selected zero tests because its renamed filter did not match the function; all its exits0 are invalid_missing_selected_test. The third launcher uses the exact function name and checks both the one-test summary and expected-negative marker. All three attempts and source patches are preserved separately.

Clean replay wrapper PID2711710 completed0 at18:14:27UTC. The third paired wrapper PID2708513 completed0 at18:08:34UTC. Exact source bindings, patches, executable hashes, diagnostic log hashes and classifications appear in fixed2379-regression-receipt.json. No nonce or official test packet was changed.
