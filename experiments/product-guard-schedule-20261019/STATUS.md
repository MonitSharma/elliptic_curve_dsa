# Materialized classical guards for lower quantum width

Prospective declaration, 19 October 2026, 16:42 Singapore. No source screen,
candidate, statistical gate or nonce search has run in this experiment yet.
Parent: exact public 9dc3798c / source 0c3a0751, compressed stream SHA256
99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683.

The completed commuting-order screen kept Q1234 after moving 6.18m gates.
It fenced 960,513 Push/Pop scopes, leaving almost 1.7m small segments. The new
hypothesis removes those artificial scheduling barriers while preserving their
captured conditions exactly. Each captured predicate is materialized in a
fresh classical bit; a classical-only Push/BitStore1/Pop macro computes AND
without any quantum Toffoli. Every quantum gate uses an explicit captured
predicate. Quantum gates may then cross former scope boundaries only through
proved read/write commutations. Both R and Hmr keep their original global RNG
event order, including events behind false guards. No packet inputs are used.

Expected cost: extra classical bits and classical instructions, zero extra
quantum gates or measurements, unchanged executed Toffolis for the same raw
inputs/RNG. Target: fewer simultaneous nonzero quantum lifetimes after exact
coloring. No saving is asserted before the full width measurement.

Required before any source screen: exact converter tests for nested guards,
guard mutation, direct conditions and inactive resets; complete primitive
macro/guard proof or independent symbolic receipt; permutation conflict audit;
protected-simulator transcript controls. An improved candidate still needs a
native source reproduction, new predeclared failure gate, affordable frozen
nonce search, and unchanged official benchmark. Failed past gates stand.

Implementation plan: use atomic classical predicate macros as scheduler nodes,
preserve old classical-bit read/write versions, treat metadata/debug boundaries
as fences, allow conditional Neg as a classical-read phase operation, keep a
single R/Hmr event chain, and use a compact graph/workspace to avoid allocation
cost proportional to every old scope. Build with one job while the 56-thread
parent4 search runs; screen on one core, up to32GiB memory after resource checks.
