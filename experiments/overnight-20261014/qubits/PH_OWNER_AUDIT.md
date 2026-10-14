# Proposed pure-HR PH owner lifetime

Status: source audit for a proposed N275 schedule; no PH-owner integration,
component pass or Q692 result is claimed.

The eligible pure-HR guard excludes wide first-column SZ, HT/switch/done,
delayed/no-step, incoming switched layout and tt. On admitted input states,
PH=0 and sc.sw=0. Proposed q22 and q23 owners are PH and sc.sw.

The source `midg::middle` currently computes act(g) from `hr_lits` before
the HR search, clears it after leaving V, recomputes it for HR correction,
then clears it after correction. PH is one of those literals. The proposed
schedule keeps the first act live through correction and omits only the
intermediate clear/recompute pair on the eligible route. PH is therefore
read at entry while0 and at final clear after q22 has been erased.

Between those boundaries, the HR search/correction size gate `ge_k` reads
SZ/SY and uses c0/pzero/x128, the gate accumulator and flight bit. It does
not read PH. Ring adds use Q, ring, carries and the given control. The
preposition and paired parking record read SY and act; their control does
not read PH after PH becomes an owner. Before V, both proposed owners must
be prepositioned into guarded Q destinations and cleared. V's size and
reciprocal arithmetic do not read PH. The size-high donor normalization
reads act/SY/SZlow6; all these are disjoint from the proposed PH owner.

On the eligible pure-HR route, payload source pads are x128/pzero. The
delayed pad that also borrows PH is excluded. Payload transition helpers
borrow ring-top lanes and pool scratch, which are physically disjoint from
PH. The source stage callback between HR search and correction records
marks/profiles and can stop diagnostic generation; it emits no quantum
operation that requires a returned PH/act at that intermediate boundary.
Partial-stage diagnostic interpretation would need to acknowledge the
extended act and PH owner rather than treating them as the old flag state.

Correction must consume q22 and q23 before the final act clear. Only then
do later unprobe, map, switching and done logic receive PH0/sc.sw0 and a
returned act lane. Noneligible routes retain the original flag lifetime.
The proposal needs a complete source diff audit, native two-owner
preposition/correction checks and full payload/measurement tests before
being accepted. The actual packet's outside-guard quotient and N275
geometry assumptions remain independently unverified in this report.
