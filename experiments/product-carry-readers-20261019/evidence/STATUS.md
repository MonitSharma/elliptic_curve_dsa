# Carry borrowing with exact read-only operand queries

Completed structural negative,19 October: run995501, profile1008320 and gap
inspection all exited0. Six decoder truth tables, five full capsule/proof
controls, twelve instrumented allocator controls and seven cover controls pass.
The scanner admits279,356 cells, only19 with operand reads. Costs are1 for
279,337 cells,2 for18 and4 forone. No complete candidate was emitted.

The instrumented strong-support allocator exactly reproduces every existing
report field and output hash82963f42fe238661b3207685fb9998f4862ee7193d9110a9c4fcc3753fae39d0.
It finds3,112 full-width regions. Even without the conservative all-top entry
filter,839 regions have no eligible disjoint capsule cover; no complete cover
exists. The all-top filter admits278,812 cells and gives the same negative.
This rules out this declared cover method on these peaks, not all arithmetic
representations. No statistical gate, nonce or scored resource result follows.

The scan's tentative save_end extends beyond the old measurement. cover.py
corrects this conservatively: only start+2 through the original Hmr inclusive
is counted, since the old carry may already be free after measurement. No
candidate used the tentative longer interval. Seven controls include this case.
Original scan Cargo bytes are retained as Cargo-scan.toml; the later profile
manifest is Cargo-profile.toml. Earlier SOURCE receipts remain immutable.

First uncovered peaks contain temporary AND fanouts. Their separate exact
dirty-output absorption experiment is in ../product-and-target-20261019.

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
