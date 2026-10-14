# N274 ownership prototypes: preserved failures and native repair pass

These are component experiments. Neither source has a generated full circuit
or an official point-addition result. Frozen N275-v2 and headflag-v1 evaluations
continue independently. Both prototypes preserve nonce34/control5, the public
schedule, Cargo files and protected harness. Candidate changes are confined to
six files under `src/point_add/`.

## V1: failed whole-column lifetime

`candidate-n274-v1.patch` has SHA256
`d592119990f5efde29f1117b6c31557e13073bb485be8f5e69737075256fa5d2`.
PID2640529 ran the source-attested `n274_` tests with 16GiB virtual memory,
four build threads and one runtime thread. It exited101 after six passing and
two failing tests; elapsed1:27.75 including compilation, peak643856KiB.

The six passes cover 6144 normalized A/B/pure-HR preposition cases, all256
SY words for the reciprocal partition, 512 donor normalization/care cases,
ordinary map extension, eleven ordinary/switch/counter maps including the
tight columns114..119, and controlled B0 replay. Each checks forward/inverse
values and sampled native measurement phase. These passes do not establish
the search lifetime of the proposed quotient owner.

The full-column HR_SY95 fixture at column36 and the exact original shot1170
division2 column35 payload fixture failed their integer/all-wire oracle.
The physical cause is explicit: `VB=6`, `ak=SX[VB]`, and the proposed
`q21=SX6` assign the same register to both the retained quotient and the
search flag. These roles coexist between search iterations. The isolated
preposition test does not exercise this overlap. The failed source, patch,
manifest, raw log and exit remain preserved; later filters were not reached.

## V2: Q118 ownership audit and helper-admission failure

The source-attested V2 patch and manifest are separate. Its component job
PID2653669 uses its own checkout and Cargo target, the same16GiB/4/1 limits,
and dedicated `evidence/n274-v2-components.log`, `.pid` and `.exit` files.
V2 exited101 with six passes and three failures, peak655264KiB,
elapsed1:20.45 including compilation. The new source-bound masked add passed
768 cases across all256 SY words and three target shifts. The other three
tests stopped while recording preposition: the inherited pure-HR helper
asserts `range.1+bit<128`, whereas q21 may park through index137.
These three tests did not reach arithmetic simulation. V2 source and failed
receipts remain preserved.

V3 uses the existing generalized `preposition_owned_qk` helper for q21 in
both A/B paths and the owner fixture. That helper accepts the complete
cycle and skips a self-target. No masking or arithmetic operation changes
between V2 and V3. PID2656623 runs its own source-attested checkout and Cargo
target; log `evidence/n274-v3-components.log`, `.pid` and `.exit`.
V3 completed with sixteen passes and one failure. It passed the768 masked-add
cases,6144 owner cases, nineteen new and thirteen inherited full columns,
the original1170 and8048 payloads, a structured q22 payload, donor/partition
tests, maps/counters and headflag self-fault checks. The first-HT3713 payload
oracle failed at seed0 with arithmetic, payload and scratch mismatches.
This precedes its phase assertion. A separate source-bound stage diagnostic
is localizing that regression; no all-measurement proof or full builder is
authorized while this known failure remains.

Several inherited output banners still literally say width692 or
q21_owner=SX6. Their actual constructors/assertions allocate691 wires and
the frozen production source assigns q21 toQ118. The receipt explicitly
retains this label limitation; the banners are not geometry evidence.

The admitted nine-reserve domain requires `SY+bitlen(q)<=138`; thus q21
can be nonzero only for SY<=116. On those states Q118 is above Y and originally
zero. SY117/118 has zero bit118, while SY119..128 may hold genuine Y there.
Gate21 and fetch21 use an exact full-eight-bit SY1..116 predicate. All other
size words remain explicitly distinguishable; inactive arbitrary Q118 values
must restore. This argument is an admitted recurrence bound, not a claim
about every denominator or schedule envelope.

Q118 is outside the R32 loans Q119..127. Production reciprocal helper banks
exclude Q118. Every middle add uses Q[..118] and a dirty tail; its separate
high-source add at weight118 is controlled by the exact full-eight-bit
SY>=119 predicate. Both paths exclude Q118 and the remaining high-Q lanes
from carry banks. The returned SX0 holds the high-source predicate only
around that add. The source-bound arithmetic fixture compares against an
independent integer add for all256 SY words, three target shifts and dirty
inactive owners, checking all wires, inverse and sampled phase.

The HR payload transition uses a short source Q[..118] on SY1..116 and the
original full source on SY117..255. It temporarily uses returned `ak=SX6`
for these disjoint predicates and returns it before any search flag reads.
This avoids storing q21 in a delayed-HR zero pad. The plain transition's
existing carry-to-tail path supplies the omitted zero source suffix.

The restoring ripple's carry into actual SY<=116 depends only on source
indices through SY, preceding Q118. Its unmodified up/down passes restore
every source bit regardless of the higher passenger. For SY>=119 Q118 is
the original Y bit. The whole-column and payload tests must still confirm
this source argument and measurement phase in context.

