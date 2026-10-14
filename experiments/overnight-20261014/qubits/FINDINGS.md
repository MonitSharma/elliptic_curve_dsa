# Identical-input diagnosis of the failed compact reciprocal

14 October 2026, Singapore time. **Research diagnostics only; no qualified
score, width improvement or submission.** The existing compact patch remains
unchanged in `agents/qubits` and in the preserved server `compact` checkout.

The first full-benchmark counterexample, shot 1170, also fails the clean public
`c95b9325913abacca9c86bdebad10a20633cd04e` circuit when given exactly the compact
stream's point coordinates. This establishes an inherited correctness failure
for that input. The completed five-batch pair also establishes public-source
failures on shots 1937, 4131, 4202 and 8048. It does not establish that all six
original compact failures are inherited or that the compact change introduces
no other regressions.

The compact diagnostic reconstructed all 9,024 original Fiat–Shamir points and
replayed batch 18 with the original measurement RNG offset. It reproduced shot
1170, with one classical mismatch, zero phase in that batch, and 22 dirty
ancillas on its lane. The clean-base paired replay used the same 64 point pairs
and an independent fixed measurement seed. It also failed shot 1170, with zero
phase and 34 dirty ancillas. Different internal measurement transcripts can
propagate dirty arithmetic into different final coordinates; equality of those
incorrect output coordinates is not claimed.

The exported point packet SHA256 is
`fbeaf4f6dd9584527f974d49244d0a3af69f3f1370ef7cbe25e603061f90ba6e`.
The independently rebuilt clean-base diagnostic stream SHA256 is
`9fcdc3449204b433cb060645423f86b42b32e7ec8858688b137fbbf6a7591721`, matching
the public author's recorded stream. Generation was successful, with measured
child exit 0. The first wrapper's relative exit-marker path failed after it
changed directory; that bookkeeping failure and its original log are preserved.
Neither diagnostic generation nor paired replay produces a challenge score.

## Arithmetic localization

Shot 1170's second intended division starts at
`dx'=0xe1a14a46e6340fd02bde43002b9b85d32649195df078b8aa7efe88ce0964f802`.
At Euclidean step 36, source column 35, the exact recurrence gives:

| Quantity | Exact value |
|---|---|
| Z = r36 | `0xa73f25333f56020b6ac70113ba377efc65a521b6eb` |
| X = t35 | `0x8e4ffd864049a811d` |
| Y = t36 | `0xb95d8a2fca3706cd8` |
| q36 | 2,216,631 |
| Expected t37 | `0x187da29bb20aa8d1b197f85` |
| K24 search t37 | `0x187da3550f94d89be89ec5d` |

The approximate reciprocal accepts one additional Y. The exact quotient is
within the existing QB23 cap. The independent integer model and the clean-base
native column reproduce this error. Both intended denominators for shot 1170
fit EMAX21: their maximum nonzero Euclidean valuations are 6 and 10. The
independent audit of all 18,048 intended denominators finds no valuation or
modeled map-region violation. This first failure is not explained by EMAX21.

The corrected v2 native column diagnostic uses distinct package/binary names
and prints distinct base/compact source paths. It emits different operation
counts for the two sources. All 693 quantum words agree at recorded stages
0–10 for this admitted HR state, including 259 dirty passengers. Both sources
produce the incorrect t37 after stage 4; both inverse column runs restore all
words with zero phase. This is a single column without payload, using the local
builder's default cancellation settings, not a full-circuit equivalence proof.
The final attested run corroborates this result with separate build directories,
unique binaries, embedded commit/three-source-hash attestations checked against
the checkout bytes, and 693-word snapshots for every recorded stage.

## Other preserved packet leads

The independent integer audit flags these five point inputs:

| Shot | Division / Euclid step | Modeled violation |
|---|---|---|
| 1170 | 2 / 36 | HR reciprocal chooses one extra Y |
| 1937 | 2 / 10 | HR reciprocal chooses one extra Y, despite q=10 |
| 4131 | 1 / 100 | HT reciprocal leaves quotient residue 2, q=101 |
| 4202 | 2 / 40 | HR reciprocal misses one Y, q=1,847,351 |
| 8048 | 2 / 23 and 25 | HR reciprocal error; later exact q=8,505,374 exceeds QB23 |

A five-batch paired diagnostic completed on both streams with the same fixed
RNG word sequence. Both fail these same five shots among 320 input pairs.
The base has phase on the failing lanes in batches 30 and 125; compact in
batches 30 and 65. Both have dirty ancillas on every failing lane. The mapping
of random words to measurement operations differs between streams. The sixth
original compact mismatch is not yet localized. Increasing head precision
alone cannot repair the quotient-cap counterexample at shot 8048.

## Preserved diagnostic failures

The first one-column differential attempt is explicitly
**invalid_duplicate_binary**. Two external crates shared a Cargo package
name/version and target directory; the second invocation reused the first
binary. Its original logs and state comparison are preserved under their
original names and are excluded from the corrected comparison claim above.
The corrected v2 uses unique names and verifies source tags and differing
operation counts. Future probes also embed source hashes and use separate
build directories. Two later attestation wrappers failed on binary/path-name
bookkeeping before a complete differential run; their logs are retained.
The explicit-path final attested wrapper completed successfully.

The compact full benchmark remains failed: six classical mismatches, three
phase-garbage batches and six ancilla-garbage batches. Component results and
this inherited counterexample do not overturn that result.

## K25 component repair and next experiments

A compact K25 remainder uses the public circuit's original 25 scratch lanes
(`ring[0..19]`, SX1–SX5, and the virtual leading-one lane) without increasing
Q693. The window-top lane is untouched by V's additions; it is returned before
binary-search predicates. The divisor head and care-rotation protection must
grow together. This source-isolated experiment passed the focused native suite:
18 tests passed, none failed, and one inherited test remains ignored. Its new
column-35 regression uses the exact Euclidean recurrence, 64 cases with dirty
passengers, all-wire comparisons, zero phase and exact inverse restoration.
It repairs the localized shot-1170 column error without increasing that
component's 693-wire allocation. The prior K24 column is its negative evidence.

The exact source and reapplicable patch are in `candidate-k25-manifest.json`
and `candidate-k25.patch`. Only `src/point_add` changes. QB23 and the nonce are
unchanged. This is not a full circuit result or a proposed record. No full
benchmark is scheduled while the known quotient-cap counterexample remains.
Full correctness, quotient capacity and any Q692 schedule remain open.

N275 would create six external quotient owners q17–q22, whereas SX1–SX5 fund
only five. SX6 holds the gate accumulator. Sharing a switch or size lane also
affects payload padding, selectors and the seven-lane parking cycle; no such
sharing is justified by a complete lifetime proof yet.
