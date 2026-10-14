# Production square consumer diagnosis, October 14, 2026

This is research diagnosis from the passing public product source
`c5bb1ec876db859a3f9f8a9052c140a145df834e`, not a qualified resource record.
Every protected file is unchanged; all source observations live in
`src/point_add/`. The [builder receipt](raw-handoff-receipt.json) and
[observational patch](raw-handoff-observation.patch) bind the production run.
The final unchanged official builder output remains byte-identical baseline
`49b35cf7640ebd529d76894eb8bef93ebf57e7e970fe14b3c27c8c5feb6e73e4`.

The [native prefix receipt](production-prefix-receipt.json) includes separate
source and binary hashes for the final-stream and raw-stream diagnostic crates,
the untouched public loader/library hashes, packet/log hashes, exact boundaries,
actual installed settings and counterexamples. Both diagnostic runs completed
exit 0. They replay the original 64-shot structured packet and actual subsequent
multiply, not an isolated square with its staged state discarded.

## Exact production boundaries and the first discrepancy

Forty-operation observed windows uniquely match the final stream at condition
depth zero. Exact boundaries are coordinate-y subtraction 5,503; division
5,394,653; multiply 11,452,887; final coordinate-y subtraction 11,459,418.
Shorter windows were not unique at the multiply endpoint. The square endpoint
could not be recovered from its last 100 raw operations this way, so the
builder also serialized its original, unmodified operation vector before
postpasses. Raw stream hash is
`eca53f6002583b148973ec0ebfb453839038b92984e3356bec8e24e6c662e683`.
Its exact square endpoint is 5,986,173. Observing/writing the vector adds no
operations and does not change the final stream.

All 64 slopes are mathematically correct after division. The production square
does not return a plain coordinate: it hands a signed odd R0 rail directly to
the multiply. Its actual settings are native B mode 1, T6 seed fusion enabled,
53-bit seam fold and 20-bit borrow erasure. R0 uses wires 0–255 followed by
857,861,860,859. Reading its signed residue requires subtracting
`2^256 mod p = 0x1000003d1` when the extension sign is one.

All 64 R0 values have uniform sign extension and are odd. The outcomes are:

| Family / physical slope | Shots | Correct R0 residue | Correct final x |
|---|---:|---:|---:|
| Zero slope, literal 0 | 18 | 0 | 0 |
| Zero slope, physical p | 14 | 14 | 14 |
| P = -2A, nonzero slope | 32 | 32 | 32 |

The 18 literal-zero shots already have the same residue discrepancy at the
real square endpoint, before the multiply consumes the handoff. There,
expected minus actual is
`0xfff00002c2a00b770b800b77ffc007a40ba00b71869ffc2adcbfe54c000e9c14`.
After multiply's reversed x seam the sign reverses modulo p, giving the
previously observed final-x discrepancy
`0xffffd3d5ff488f47ff488003ff85bf45ff48e796003d523401ab2fff1601b`.
The final y subtraction does not change the phase mask. The physical-p zero
slopes succeed; normalizing them to literal zero would worsen this packet.
Mapping literal zero to p is also non-injective without a retained and cleaned
branch flag. Neither normalization has been adopted.

For all 32 `P=-2A` shots, R0 is the actual signed integer **-p**: low word f and
negative sign, with correct zero residue. This lies outside the documented
generic rail contract `|R| < p`. Their final x is correct, but inherited y/phase
failures remain. This is distinct from the square residue discrepancy.

Public `square.rs` itself documents at its leaf inverse that the `SQ_ASM_TAIL`
node carry cut goes wrong for leaf inputs 0 or 1. `add_cross` truncates the
assembly carry path to `cross.len()+E`; the pinned policy is E=24, whereas
the separately configured research-overlay pin is 18. The full-width diagnostic
printed the actual installed E=18 at every producer site, confirming that the
overlay value is active in this recipe. The next experiment
retains the full assembly path and observes the same real coupled consumer.
No repair claim follows from these 64 shots alone.

The first full-width run completed the square but stopped during the following
multiply at an inherited allocator fingerprint assertion, exit 101. It expected
`15883674259064070659` before reverse tick 126 and observed
`5305852344426446918`. Its [failed receipt](full-cross-bound-failed-receipt.json)
and [source patch](full-cross-bound-failed.patch) are preserved, with protected
changes empty. It produced no complete final stream or coupled-consumer repair
result. A documented unbound allocator research mode is being assessed for the
next diagnostic; no fingerprint was silently relaxed.

## Preserved unsupported standalone fixture

The [standalone test patch](square-zero-test.patch) and
[receipt](square-zero-receipt.json) preserve an earlier failed component test,
exit 101. The runner supplied `G3_UT_CAP`, `G3_UT_BATCHES` and `G3_UT_SEED`,
but the renamed test reads `ZERO_REP_DIAGNOSTIC_*`; actual settings therefore
were the defaults: cap None, 16 batches, 1,024 shots. Its asserted plain-square
output/clean-scratch contract omitted the actual staged seed consumer. It
reported 886 output mismatches, 389 phase shots and 16 dirty batches, with y
preserved. These counts are an unsupported fixture failure, not proof of a
production defect or a scored result. The production boundary evidence above
supersedes that fixture for arithmetic localization while preserving its
source, log hash, incorrect requested keys and actual settings honestly.

No nonce tuning, sampled absent-control gate deletion, full benchmark rerun or
resource claim was used in this diagnosis.
