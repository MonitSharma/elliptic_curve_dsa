# Original public4b phase localization

This is a diagnostic and primitive-proof archive. No circuit was changed here,
no nonce was screened, and no record or full-circuit MR-independence certificate
is claimed.

The unchanged original public4b circuit is frozen at stream SHA256
2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e.
The independent A29-parent census contained 104 phase-only failing inputs.
The first 64, in census order, were replayed under eight new measurement
streams. Every output remained value-correct; 233 of the 512 replays had bad
phase. The gate-inert observer matched every quantum and classical word,
phase, Toffoli count and final RNG position against the protected Simulator.
All 252 byte-identical complete fold bodies had zero phase delta in these
replays. Smaller source helper intervals often retain transient phase and
their nonzero deltas alone are not fault attribution.

Exact SIMD diagnostics then flipped each of the 906,156 physical measurement
draws individually, with identical inputs replicated into 512 lanes. All 64
witnesses were scanned on the all-zero background; the first four were also
scanned on a fixed pseudorandom background. These are first-order Boolean
sensitivities at the stated backgrounds, not a universal proof excluding
higher-degree MR terms elsewhere. There were 65 phase-sensitive draws and no
quantum-sensitive draws on the zero background. Sixty-three witnesses had one
hit; one had two. The four alternate-background scans found the same sites.
Source roles were 48 ordinary chunked-add carry erases, six joint-lowfold
erases, six TOP1 held-carry erases, four other y15 carry erases and one named
front-seam overflow erase. These conditioned witness counts are not population
failure-rate estimates or a rule for choosing repair ticks.

The first localized actual helper, original operations [689514,689738), has
19 comparison bits and 37 MR/reset draws. A local universal Boolean proof
allows arbitrary entry target/operand bits and classical bits, assumes only
the comparator's allocated scratch wires are clean, and quantifies every MR.
It proves all quantum outputs restored/cleared and exactly

    phase_delta = first_MR * (entry_target XOR carryout(~u + v + seed)).

Outer MR algebra leaves one input-only coefficient equality conservative;
an independent reduced ordered BDD discharges it exactly with 76,532 nodes.
It also independently checks every input-DAG union. Fifteen algebra tests
pass, and 4,096 protected arbitrary-bitplane cases verify phase and quantum
outputs. Thus this original primitive implements its intended shortened
comparison; its observed error is the predictor approximation, not a missing
Clifford term in that helper. The earlier conservative UNKNOWN is preserved.

A source-call observer reproduces the original raw-builder hash
ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69
with gate-inert caller/interface logs. Original and compact indices are mapped
explicitly; original annotations and all MR draws remain accounted for.

The named front-seam classical-source precision idea is a separate experiment
under seam-phase-repair-20261016, with its own predeclaration, source binding,
tests and fresh gate. This archive does not claim that repair passes or that
the original roughly 1.1-failed-batch value floor has been fixed.

Setup failures, the corrected inherited observer output path, conservative
proof UNKNOWN and all diagnostic logs are preserved. The archive manifest
distinguishes included files from large server-only streams/executables.
