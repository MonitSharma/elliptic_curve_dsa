# Exact eight-lane SHAKE256 backend

Research-only entropy accelerator for the SIMD prefilter. It preserves
SHAKE256's 24-round permutation, 136-byte rate, 0x1f domain suffix and exact
output order. The wrapper supports cloning a common circuit prefix, eight
different nonce tails, ordinary nonce-major output for input generation,
then interleaved 64-bit random words for eight simulator lanes.

The integrated helper build passes **6,912 checks against Python hashlib.shake_256**,
including empty and partial blocks, rate boundaries, cloned prefixes and
interleaved reads after partially consumed output, and different selected
random-word offsets for each nonce. The selection helper allows the exact
simulator to confirm one advisory batch per nonce while preserving the
original RNG position. Clone the context before selection for fallback.
A 64 MB interleaved-output benchmark takes 24.538 ms total (about 3.067 ms
per nonce for 8 MB each); the first build measured 25.718 ms.
This is an entropy-kernel timing, not a full search timing. Integration must
also match the protected Fiat-Shamir seed and complete simulator state.

Dependency: XKCP revision `4affab454735d54e78156880b3b44e38dcbf765c`,
KeccakP-1600-times8 AVX512 implementation, with the upstream CC0 notices
preserved. The header's default unrolling setting does not alter the round
count: the wrapper explicitly calls the 24-round permutation. The server
directory is `/home/hclau/ecdsa_research/shake8-20261015`.
