# Toffoli candidate: 753,694 executed Toffolis (1,556 qubits)

Queue mode; not yet submitted. This targets the fewest executed Toffolis,
27 below the public record 753,721 (our `03be8e19`, 1,468 qubits; refreshed
17 Oct 2026). Extra width is deliberate: this record ignores qubits. The
product (1,172,747,864) is not competitive and is not claimed.

**Unchanged benchmark.** All 9,024 shots pass; classical, phase and ancilla
failures are all zero. Total executed Toffolis 6,801,338,903; mean
753,694.4706; rounded 753,694; peak 1,556 qubits.

**Circuit.** Our official 753,771 source `5a7c3902` plus a fixed 95-stage
exact cache that reuses repeated AND computations in idle and extra wires.
Only `src/point_add` differs (module call, loader, frozen data table, nonce).
The native source reproduces the frozen cache stream byte for byte; the final
stream's pre-tail is byte-identical to the gated stream. Protected files match
the base. The inherited approximate arithmetic of the parent is unchanged.

**Failure rate (fresh inputs, declared before running).** Label
`wide95-gate-20261017-v1`, 32,768 batches (2,097,152 shots) per source, on
identical inputs.

| | Record `1d8c05ee` (753,721) | Source parent `5a7c3902` | This candidate |
|---|---:|---:|---:|
| Failing batches | 1,343 | 1,336 | 1,337 |
| Failed batches per 9,024-shot packet | 5.78 | 5.75 | 5.75 |
| Value-failing shots | 1,174 | 1,174 | 1,174 |
| Dirty-ancilla shots | 0 | 0 | 0 |
| Fresh mean executed Toffolis | 753,722.66 | 753,764.47 | 753,697.64 |

Against the record: 27 batches newly failing, 33 newly passing, one-sided
exact McNemar p = 0.82; paired saving 25.02 ± 0.28 T. Against `5a7c3902`:
28 / 27, p = 0.50; saving 66.83 ± 0.28 T.

Disclosure: two sibling cache variants of the same parent (67 stages, and 95
stages plus an extra 2,048-cap stage) failed their own pre-declared gates
under our earlier, stricter rule. Those verdicts stand. This 95-stage stream
was frozen before any measurement and had no earlier verdict.

**Nonce.** 294, ascending from 1, lowest pass; 379 nonces screened with the
exact screener (all of 1–293 fail; the rest is parallel in-flight work). No
nonce was chosen by its Toffoli count; no circuit content, table or cut was
tuned to a test packet.

**Hashes.** Final stream SHA-256
`7efded3d956e22172e897d261f5b753ffbac63d9b3f5f0f8bf38e577d3e22fad`; patch
`f23f8d69…`; frozen gated stream `7c0ac958…`.
