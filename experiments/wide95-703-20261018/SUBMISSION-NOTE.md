# Toffoli candidate: 752,991 executed Toffolis (1,863 qubits)

Queue mode; not yet submitted. This targets the fewest executed Toffolis,
**703 below the public record 753,694** (our `b99c9678`, WIDE95, 1,556 qubits;
refreshed 18 Oct 2026) and **730 below our prior public record 753,721**
(`03be8e19`, WIDE15, 1,468 qubits). Extra width is deliberate: this record
ignores qubits. The product (1,402,822,233) is not competitive and is not
claimed.

**Unchanged benchmark.** All 9,024 shots pass; classical, phase and ancilla
failures are all zero. Total executed Toffolis 6,794,986,909; mean
752,990.5706; rounded **752,991**; peak **1,863** qubits.

**Circuit.** Our official 753,694 source `b99c9678` (`5a7c3902` + fixed 95-stage
exact cache `frozen_cache_wide95.bin`) plus `retained_703.rs`, which caches all
703 remaining unconditional repeated-AND pairs in the circuit using the
Symmetric Triple identity over $\mathbb{F}_2$ ($\mathcal{T}(X, Y) = \{X, Y, 1 \oplus X \oplus Y\}$,
where $A \cdot B = X \cdot Y$ and $(-1)^{A \cdot B} = (-1)^{X \cdot Y}$ for any
distinct $A, B \in \mathcal{T}(X, Y)$) after evaluating constant lease
conditions (`temp1 == 1`, `temp2 == 0`). Together with the 1,839 live leases in
`frozen_cache_wide95.bin`, this caches 100% of all 2,542 unconditional
repeated-AND pairs in the secp256k1 Leapfrog circuit. Only `src/point_add`
differs (`mod.rs`, `frozen_cache_wide95.rs`, `frozen_cache_wide95.bin`,
`retained_703.rs`, nonce). The final stream's pre-tail (10,550,160 ops) is
byte-identical to the gated stream. Protected files match the base. The
inherited approximate arithmetic of the parent is unchanged.

**Failure rate (fresh inputs, declared before running).** Label
`wide95-703-gate-20261018-v1`, 32,768 batches (2,097,152 shots) per source, on
identical inputs.

| | Record `7efded3d` (WIDE95, 753,694) | Prior record `1d8c05ee` (WIDE15, 753,721) | This candidate (`WIDE95+703`) |
|---|---:|---:|---:|
| Failing batches | 1,328 | 1,328 | 1,335 |
| Failed batches per 9,024-shot packet | 5.71 | 5.71 | 5.74 |
| Value-failing shots | 1,154 | 1,154 | 1,154 |
| Dirty-ancilla shots | 0 | 0 | 0 |
| Fresh mean executed Toffolis | 753,697.53 | 753,722.33 | **752,994.53** |

Against the current record `7efded3d` (WIDE95): 38 batches newly failing, 31
newly passing, one-sided exact McNemar $p = 0.2352 \ge 0.05$; paired saving
**702.995 ± 0.249 T**. Against `1d8c05ee` (WIDE15): 40 / 33, $p = 0.2414 \ge 0.05$;
paired saving **727.796 ± 0.282 T**.

Disclosure: two earlier sibling cache variants of `5a7c3902` (WIDE67 and
WIDE95+cap2048) failed their own pre-declared gates under our earlier strict
rule. Those verdicts stand. `WIDE95+703` is a distinct frozen stream with no
earlier verdict.

**Nonce.** 167, ascending from 1, lowest pass; 256 nonces screened with the
exact screener (all of 1–166 fail; the rest is parallel in-flight work). No
nonce was chosen by its Toffoli count; no circuit content, table or cut was
tuned to a test packet.

**Hashes.** Final stream SHA-256
`09dbeacbd80a5d51656723c4350e367e91d5b5a00306008bf97b288bd4a205e4`; patch
`6a0aa8e0dab619a874919d6e4dd3dbdb454b4906a92b34bbdeb89f007f8cacef`; frozen
gated stream `b127c64e9e6fa14e497d6338950ee477805fe8990abd59ec05a8f96d9c1295e8`.
