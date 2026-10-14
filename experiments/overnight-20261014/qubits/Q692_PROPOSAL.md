# Q692 ownership proposal, not an implemented result

Status: proposed schedule awaiting independent source-model screening,
complete source audit and native components. No width reduction is claimed.

N275/K16 would provide the physical window at ring17 and five returned SX
owners for q17–q21. A compact24-bit reciprocal remainder can use
ring0–ring17, SX1–SX5 and ring274. For small-SY, eight Q loans at120–127
would extend it to32bits; cutoff96 keeps all parked QB24 bits below120.
LargeSY97–128 implies SZ<=160, so the low-six SZ representation can be
extended from101–159 to101–160 by including low-six value32 in the SZ7
normalization/care predicate.

This proposal keeps a22-bit quotient cap in mixed/crossing and unsupported
columns. An independent audit must check whether the preserved packet has
any quotient at least2^22 outside the eligible pure-HR guard, including the
tail and wide first column. It must also check the N275 map/cut geometry and
mixed K24/K32 reciprocal predicates. Passing such a predictive packet audit
would not qualify the new hash-derived official packet or prove all inputs.

Pure-HR columns could fund q22/q23 on PH/sc.sw respectively, with the same
wide/incoming-switch exclusions as `CAP24_PURE_HR.md`. PH starts0 there.
Unlike sc.sw, PH is read by `hr_lits`, so its loan requires extending the
existing act(g) lifetime from initial HR entry through the entire HR
correction. The intervening clear/recompute pair would be omitted on this
route; act is cleared only after correction has erased q22 and restored PH0.
All other PH reads and payload padding must be audited before integration.

Both external owners would be prepositioned into Q[SY+22/23] before V and
their ordinary park swaps skipped. A direct multi-owner preposition helper
would need to exclude self aliases and retain the current guard's strict
Q destination bound; the one-owner last-slot helper is insufficient by
itself. The existing return must restore both owners before correction,
which consumes their bits. The extended act must not enter any later map,
size or payload scratch lifetime.

The complete source schedule, all four V boundaries, first HT/delayed
crossings, restricted PH lifetime, inactive paths and payload/measurement
phase remain required checks. The proposal does not justify running an
unchanged full benchmark or labeling a component692-wire allocation as a
complete point-addition record.
