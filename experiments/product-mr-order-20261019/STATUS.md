# Exact measurement-channel scheduling with an explicit outcome bijection

Declared 19 October 2026, 17:18 Singapore before source screening.
Parent: public9dc3798c/source0c3a0751, compressed stream SHA256
99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683.
The independent frozen parent4 search remains unchanged.

Earlier schedulers kept every reset/measurement in its original RNG order.
That is stronger than channel equivalence. Independent R/Hmr operations on
disjoint quantum/classical supports commute when their independent random
outcomes are identified by event label. Removing only this artificial global
dependency can let ready measurements clean qubits before unrelated work.
Every quantum/classical read-write conflict and captured-scope fence remains.

The resulting circuit uses the ordinary protected simulator RNG in its new
event order. Its coupled physical transcript need not equal the parent's.
An exported, source-bound bijection maps new event positions to original event
labels; under that mapping, values, bits, phase and executed Toffolis must
match exactly. Because all event words are independent and drawn even for
inactive events, this fixed permutation preserves the complete probability
distribution for every input. The statistical gate will still use the usual
unchanged census driver and ordinary physical RNG for both streams.

Two fixed cases: tail-pinned ordinary priority, and tail-pinned priority using
the existing source-bound proved-clean annotations. Both are followed by the
unchanged guard-support allocator. Choose only by complete deterministic Q;
ties prefer the ordinary case. No input packet or failure sample informs the
schedule. Preserve all original quantum gates, event count and Toffolis.

Required controls: corruption/coverage checks for event maps, synthetic
disjoint-measurement swaps with mapped outcomes, all prior dependency/phase
controls, independent complete permutation audit, and protected-simulator
transcripts using the explicit event mapping. A lower-Q stream is a diagnostic
until native reproduction, one new predeclared failure gate, frozen ascending
nonce search and unchanged official benchmark pass. Past gate verdicts stand.

Resource plan: one build job, one screen core, up to32GiB after fresh resource
checks. No job in this directory has launched yet.
