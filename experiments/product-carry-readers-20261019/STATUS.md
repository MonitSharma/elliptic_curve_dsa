# Carry borrowing with exact read-only operand queries

Prospective declaration, 19 October 2026, 18:15 Singapore. No circuit screen,
candidate, statistical gate or nonce search has run in this directory.
Parent: public9dc3798c/source0c3a0751, compressed stream SHA256
99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683.
The frozen parent4 search is independent and unchanged.

Earlier carry borrowing rejected every intervening operand read. Extend it to
queries whose exact Boolean function can be decoded from a three-wire MAJ
encoding. Compact cells have particularly cheap readers: two operand values
become linear in the encoding, so their CNOT reads need no extra Toffolis.
This is a new arithmetic representation, rather than another coloring priority.

Admission: original four/six-operation carry constructor, matching exact cleanup,
initial carry target proved zero, stable operand values through the body,
root/unconditional endpoints, and private cleanup measurement bits excluded
from registered classical inputs. Body operations may read the operands but
must not write them. XOR queries must have decoded degree <=2; phase queries
degree <=3. Retain their exact classical guards. Unsupported queries reject a
cell. Select only disjoint (not nested) capsules for the first implementation.

Conservative cost: one extra reverse Toffoli per capsule plus positive extra
Toffoli cost of decoded queries. Use a whole-circuit upper budget of600 T for
a one-qubit reduction, leaving margin below the refreshed617-T break-even
point. Find a minimum-cost disjoint cover of complete peak intervals; a local
carry result is not a complete Q×T result. Measure the final complete stream.

Before a source scan: exhaustive decoder truth tables and complete capsule
value/phase controls. Preserve source/patch/logs/hashes, failed and unsupported
cases. Measurement cleanup removal requires a private-bit suffix proof and
explicit observed-event injection controls; use ordinary unmodified census and
official benchmark for final qualification. No gate verdict may be resampled.

Next implementation: extend the existing borrow.rs detector using write epochs
instead of touch epochs; build per-wire touch lists; classify every body query;
reject operand writes or unsupported degrees; emit source-only cell intervals,
decoded cost and coverage. Do not use the old rewrite function on these new
cells—it does not decode operand queries. Implement the decoder-aware emitter
only after structural feasibility and complete local controls pass.
