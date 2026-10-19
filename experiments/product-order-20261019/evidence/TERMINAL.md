# Exact commuting schedule: negative width result

The corrected source-only run finished with genuine run-v3.exit=0. It
reordered 6,184,657 of 17,891,901 operations, and the complete permutation
audit passed. It preserves the order of both reset and Hmr randomness events,
all quantum/classical read-write conflicts, and every scope barrier.

Peak width after RNG-preserving dynamic coloring remains **1,234 qubits**.
There is no complete product improvement. These are diagnostic generated
streams, not benchmark results. No candidate gate or nonce search was started
by this experiment. The separate frozen parent4 search is unchanged.

All 18 scheduling/coloring controls pass. A further integration control runs
the protected simulator on 512 uniformly generated raw input assignments,
with arbitrary initial phases. Original and reordered full transcripts match.
The colored output matches registered outputs, original classical bits,
phases, executed Toffolis, scratch-state multisets and 64 subsequent RNG bytes
in all eight batches. This is a tool control, not a curve failure-rate census.
Its genuine trace-v2.exit is 0. The initial standalone trace compilation failed
because apply_iter requires an iterator; the corrected call uses v.iter().
Both attempts are retained, and no sample label was changed.

A source-only profile explains the long runtime: 54,996 classical bit slots,
1,949,506 barriers and 1,695,585 nonempty segments. Most segments are very
short, so allocating slot-sized arrays per segment is expensive. The maximum
segment contains 173,933 operations. The profile used a small C fallback after
NumPy and zstd development headers proved unavailable; the installed runtime
library supplied decompression. The original failed profile sources remain.

New direction: materialize captured execution guards into fresh classical
bits, then schedule across the former Push/Pop boundaries with explicit
read/write dependencies and unchanged physical RNG order. Classical bits are
not counted in the public Q×T metric and their garbage is not a scored quantum
ancilla. This requires a new exact converter and proof; it is not implemented
or qualified by the negative result above.
