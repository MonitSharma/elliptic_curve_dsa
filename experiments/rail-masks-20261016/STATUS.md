# Register/mask advisory — exact flags, modest kernel improvement

The generic ABI remains unchanged. Variable-index vector-limb accesses use masked
selection; sign-extension masks are precomputed and combined with ternary logic.
All262144population flags,517edge inputs, partial vectors and a changed valid
table match the original library. Three interleaved trials measure best5.41024
microseconds per shot versus6.25416original, about13.5%less time. This is advisory
kernel timing, not complete screening throughput or a resource record.

An initial Python table-formatting failure is preserved. The corrected library
SHA256 is046dd5f1d11386550ec5234b955f6bc1974431e79a6b80499bda97da0ade3e90.
It may prioritize exact checks but never directly rejects a nonce. Integration
is isolated in the still-disabled masked-witness benchmark.
