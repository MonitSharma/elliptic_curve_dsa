# Eight-lane advisory rail scan — verified, available for integration

The C AVX512 implementation reproduces the canonical Rust rail advisory flags
on all **262,144** inputs, with zero mismatches in three complete runs. It also
matches 261 edge cases including zero, ±1, powers of two through bit255, and a
partial final vector. It remains an advisory model: no flag authorizes rejecting
or skipping a nonce. The exact circuit simulator must confirm every rejection.

| Two forward walks per shot | Time per shot |
|---|---:|
| Canonical Rust reference | 33.586 µs |
| Eight-lane C, best | 6.283 µs |
| Other C repetitions | 6.286, 6.315 µs |

The measured speedup is **5.345×**, below the requested 10 µs/shot target.
Timings include both denominator walks, gathering AoS limbs and writing flags.
They exclude point generation, modular denominator subtraction, input parsing,
and exact circuit confirmation. This is not whole nonce throughput.

The output counts are [261776, 72, 187, 109] for flags0…3. Bit0 means nonunit
terminal rail; bit1 means a rail truncation observed by the original model.
These reproduce the existing advisory population, including its false alarms
and misses. No correctness claim was strengthened by this implementation.

## API

Server directory: `/home/hclau/ecdsa_research/simd-rails-20261015`.
Published library `librail8.so`, header `rail8.h`, source `rail8.c`.

`rail8_population(steps,nsteps,pairs,count,flags)` returns 0 for a valid table.
`RailStep` consists of six u32 fields w,n0,n1,n2,nb,anchor (24 bytes).
`steps.bin` contains the 138 bound records, using the first138 entries of the
218-entry anchor file, exactly as the Rust model does.
Each input record contains eight little-endian u64 limbs:
d1[0..4], then d2[0..4], where d1 = target.x − offset.x modp and
d2 = offset.x − expected_sum.x modp. Denominators must be canonical modulo
secp256k1 p. The implementation handles a partial final vector internally.
CPU AVX512F/DQ support must be checked by the caller before invocation.

Library SHA256:
`74b8cfead159dfb6d0344f4200edbc05b5ece89835d25c326d81a0e16dfde1d0`.
Table SHA256:
`b3979902aa1635c0915fc2572c1e7a039121889a57b89c62ab3a9851e5b34309`.

## Implementation and scope

Five u64 vector limbs represent the reference's 256-bit low value and signed
64-bit upper word. Vector carry/borrow, two's-complement negation, sign
extension, unsigned window comparison and arithmetic shifts reproduce the
reference equations. Each vector lane is one independent input. All tick
widths and anchors are common across lanes; the extra0…3 shift is lane-specific.

One algebraic simplification avoids variable-width sign extension:
ar(sx(x,nb),extra) is already sign-extended at width nb−extra, so applying that
final sx again cannot change the signed value. Every source truncation and
overflow check is otherwise retained at the same model stage. The two walks
retain their different fused-width behavior.

The unchanged Rust advisory source is snapshotted as
`rail_advisory_reference.rs`, with alloy-primitives pinned to1.5.7. The complete
population is exported as `denominator-pairs.bin` and `reference-flags.bin`,
allowing direct shared-library replay through `verify_binary.py`. The original
coordinate TSV, source model tables and canonical Rust file are hashed in the
manifest. The sibling prefilter task owns all scheduling and final confirmation.

## Preserved setup failure and resource use

The initial harness incorrectly asserted equal step and anchor lengths
(138 versus218); the reference consumes only the needed anchor prefix.
That setup failure (exit101) is preserved in the initial logs. The corrected
run uses the exact reference prefix and exits0. Its peak RAM was about150MiB
and runtime one thread; the build used four threads. No existing workload or
candidate source was changed. No nonce search or submission was run here.
