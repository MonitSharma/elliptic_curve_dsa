# RNG-free ternary certificate: sound but no coverage

**Negative experiment.** A conservative bit-value abstraction tracks known0,
known1 or unknown per shot, using conditional mux for swaps and HMR updates,
and immutable snapshots for pushed guards. Measurement outcomes are unknown.
A known wrong output would prove failure for every possible MR assignment,
without generating any SHAKE measurement words. Unknown outputs cannot reject.

All 320 primitive containment checks pass. On 256 selected actual inputs
(128 failing, 128 controls), every final quantum and classical word contains
the protected simulator's value. Runtime is about 51.4 ms per 64-input batch.
However, **all 131,072 output bits are unknown**, so no failure is certified.
Lost correlations between repeated random expressions make this abstraction
too weak. No nonce search used it, and no candidate source changed.

Source stream: public product tip `4b2ec52f`, 11,630,716 operations, SHA256
`2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e`.
Inputs: first128 wrong-value rows and first128 controls from the preserved
262,144-shot census coordinate file. Protected simulations use an independent
label and verify complete final state containment. The abstract operation
rules are sound by Boolean set containment and compose inductively, but the
result supplies no useful rejection certificates on this sample.

Server: `/home/hclau/ecdsa_research/rng-free-certificate-20261016`.
Raw sources, build log, containment log and hashes are preserved. This line
stops here; the source-bound arithmetic-model investigation remains active.

A second use tests the exact inherited-cut predicates on the reconstructed
pre-census stream (all144 source anchors checked independently). A deletion
needs guard & a & b =0; a CCX-to-CX reduction needs guard & survivor & !removed
=0. Pushed-guard snapshots are included. On the same256 inputs, no input can
be proved inactive at every cut; complete state containment still passes.
Runtime65–70ms per64-input batch. This second attempt also supplies no
certificate and stops. The original attempt's source/logs are retained in
`initial/` rather than overwritten.
