# Exact SIMD/SHAKE census — validated v2

This isolated follow-up preserves frozen v1. It replaces scalar measurement
SHAKE/transposition with the previously validated eight-way SHAKE library.
Each lane absorbs the exact census domain, label length, label and batch index.
Its measurement offset includes every accepted and skipped scalar pair. Output
rows and all simulator semantics remain unchanged.

All4096 throughput rows are byte-identical to frozen v1. On each of the public
product source and old four-stage source, all128 output rows match the protected
reference, every quantum/classical/phase/Toffoli word matches for64 batches,
and every measurement word in those verified groups matches scalar SHAKE.
The threaded partial first17/count11/workers3 test also matches.

4096 batches take11.54 seconds with four workers after table initialization,
versus40.41 seconds for v1. These are census-tool timings, not nonce-screen
throughput or resource records. An initial wrapper check used the wrong success
return convention; its failed attempt is preserved separately.

Stable executable: `/home/hclau/ecdsa_research/simd-census-v2-20261016/bin/simd_census_v2`.
Arguments remain `OPS LABEL FIRST COUNT WORKERS OUT VERIFY_FIRST_BATCHES`.
`FREEZE.json` binds sources, binary, external libraries and validation streams.
Use final0 after validation; existing running v1/old censuses remain unchanged.
The official benchmark remains mandatory on final submission source.
