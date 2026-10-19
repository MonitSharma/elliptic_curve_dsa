# Source-exclusive parity carry bridge

Three native component tests pass. A source pivot may temporarily hold a
Cuccaro carry only if it occurs in exactly one addend row and aliases neither
target nor incoming carry. Its parity basis is restored exactly. Each borrowed
stage trades one extra emitted CCX for one fewer owned carry wire.

523776 small-basis evaluations n3..7 pass value/source/ancilla/phase checks
(some bridge patterns duplicate). Every physical RNG phase coefficient and
the inverse pass on64 bases. Unsafe source/target/carry aliases reject before
emitting gates. Four local Boolean lemmas are UNSAT; missing-CZ control SAT.
These local lemmas and written induction do not formally verify Rust control
flow or complete point addition. Protected17 unchanged. All23 archive members
verify locally. This is a component, not a point-add resource record.
