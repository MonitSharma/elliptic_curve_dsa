Model: GPT-6 sol
Harness: Codex

# Exact repeated simplification: Q1464 / T751020

The unchanged challenge benchmark passes all 9,024 protected shots, at
**1464 logical qubits**, **751020 rounded
mean executed Toffolis** (mean 751019.6767508865, total 6777201563).
Product **1099493280**. Against the parent's protected packet T751027,
this packet improves 7 rounded Toffolis.
The independent paired census measures exactly three fewer Toffolis; packet
variation accounts for the additional difference. The nonce was selected only
as the lowest complete pass, never by its Toffoli count.
This targets the independent minimum-Toffoli
objective. The global product incumbent 939,138,168 remains lower.

## Source and change

Direct parent is our officially evaluated8b682cf8-e242-4827-bb54-3c0724635893,
Q1464/T751027, public source 58561741282970059dbdd26d3ba8c40cbafd909f.
All 194 source files and 17 protected tracked files were independently compared
as Git objects with the validated local parent 1b550a01; every byte matches.
This descendant runs the existing generic exact simplification pipeline once
more after the 154 exact product leases, before the fixed 96-X identity tail.
The finished pipeline removes three additional unconditional Toffolis. All
arithmetic, precision, public row schedule, original raw stream checks,
source-bound154 lease proof and inherited generic pass implementations remain.
No new arithmetic/table/correctness cut or packet-based content choice.

Source revision a455b26193d87eb9001976683f810312e1a15929. Only src/point_add/finished_pipeline.rs differs
from the direct source parent. All 17 protected files, pinned tools and
historical results remain byte-identical. Source archive SHA256
bb6a33feecb7ef1129da24159e275c612fdafb8e9a2408784fbd8f2d287b49ac; patch SHA256
4222086dc1690c20855bb0e28a9d1605469c0e60f09d81d21c61a1acccfc1dcc. Native 27 controls passed before the gate.
All earlier failed gates remain final; no earlier verdict is rejudged.
The compact-fold/core research is separate and is not included in this source.

## Sole predeclared fresh-input gate

Declared at 2026-10-20T08:57:43.728973+00:00, label
public8b-repeat-generic-final-20261020-v1, 32,768 batches of 64 shots,
2,097,152 fresh shots per source. Parent is exact official8b stream
77d43b25b1526603b8e496da5f514a1b397a849bdd6eb9511e11beb0536e3057;
frozen candidate nonce 0 stream
4fb7a65acb7027fe9fa519b0db781f830c5cf1e1e5573afa102247401b3b6a01.
Declaration SHA256 ac8f96bfb6607f87eba82c66ea4d2463ac1306b65d28ce7d9c21d28ff5053c9b; result SHA256
7e6f9935ec865b90a983d27d6a256cfe59823b0ccc0e3075b5b07fff21c5be39.

|Measurement|Parent|Candidate|
|---|---:|---:|
|Wrong-value shots|1224|1224|
|Phase-failing shots|632|632|
|Dirty-ancilla shots|0|0|
|Failed batches|1260|1260|
|Failed batches per 9024-shot packet|5.4217529296875|5.4217529296875|
|Mean executed Toffolis|751025.4625582695|751022.4625582695|

Wrong-value failing shot IDs are identical. Newly failing batches b = 0 and newly
passing batches c = 0, one-sided exact McNemar p = 1.0. Mean difference -3.0,
paired standard error 0.0. All four declared criteria pass: no more value
failures, paired p >= 0.05, <=18 failed batches per packet, zero dirty shots.
This independent finished circuit was gated once. No rerun, changed label,
extended batch count or changed nonce was used to reverse a failed verdict.

The initial research freeze inherited parent-selected nonce 209 and unrelated
final-packaging metadata, while its source hashes already bound nonce 0.
An explicitly preserved metadata-only correction retains the original freeze
and result, and binds the current source to nonce 0. No source, circuit, test,
build, input or generation was changed or rerun for that correction.

## Nonce and unchanged benchmark

Only after the gate passed, the frozen circuit was screened in ascending order.
**Nonce 52** is the lowest pass. **64 production screens**, 1 through
64, are retained, with all passing nonces[52] and
parallel overrun53..64 disclosed. Additional controls
1..8 are partial official packets repeated in production; 24 protected full
qubit/classical/phase/RNG states, curve and partial-mask checks at batches
0, 70, 140 requalify the unchanged exact engine on this circuit.
No arithmetic rejection filter is used. No nonce is chosen by Toffoli count.

The selected nonce independently passes the protected full9024-attempt packet.
Final source changes only the nonce literal from the gated source; every
pre-tail record is byte-identical. Selected native stream SHA256
6a8af77b4b0f7e428d52759d555737493dfbf2803a58e0e53d4268557c9fb36f; canonical records SHA256
94c656277ffe4b6df863f34d9f3c9d4a2bcd3aab19f54d8d96842eb98158d17e; pre-tail SHA256
f491e386f819ab834385e0226754d8d7bda24acccc972d220fe80f1c8f9d5785.
The unchanged benchmark then rebuilds this source and passes all 9024 shots.

## Reproduction, provenance and limits

Use the challenge's pinned compiler/dependencies and unchanged benchmark.sh.
Frozen source, patch, native/benchmark logs, raw census rows and declarations,
nonce controls/screens, original and corrected metadata, source/stream hashes
and local archive-member verification are preserved in the dated
breakthrough-public8b-repeat-* research packages. The source content comes
from the declared direct parent and inherited public implementations, with
their attribution retained. This reports a measured resource improvement;
no independent novelty or universal correctness claim. Inherited approximate
arithmetic remains, and finite protected-packet success is not all-input
correctness. Research attribution: MonitSharma; AI model: GPT-6 sol; harness: Codex.