Pre21 swaps the non-last Q118 owner into cycle indexSY+21. In A its decoder
reads only low-seven SY bits because its target can be borrowed SY7. In B,
pre16 normally runs first, clearing SX1 before pre21 can target it at SY115.
SY102 is exceptional: pre16 targets Q118, so pre21 runs first there.
The implemented order is pre16-except102, pre21, pre16-only102; inverse order
is reversed. Self-target SY97 and boundaries102/115/116/117/118/119 are
explicit in the all256-word normalized owner test. Generic parking skips
these already-positioned quotient owners.

Original-packet HR/HT boundary columns and the original1170 payload are
fixed diagnostic fixtures. The original packet hash is retained with each
fixture receipt. No nonce or official packet is selected to improve a score.

## Alternative donor audit

The existing SZ6/7 loan is justified only on large SY, where the admitted
interval101..161 is injective modulo64. Several source columns have a
small-SY SZ envelope spanning at least128 values, for example column93
SZ110..246. A universal SZ7 search-flag loan cannot be reconstructed from
low-seven SZ bits there. A q21-live bound narrows that domain, but retaining
the original loan decision across q21=0 states requires an additional
reversible schedule. No such donor loan is implemented or claimed.

## V3 stage localization and V4 repair under test

A separate research checkout compares with/without-payload circuit states.
The first wrapper failed compilation because `Fd` does not implement Clone;
that source/log remains invalid-for-simulation. Its corrected second wrapper
completed the diagnostic with exit0, explicitly reporting the candidate's
failure rather than claiming correctness. Stages1..3 matched the arithmetic
reference; stage4 first differed at ring155 and acquired phase3 on two lanes.
The full failure persisted after later stages. This localizes the first
corruption to the inactive HR payload transition before the HT transition.

The concrete alias is in the full source padding: delayed-HR `src` includes
SX6 as a zero pad, while the new aggregate transition control also uses
SX6/ak. The unconditional ripple up-pass changes that source before the
down-pass uses it as a control. SY7 is also in the original pad list and
cannot simultaneously serve as an unmodified full-eight-bit selector.

V4 uses the existing plain transition carry-to-tail path for both source
branches: Q[..118] and Q[..128]. Neither source contains SX6 or SY7.
The precision path also omits the old pad-specific SY7 normalization, so
SY128 remains exactly128 when its full-word predicate is read. The legacy
nonprecision path is unchanged. The added original shot12/division1
HR_SY128 column67/j68 payload fixture checks dy0/1/p−1 and independent
varied values against the same true offset recurrence. It complements
the first-HT3713 regression and the original1170 q21 payload.

V4 component PID2673227 completed exit0: all18 selected tests pass. The five
groups contain10 N274,3 headflag (including two expected-fault checks),2 PH
owner,1 cap24 and2 reserve9 tests. This includes32 full arithmetic columns
(2048 lanes), five true payload oracles (256 lanes each),6144 normalized
preposition cases,768 production masked adds,512 donor cases, and map/counter
fixtures. Values, all-wire inverses and sampled native phase pass. Its fresh
checkout/target used16GiB virtual memory, four compile and one runtime thread.
The frozen six-file patch SHA256 is
`d471e44041f41919516f10ae5a472bd91a6ca91cf306dcb6ebb063799400e9e0`.

The independent fixed-kernel all-measurement proof completed exit0:
15 selected tests and378 exact audits pass, retaining every native value
and inverse assertion. Its input domain is the fixed64-lane batches in
these fixtures, with every independent R/HMR outcome quantified. This
includes the changed ordinary, B0 and eleven counter/switch maps. PID2686129
used627100KiB peak memory and97.85s test time. The kernel remains byte-equal
to SHA25672ab93a2fa1fd20bb3aad370aca9f6016ea9069013eaaa34d6b02d911d859622.
See `n274-v4-decision-receipt.json` and the complete source binding.

After reviewing both terminal pass guards, the coordinator launched the
full-stream generator at17:49:48UTC as wrapper2691773/native2692372.
The unchanged serializer equality test passed first (462 physical operations,
all fields). Generation and bounded scanning completed exit0 at18:06:45.
The external stream contains2258490788 operations and references691 qubits;
SHA256afc10211f95bd28a131dfd4a3a3c67284597c308b2a8a2e10682e56207f8ba93,
compressed4253925129 bytes. Its calculated operation-vector size is
126475484128 bytes; no operation vector was allocated by the bounded scan.
Generation took15:22.20/1044592KiB peak; scanning0:59.02/6912KiB.

These are generated diagnostics. A new independent counterexample from
the failed N275 official packet, shot2379 DIV2 column86, requires quotient
22815568 (25 bits). The unchanged N274 source caps that mixed step at22.
A source-bound native one-column expected-negative replay reproduces wrong
arithmetic, sampled phase garbage and failure of its all-wire inverse.
The passing component/phase fixture domain did not include this new input.
This known failure blocks an official evaluation of N274-v4. No grade or
resource record is claimed. See the separate
`n274-v4-generation-receipt.json` for active job and source identities.
The691-wire assertions describe these components and do not establish a
passing point-addition resource record.
