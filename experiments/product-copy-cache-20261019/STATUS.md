# Reversible idle-wire cache with a clean consuming target

Declared before implementation/source run on19 October2026. Both larger ANF
screens found0 current-wire substitutions; do not repeat their fixed scans.
Test a temporal cache instead, on the same frozen classical12 source only.
All source9 search and source12 gate/runtime jobs remain unchanged.

At an unconditional CCX(a,b,t), reroute its AND into an existing idle zero
wire s, then CX(s,t). This has the original target effect and leaves s=a*b.
At a later unconditional CCX(c,d,u) with u provably zero and c*d=a*b,
replace it with CX(s,u); CX(u,s). The later clean target now holds the
product and s returns to zero. Exactly one executed Toffoli disappears,
with no additional measurement/reset/classical bit/physical qubit. This
needs no assumption that the first target was zero.

Only exact fixed256-term/degree12 polynomials may certify product equality
and the later zero target. The original source must not touch s anywhere
in the closed capture/consume interval, and s must be zero in the original
state at consumption (hence also at capture). Exclude every quantum ABI
wire. Added cache intervals on one slot and original CCX endpoints must
be disjoint. Choose the lowest permitted existing slot deterministically.
No conditional captures/consumptions, extra R/Hmr, quantum/classical ABI
assumptions, nonce packet observations, or score-based tuning.

Before source screening, require exhaustive primitive/full-simulator controls
for arbitrary first target, later clean target, Hmr and physical RNG,
algebraically equal different controls, no-idle refusal, phase-only touch,
dirty consuming target, overlapping intervals and conditional refusal.
Disabled mode must reproduce the completed ANF256 report and full hash.
Any changed source then needs512 complete q/c/phase/physical-RNG controls.
Static predictions are component diagnostics, not a scored record. Positive
results still need source-bound independent identities/idle-interval audit,
native src/point_add-only reproduction and their own final statistical gate.

One local Ubuntu core/12GiB, portable verified compiler, dedicated nohup,
PID/exit/log and exact source/stream hashes. Launch only after the prior
current-wire witness experiment is authoritatively terminal.
