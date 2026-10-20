# Full fresh comparison and exact parity equivalence control

Single512x64 fresh comparison of exactpublice3/714c, cache53/93c783 and frozen
cache-plus-live-parity nonce0 source. Four workers/source, eight protected scalar
batches/source; labelpublic-e3-cache-live-development-20261020-v1. All fullsource,
proofs, output canonicalbindings and nativecontrols precede these inputs.
In addition to retaining all differences vs exactpublice3, require every target/
other quantumlane hash and every value/phase/dirty failure flag to be IDENTICAL
between cache53 and the parity output. These two sources have the same RNG
draws; any such difference blocks progression. Wait DEVELOPMENT-CONTROLLER.exit,
not the diagnostic child's run.exit, before declaring any final gate.
No finalgate/nonce/benchmark/score. Retain earlier512 development and all failed
preflights; no phase/failure label is optimized by circuit selection.
