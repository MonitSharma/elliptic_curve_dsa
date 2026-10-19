# Two-target Toffoli absorbed into an existing dirty output

Completed bounded source-only negative,19 October2026. PID1102294 exited0.
All9 identity/guard/mutation/fence controls pass. Each of the six fixed cases
finds zero eligible pairs; no rewritten circuit is emitted. This excludes only
the declared physical-wire/guard/root/untouched-target query with gaps<=4096,
not broader algebraic identities or arbitrary long windows. No native source,
census, nonce, complete executed-T saving or scored result is claimed.

Declared19 October2026 before this screen. Six fixed source-only cases:
public0c3a0751 and its audited physical-RNG materialized-guard permutation,
each at original-operation gap limits1,64,4096. Exact source hashes are read
from preserved public/guard audit records before execution. No statistical
gate, nonce selection or packet-content optimization is involved.

CCX(A,B,D); CCX(A,B,E) is exactly CX(D,E); CCX(A,B,D); CX(D,E)
for distinct A,B,D,E and arbitrary dirty D/E. With a shared unchanged direct
condition F, guard all three replacement gates by F. Both original CCXs must
be at root scope; A/B and F must not be written in between, D must have no
touch since the first CCX, and E no touch after that position. Metadata/debug
fences reject a pair. Independent intervening operations are preserved.

This differs from the old strict dirty-fanout screen, which sought at least
three consecutive CCXs and a restored outside donor costing two Toffolis.
The new identity can save one Toffoli from a pair with no outside donor.
Earlier source queries do not establish this declared pair query's outcome.

Use exhaustive basis/flag/phase controls and negative target/control/condition
mutation checks before source execution. Pair selection is greedy over all
unused same-key CCXs inside the declared window. Keep physical RNG order and
all classical state unchanged. Positive source counts are not complete measured
T savings or scored results: require full integration, native src/point_add-only
reproduction, complete measured Q/T, new ordinary-RNG gate and final benchmark.
One build/screen thread,32GiB cap, after the current combined guard job ends.
