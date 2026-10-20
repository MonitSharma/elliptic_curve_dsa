# Prime unused clean quantum capacity before allocator snapshots

All eight spacious cases stop at the unchanged y42 free-set assertion. The
payload can allocate fresh qubit IDs beyond the snapshot's frontier, then
return them clean; the free set has grown. This experiment tests that diagnosis
without relaxing the assertion: allocate the unused clean capacity before each
plain-pool snapshot, then release in reverse allocation order. No quantum gate,
measurement or reset is emitted. Reverse release preserves the natural LIFO
allocation trace; fresh IDs remain below existing free IDs in the pool.

Native controls must reproduce the original clean-growth assertion failure,
pass it after priming, and compare exact operation fields/allocation traces
with unprimed builders over long interleaved allocate/use/reset/release traces.
Protect all17 external files. Keep the same nine predeclared spacious cases
and byte-exact7fe control. A genuine leak or arithmetic assertion still fails.
No gate, nonce, weakened arithmetic cut or scored result.
