# Ordinary point failures persist in C5 and the positive-bias prototype

Status: completed source-bound native comparison, no scored improvement or globally exact claim.

The same271 saved point tuples—fifteen known B3 candidate-official failures plus256 fixed independent points—are run through three attested complete raw bodies before any postpass. The protected curve reference independently verifies expected coordinates. All three stream hashes are checked before replay; their protected evaluator/simulator/operation definitions are unchanged. A fresh dedicated diagnostic crate/target binds its source and native binary.

| Raw source | Selected15: wrong x / y | Selected15: wrong pairs | Independent256: wrong pairs | Selected15 native phase shots |
|---|---:|---:|---:|---:|
| C5 | 12 / 14 | 14 | 1 | 8 |
| B3 | 13 / 15 | 15 | 1 | 9 |
| Positive-bias C5 | 12 / 14 | 14 | 1 | 6 |

**All271 observed C5 and positive-bias x/y pairs are exactly equal.** The uniform+2 producer repair therefore does not fix these ordinary-point value failures in the tested domain. Its successful zero-slope correctness science remains separate. The positive-bias raw body is an unbound diagnostic with its later101 source-binding failure preserved and worse generated Q1238; it is not a qualified candidate.

B3 differs from C5 on four known point outputs:382,845,4210 and8033. The first three are wrong in both sources but have different wrong values. Point8033 is correct in C5 and the positive-bias prototype, and wrong in B3. The independent failing point is wrong in all three. These comparisons use different R/Hmr counts and widths; phase transcripts are **not aligned**, and phase totals8/9/6 do not establish a repair or introduced phase error.

A separate pure modular check in [b3-scalar-consistency.json](b3-scalar-consistency.json) tests whether returned coordinates fit one common scalar in the affine addition formulas, assuming retained original target/offset x values. All fourteen known C5 failures violate that identity. B3's extra8033 and the independent failure fit one wrong scalar. This is a diagnostic invariant, not a unique causal localization: changed denominator values, differing scalar handoffs or downstream arithmetic can all affect the relation. Direct source-bound body boundaries are the next check.

The rejected rough16-bit leaf failure-density hypothesis is absent from the inference: actual installed recursion produces32/33-bit triangular leaves or larger. No nonce, packet or source binding was tuned. Native binary SHA256 `180a89adfd8980847341a5e1490044f92c3c9bb609a70cc22ae0f29e0fa9b676`; compile34.08s, replay4.97s, replay peakRSS621884KiB. PID2634310 completed exit0. [b3-arithmetic-compare-receipt.json](b3-arithmetic-compare-receipt.json) binds all source, packet, stream, native and log hashes; server evidence is `product-evidence/b3-arithmetic-compare` under `/home/hclau/ecdsa_research/overnight-20261014`.
