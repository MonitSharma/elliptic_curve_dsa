# N275/K16 source and component evidence

This is a source-isolated prototype, not a complete point-addition result.
The preserved compact submission and its nonce are unchanged. The native
constructors below allocate692 wires; no full emitted peak or scored count
has been measured.

## Source schedule

N275/K16 places the physical window at ring17. The large-SY reciprocal
uses24 remainder lanes: ring0–17, SX1–5 and ring274. Small-SY1–96 extends
this to32 lanes with Q120–127. Pure-HR guarded columns have a24-bit cap,
funding q22 on PH and q23 on SW. Other columns retain a22-bit cap. The
public schedule, payload digit cap24 and reserve9 remain fixed.

On admitted active shots, SY is1–128. For small-SY, even a24-bit quotient
parks at or below96+23=119, so Q120–127 are clean at every V call. First-HT
refill precedes the middle; delayed/no-step and done shots are inactive.
Inactive borrowed remainder words need not be zero: the restoring head
operation and its reverse are permutations on arbitrary words, as proved
in the preserved dirty-restoring component report. Full-SY positive cube
partitions distinguish96 from97 and preserve act as a separate control;
inactive high-bit aliases cannot activate a value-changing window update.
The source-bound finite audit `n275-selector-proof-v2.json` checks every128
admitted SY value, all256 SY words, all60 SZ encodings and1424 determinant-
bounded SZ/SY pairs. The largest small-SY parked index is119. Audit v1
stopped at a parsing assertion before evaluating predicates (its regex
also captured the function's slice type); the unchanged failed script is
preserved, and v2 corrects only that parser. This is not a candidate fault.

The determinant bound Z*Y<p implies SZ+SY<=257. Large-SY97–128 therefore
has SZ<=160. The source schedule's admitted lower bound101 is an additional
domain assumption, not a guarantee for arbitrary curve inputs. Sizes101–160
have an injective low-six encoding: SZ6 is low6>=37, and SZ7 is low6<=32.
The equality32 cube added for SZ160 is disjoint from low6<32. Normalization
and all care rotations use the same virtual-size rule while SZ6/7 carry
parked quotient data. Inactive words restore regardless of their high bits.

## Three-lane ordinary-map extension

The ordinary envelope257+EMAX21 requires three lanes beyond N275. A regular
non-switch map takes BQ, SW and the existing returned map ancilla. Stage8's
inverse Z probe has erased every SZ bit before map_stage starts. This also
erases SW's temporary ninth-SZ role in the wide first column. Non-switch
maps have no live switch flag; SW is outside the map's private flags, probes
and multiplier. The existing AND-carry loan guard excludes any owner taken
by the extension. The extension returns all owners before later stages.

The final B0 map cannot take SW: SW is its outer replay control, and pool-g
is its controlled replay helper. It instead takes BQ plus Q120 and Q119.
The done value R is below2^26, the map reads Q0–27, and the idle counter
lives at Q121–127. Both loaned Q bits are zero. Care normalization's support
closure lies below m+31=59, and masked map swapping reads only the operand
support. V2 explicitly excludes every extended-ring owner from frame_mul's
Q-tail carry vector, rather than relying on an unused distant carry prefix.

## Preserved native outcomes

Initial candidate patch
`eb8adf4d89de19ea335675d7b9db2856b229570a7dd9348220a1f2857b9b3376`
passed9 tests, exit0 at2026-10-14T13:36:25UTC. Wrapper PID2468409:
`/home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/n275-components.log`
and sibling `.pid`/`.exit`. Dedicated target was candidate-n275/target,
virtual-memory limit16GiB, build threads4, runtime threads1.

The tests cover wide-first ordinary map64 lanes; controlled B0 map64;
all256 SY selector words; SZ101/127/128/160, SY96/97/128 and inactive donor
aliases512; two quotient owners256; structured q22=1 payload256;
original8048 q23=1 payload256;13 prior exact columns832; and3713 first-HT
payload256. Arithmetic, all scratch/passenger words, forward/inverse
restoration and sampled native phase passed. The selector and donor
primitives have zero measurement coefficients because they are unitary.
Full-column/payload measurement-phase polynomials remain unproved here.
The initial test banners retained stale98/99 labels for two primitive
fixtures; the actual source inputs were96/97. V2 corrects those banners.

V2 patch
`10a0d56672b4327a341eca3a88fb0aaa34f1cad0a1e68c65ce30461b286cb17f`
adds explicit map carry exclusions and five exact native columns at
HR/HT SY96/97 and the wide first column (actual input Z has256 bits).
Its dedicated-target run passed10 tests, exit0 at2026-10-14T13:41:32UTC,
wrapper PID2472667. Log and receipt names are `n275-v2-components` in the
same remote evidence directory. Native groups took10.91,1.58,1.58 and32.61
seconds; full phase coefficient claims remain limited as above.
The exact selected inputs and original packet hash are in
`n275-v2-column-fixtures.json`; selecting component inputs does not modify
the official packet or source schedule. Both source versions and receipts
are preserved. Root's independent18048+512 denominator model screen is
predictive evidence, separate from physical owner and phase proofs.

At14:03UTC the coordinator confirmed the independent decision-diagram
checker passed all9 selected N275-v2 proof tests, including the new5
columns, prior13 columns, all three payload fixtures, owner/preposition,
donor and partition fixtures. This establishes phase on those fixed input
lanes for every independent measurement outcome, not every curve input.
Source binding is recorded in the coordinator's
`coordinator-qubit-decision-n275-v2/crate/complete-source-binding.json`.

The coordinator authorized full generation, launched14:05:36UTC as
wrapper PID2502104. Generation and bounded metadata completed exit0 at
14:29:18UTC. The stream has3832705108 operations,692 referenced qubits
and2390621 classical bits. Its SHA256 is
`ad1205994a3927ba76e90a086eadcf800d5876efe36425495cc8e83e21c6a26f`.
These are generated diagnostics, not scored results. The vector would
require199.89GiB, exceeding both128GiB and192GiB caps; a256GiB evaluation
allocation was authorized after fresh capacity inspection. Full-N Vec
capacity matched3832705108. The unchanged official evaluator is running
as PID2534382, wrapper2534318, cycle2532160, with one runtime thread and
the explicit full-stream symlink in a fresh protected harness. No complete
benchmark result or Q692 record is claimed.
