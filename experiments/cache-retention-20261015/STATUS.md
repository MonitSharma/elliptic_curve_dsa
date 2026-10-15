# Symbolic cache retention: terminal component result

Both generation and replay exited successfully on 15 October 2026. **No new
qualified score.** Larger symbolic expressions reveal more exact repeated ANDs.
The best tested configuration uses five cache qubits and saves **101.109375
executed Toffolis per shot** in each of two fixed 256-shot comparisons.

| Atom cap | Product cap | Diagnostic width | Cache groups | Paired mean T saving |
|---|---:|---:|---:|---:|
| 32 | 200,000 | 1239 | 2838 | 74.91796875, previously measured |
| 32 | 1,000,000 | 1239 | 2838 | Same exact stream as above |
| 128 | 1,000,000 | 1240 | 2869 | 101.109375 |

These are component diagnostics, not complete benchmark scores or record
claims. The larger product cache alone changes no stream bytes. Raising the
expression cap finds 31 extra groups and adds one cache qubit. Extra width is
acceptable for the Toffoli objective; a product improvement has not been shown.

The first configuration reproduces the old wider-cache stream byte for byte.
Both native tests pass, including a deliberately broken phase correction.
An independent emitter reconstructs every operation of the larger stream and
aligns all original measurement events. Both fixed packets are byte-identical
to the previously archived packets; no nonce or test-packet tuning occurred.

All quantum values, original classical bits and phase agree in every batch;
new quantum and classical scratch are clean. The baseline's **one independent
failure and 189 structured failures remain**. This blocks qualification.

The exact source, tests, logs, input packets, source/stream hashes and terminal
markers are in [the receipt](evidence/receipt.json) and [archive](evidence.tar.gz).
All 39 archived artifacts were hash-verified locally. The B3 dependency's
protected files match its revision; the analyzer is an external research crate.
Large streams remain at `/home/hclau/ecdsa_research/cache-retention-20261015/`.
Launcher 3067855 and replay 3070020 are terminal (both exit 0).

The next experiment canonicalizes complemented controls, retaining exact value
and phase corrections. Arithmetic repair remains independently necessary.
