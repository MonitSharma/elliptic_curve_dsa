# N274 fixed predictive proposal and map-owner budget

Status: ideal-integer screen passes; three physical prototype failures are
preserved. The Q118-owner V4 repair passed18 native tests and15 independent
all-measurement tests (378 audits) on fixed component inputs. Full-stream
generation is running; no official evaluation of this source has launched.
See `N274_COMPONENTS.md` for frozen versions and ownership evidence.
No generated width, scored resource or passing point-addition
record is claimed. The frozen N275-v2 official evaluation and headflag-v1
generation are independent ongoing jobs.

Critical unresolved quotient owner: K15 puts q16..20 in SX1..5. Mixed cap22
also needs q21. Its V4 Q118 owner passed the component gate. PH q22 and SW q23
are proved only under the strict pure-HR guard. SX6/7 already belong to the
crossing reserve; SX6 is also the live search flag ak and cannot retain q21.
The second prototype loans Q118 and masks every source/carry read.
Observed absence of
mixed q21 inputs would not justify reducing the admitted quotient cap.

The fixed proposal uses N274/K15, R32 for SY1..95 with nine Q119..127 loans,
R23 for SY96..128, mixed quotient cap22 and admitted pure-HR cap24, reserve9,
and four ordinary map extension lanes. The effective map lengths remain278
ordinary and277 switch; this numerical assumption does not fund the wires.
With pure cap24 and SY≤95, parked quotient index is at most118, leaving the
nine proposed high-Q owners clear under the same admitted recurrence.
Large-SY determinant bounds give SZ≤161; source-admitted SZ≥101 makes the
low-six-bit representative unique across101..161. The donor reconstruction
must add residue33 to the prior high-SZ bit7 cases, and inactive aliases
must still restore arbitrary borrowed values.

`qubit-screen-n274.py` preserves the earlier coordinator recurrence model,
changing only the predeclared geometry, cutoff and large precision. PID2570632
completed exit0 at15:27:14UTC in15.18s, peak26912KiB. The original packet's
18048 divisions plus the same fixed-seed512 independent denominators flag
zero quotient-cap, parking, reciprocal or map-domain events. Maximum crossing
reserve is9; the sole original q≥2^22 case remains8048 in the strict pure-HR
guard. `n274-model-receipt.json` retains script/input hashes and limitations.
Fresh-input schedule envelopes, physical carries and phase are not modeled.

The current map pool supplies exactly ten clean owners: eight returned SZ
lanes and two pool flags. Existing map layout consumes nine core owners and
has one extension/parking lane. BQ+SW+that lane funds only three ordinary
extensions. N274 also grows switch extensions from two to three, so the
fourth owner cannot be supplied by merely changing the ordinary count.

Proposed map schedule:

1. For every non-B0 map, order sizes and erase the minimum-size SY word from
   Q or the ring using the existing source-directed `syp` records. Keep SX
   as the affine cut and CMPC as the ordering decision.
2. Move the map core's c0/e/g/v2 roles to the cleared SY lanes. Select BQ and
   the required additional clean pool lanes as extension owners. Select a
   separate free lane for f/h, retaining the remaining pool helpers.
3. Park the counter only when the existing `lean_park` condition requires
   it. Its first bit uses SW on both switch and non-switch columns; further
   bits use clean pool lanes. Outside `lean_park`, park is empty.
4. Embed, execute the map core, unembed, restore SY from the corresponding
   post-map source, undo ordering, erase the size probe, and return parked
   counter owners. No extension or helper may alias a map scratch, source,
   probe bank, cut or counter parking role while it is borrowed.

`qubit-n274-owner-budget-v2.py` applies the unchanged source schedule's
counter bound: first finish column96, maximum switch cntw5. After funding
extensions, parking and f/h, at least three helpers remain in every column.
The six tight ordinary parking columns114..119 have exactly three. This
checks a numerical budget, not the quantum lifetime or probe construction.
The initial budget script omitted the first SW parking owner in non-switch
maps and falsely reported deficits there. Its source and invalid_v1 result
are preserved; the corrected result is `n274-owner-budget-v2.json`.

The final B0 map retains the existing full-SY path and proposes BQ plus
Q120/Q119/Q118 as its four extensions. Its source operand fits28 bits,
done-counter owners are Q121..127, and normalization care is below bit59.
The controlled replay retains SW and pool g. Every operand read, rotation,
masked swap, carry loan and inverse must exclude the high-Q extension owners
while they hold ring data. The existing three-owner tests do not establish
the fourth owner's whole schedule.

Before generation, the source prototype needs full-SY reciprocal checks,
SZ161 and inactive donor checks, ordinary/switch map components, all tight
counter-parking columns and the four-owner B0 replay, inherited column and
payload oracles, fault tests, and independent all-measurement phase proofs.
The failed SX6/Q118 source versions and passing V4 components remain separate
experiments. Full generation of V4 is pending, and no N274 source has a
complete official benchmark result.
