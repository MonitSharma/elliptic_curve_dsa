# Fresh A29 mask proof

This experiment rebuilds an input-conditioned measurement-dependence certificate directly from the frozen A29 precision-repaired operation stream. Source SHA256: `1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522`. The stream contains 11,636,536 operations, Q1234 and 45,701 classical bits. Its four ordered 256-bit register maps equal the ancestor's maps; this layout observation is not a proof of equal arithmetic.

The original `4b2ec52f` mask, mask roots and compiled evaluator program are never loaded into this proof. Old interval boundaries are only candidate hints. Endpoint matching and nearest-offset selection have no mathematical authority. Every proposed interval must be proved again on the actual A29 operations before any rewrite is used. Failed candidates leave the actual program untouched.

The all-scopes scanner independently enumerates the new program's balanced condition scopes. Its first run tested 69,202 intervals, proved 4,411 disjoint reset projections and preserved every original measurement event, classical assignment and condition snapshot. It took 21.60 seconds. These are local value theorems, not a complete output or phase certificate.

The separate `a29_rng_mask` program begins with arbitrary declared inputs and zero auxiliary wires. Every physical measurement event receives a fresh random symbol, including inactive events. Helper contracts are operation-digest bound and may demand only entry-zero predicates proved by the current symbolic prefix. Conservative caps retain unresolved dependence; input-only caps keep exact immutable definitions. Export aborts if a fresh opaque variable would be presented as a declared input.

An exported dependency root equal to zero for a particular input certifies that scored output bit independent of every measurement and retained unknown. Only a wrong zero-measurement value on such a bit can be a failure witness. Other bits and phase/garbage checks require exact fallback. This experiment is disabled for screening until source binding, semantic containment and independent runtime evaluation have all passed.

Budget: one worker and at most 24 GiB address space for the global proof, with resource preflight and dedicated PID, log, exit and before/after hash records. Existing production libraries, masks, search workers and prior archives remain immutable.

The refined run is terminal with exit 0: 33 native tests and four protected full-state containment streams pass. It freshly re-proves 4,161 reset intervals and accepts all 376 actual-operation-bound helper contracts with independently checked prefix predicates. Replay takes 379.90 seconds, retains 38,468,794 input-only coefficient nodes and preserves all 906,214 A29 measurement events.

Its exported mask has two constant nodes and all 512 dependency roots equal to one. Thus it certifies no scored bits and rejects no inputs. This is a negative result about the strength of this conservative symbolic model, not a claim that the circuit really depends on measurement outcomes. It provides no usable A29 screening acceleration. The planned smaller-cap script was not launched. The incomplete first trial was explicitly stopped, receipted and preserved; no mask was admitted from it.

The first residual quantum measurement taint is A29 operation 3,991,486, a CCX targeting q588, followed by q260/q547/q191. This corresponds to the ancestor's operation 3,985,666 in the late-forward tick128 carry family. A stronger exact helper contract, if possible, must be independently proved against actual operations and checked prefix predicates. No old input-conditioned mask can substitute for that proof.
