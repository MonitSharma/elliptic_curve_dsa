# Exact guard-cofactor Toffoli elimination

Declared 19 October 2026, 17:50 Singapore before source screening. Parent:
public9dc3798c / source0c3a0751 / compressed SHA256
99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683.
The independent frozen parent4 search remains unchanged.

The strengthened support allocator still gives Q1234 on all three fixed orders.
Use those same universal support proofs to remove a CCX when its execution
guard intersected with both controls' possible-one supports is FALSE. A CCZ
also intersects the target support. In either case, the gate has exactly zero
action and phase on every reachable basis state, for every input and RNG word.
This is semantic identity removal, not an arithmetic approximation or sampled
rare-event cut. A false execution guard saves no executed T and is reported
separately from a potentially executing identity.

One fixed input: the original public circuit order. Keep every other original
operation and every R/Hmr event, including inactive and zero-target events.
The existing 16-term/32-factor support limits and overflow-to-TRUE stay fixed.
Only zero-proved Toffolis are removed; lane relabeling and final restoring swaps
may also reduce Q. Source content is not selected from any input packet.

Required controls: all previous Boolean/support/reset/swap controls; direct
zero-control and disjoint-support Toffoli identity cases; unchanged protected
outputs/bits/phase/RNG with nonincreasing executed T. Any diagnostic saving
must be checked on fresh curve inputs before a final source freeze and the
single predeclared qualification gate. No nonce search or record claim yet.

Resource plan: one build job, one screen core,32GiB after fresh resource checks.
