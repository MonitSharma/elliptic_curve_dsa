# Complemented-control cache: terminal, no extra measured saving

Completed 15 October 2026, launcher PID 3072230, exit 0, server directory
`/home/hclau/ecdsa_research/cache-polarity-20261015/`. **No qualified score.**
Seven more cache groups were found at the same diagnostic Q1240, but the paired
saving remained 101.109375 executed Toffolis per shot on both fixed packets.
This rewrite is correct on the tested scope but provides no additional measured
benefit over the simpler larger-expression cache.

The exact identity `(a xor ca)(b xor cb) = ab xor ca*b xor cb*a xor ca*cb`
allows a cache to serve different complemented-control products. Each use
restores the required linear terms; measured cleanup includes CZ, Z and
constant phase corrections. Constants are proved symbolic identities, never
sampled input values. Expression/product limits are fixed at 128/1,000,000.

Four native tests pass: original wider-cache behavior, its phase fault,
all small complemented-control inputs/outcomes with mutable condition bits,
and detection of a missing linear phase correction. Full-stream generation
and independent reconstruction/replay pass, using the unchanged fixed
independent and structured packets. All quantum values, original classical
bits and phase agree, with clean new scratch. The baseline's one independent
failure and 189 structured failures remain qualification blockers.

Work is confined to external research crates. The submission and protected
evaluator are untouched. Four build threads, one library thread and a 32 GiB
process limit bound resource use; logs and PID are dedicated to this experiment.

[Receipt](evidence/receipt.json) · [Archive](evidence.tar.gz) ·
[Portable external research source patch](research-crates.patch).
All 28 archived artifacts are hash-verified locally; protected files match B3.
