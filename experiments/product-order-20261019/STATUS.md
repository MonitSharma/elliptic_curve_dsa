# Exact partial-order scheduling for lower live width

Declared19 October2026,16:24 Singapore before source screening. The exact
public9dc3798c/0c3a0751 stream is fixed, SHA25699edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683.
The independent frozen parent4 search stays unchanged.

Unlike recoloring a fixed sequence or paying for carry recomputation, this
experiment reorders commuting operations. A dependency graph preserves every
read/write conflict on quantum and classical wires, every original Hmr order,
and all Push/Pop/register/debug/unknown barriers. Two control reads commute;
a control read and a target write do not. Phase gates read their support;
measurements and resets write their targets. Therefore the allowed swaps
preserve arbitrary initial phases and the original physical measurement RNG.

One fixed greedy heuristic prefers guaranteed resets, then operations needing
fewer newly live wires, then original order. Reordering is checked independently
with a complete permutation, per-wire read/write epoch positions, unchanged
barrier ranges and original measurement order. Existing exact dynamic coloring
then measures resulting width. No extra quantum/classical/MR gates are added
by scheduling, so executed Toffolis should be identical. Any lower-Q stream
still needs exact native reproduction and a newly declared gate.

Admission: synthetic permutation/value/phase/classical/measurement controls,
independent order checker, source hashes, one-core screen,16GiB cap, four build
threads, research total about64. No statistical census or nonce search here.
