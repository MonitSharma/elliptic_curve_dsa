# Public-input curve preparation backend

Research tool only; no submission files or protected evaluator were changed.
The server experiment is `/home/hclau/ecdsa_research/scalar-fast-20261015`.

The backend prepares P, A and P+A from two public 32-byte scalars. A fixed
generator table, variable-time public lookups and batch normalization of 192
projective coordinates reduce measured fresh-input preparation to **9.391419
microseconds per shot** with window 20. The table uses about 800 MiB and takes
5.66 seconds to initialize once; worker threads share it read-only. Window 16
uses about 64 MiB and measures 10.985263 microseconds per fresh shot.
Each timing processes 128,000 newly generated scalar pairs. Earlier repeated
64-input timings are retained separately and are not the selected result.

The independent protected Rust curve reference agrees on 4,096 pairs, 8,192
scalars and 24,576 coordinate values, including zero, order, overflow and
infinity cases. Scalars reduce modulo the group order; infinity uses (0,0),
matching the protected reference. Native point comparisons also pass.

The exact prefilter agent integrated this backend. For the same 128 nonces
and 1,034 simulated batches, every result and first failing batch agrees:
67.38 thread-seconds versus 84.17 with its previous curve backend, and 284.85
for the protected evaluator. This is a complete-screen speedup of 4.23x over
that protected baseline, not sufficient alone to unblock the product search.

Dependency: bitcoin-core/secp256k1 tag v0.7.1, revision
`1a53f4961f337b4d166c25fce72ef0dc88806618`, MIT license preserved in the
evidence archive. The direct compilation flags are recorded in the build
scripts. This implementation uses public scalars only.

An isolated follow-up replaces generic signed rail shifts with explicit limb
operations. Its independent width/shift tests pass. On 262,144 inputs,
predictions are byte-for-byte identical; arithmetic takes 80.691 versus
121.518 microseconds per shot in the paired run (total 85.052 versus
125.703). These timings include concurrent server load. The arithmetic
failure model itself remains diagnostic and cannot reject nonces.

Sources, compiler logs, vectors, validation and content hashes are bundled in
`evidence.tar.gz`; large vendor/build directories remain on the server and
are reconstructible from pinned revisions. No scored resource claim follows
from these preparation timings.
