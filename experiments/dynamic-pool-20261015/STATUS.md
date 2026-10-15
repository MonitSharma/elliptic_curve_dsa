# Dynamic allocator repair and wider Toffoli control

Completed 15 October 2026. Both jobs exited 0. **No qualified score.**
The new checkpoint fixes the wider circuit's construction failure while
retaining ownership assertions. The unchanged-width circuit is byte-identical
to its parent; the wider circuit still fails arithmetic and phase checks.

## Repair and verification

The old cap1536 failure had exactly one extra free wire, ID1364, with no
missing or duplicate wires. Its snapshot did not retain the fresh-ID boundary.
The repair records that boundary and the live count, requires every newly
allocated ID to be returned, checks the complete free-wire multiset, and
retains the original classical-bit checks. It restores old stack priority
with fresh returned IDs below it in lazy-allocation order. The original
pinned-table path and `y42_alloc_set` assertions remain unchanged.

Six allocator tests pass in both isolated builds. They cover returned fresh
capacity, unchanged restoration, live leaks, a balanced old-wire leak/illegal
free, duplicate frees, and classical-bit leaks. These are bookkeeping tests;
they do not establish quantum cleanliness. Fixed replay separately reports
zero dirty batches in all three input families.

The cap1267 control is byte-identical to carry-frame/unseeded-b3:
`b26a283aab80a23b36ba7ef75d3d35b5f25d97dde759270a53a45691603144d0`.
The cap1536 stream is:
`95e771bae57bd96e75c11b569faf2f87cd7dfa52b227b40dd16e40a301d8e122`.
Both source patches change only `src/point_add/`; protected files match B3.

## Wider circuit: diagnostics only

The builder reports peak1464, versus1282 for the parent. On independent256,
executed T totals fall from197312724 to192951219 (about2.21%). This is a
fixed-packet diagnostic comparison, not an event-aligned optimization proof
or benchmark score. Measurement events differ between circuits. Multiplying
those diagnostic means by the reported peaks would increase product by about
11.7%; this width tradeoff is not promising for the product objective.

| Fixed family | Shots | Wrong values | Phase shots | Dirty batches |
|---|---:|---:|---:|---:|
| Independent | 256 | 0 | 0 | 0 |
| Structured | 256 | 128 | 129 | 0 |
| Preserved candidate | 9024 | 5 | 5 | 0 |

The candidate's five wrong-value indices remain562,720,2777,3447,8322.
Structured failures retain the zero-multiplicand cases. All-measurement BDD
analysis of the first fixed zero-slope input finds a nonzero phase polynomial.
The protected native simulator verifies a single-outcome counterexample:
MR278924 / operation3610757, Hmr qubit221, bit1566. Flipping that measurement
changes phase0 to all ones while keeping the point value correct.
This exact result covers one fixed input, not all possible inputs.

## Evidence and next work

Control PID3135762 and wide PID3135763 are terminal. All55 archived artifacts,
two candidate patches and the external proof-runner patch pass
[local verification](local-verification.json). The [receipt](evidence/receipt.json)
retains protected-source hashes, fixed packets, binary and stream hashes,
test results, failure sets, logs and statuses. The original failed cap1536
attempt remains archived in the preceding experiment.

Retain this allocator repair for future width tradeoffs. Attribute the new
phase witness to its source before selecting a general comparison repair;
the wider setting itself does not solve correctness. Continue treating lower
Toffolis and lower product independently. No failed circuit enters the plots.

The public refresh analyzed at12:30 Singapore reports T761156 and product
939347948 unchanged, but a new width minimum682. README and public figures
now reflect1566 submissions,1225 eligible records and46 frontier points.
The historical local Q692 pass is preserved and no longer below the public
width minimum. Both leaderboard/plot admission test suites pass (5 tests each).
