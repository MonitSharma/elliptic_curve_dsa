# Exact sparse Boolean-polynomial Toffoli simplification

Declared19 October2026,16:13 Singapore before source screening.

Parent: exact public9dc3798c/0c3a0751 circuit, compressed SHA256
99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683.
The frozen parent4 search is independent and remains unchanged.

Hypothesis: the previous factored XOR/product interpreter misses identities
that require Boolean distributivity. A sparse square-free polynomial engine
will expand exact expressions with a fixed64-term/8-degree bound. Expressions
exceeding the bound become fresh unconstrained Boolean atoms; this loses
proof power safely. No values, inputs, tables or cuts are selected by packets.

Only CCX gates whose exact effective-guarded product is zero or equal to a
single guarded control may be removed/replaced. No measurements, phases,
classical slots, qubits or remaining gates change. Inputs are loaded before
op0; Push guards capture values; Hmr bits stay independent fresh variables.
Expected Q is unchanged; T benefit is unknown. A source-only zero result
terminates this fixed screen. Positive sites require separate proof/native
reproduction and a new predeclared gate before any nonce search.

Resource plan: single-core screen, four build threads, libraries1,16GiB
process cap; <=64 research threads including the56-thread search. Long runs
use nohup and retain PID, log, exit and source hashes.
