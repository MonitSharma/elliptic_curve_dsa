# Exact recomputation versus qubit width

## Final status: negative screen, 19 October afternoon

The detached job finished with actual exit code 0. All nine research-tool
tests passed. Removing 2,423 proved cache episodes left the conservative
peak unchanged at 1,234 (512 pinned registered wires and 722 scratch
lifetimes), with 8,251 predicted additional Toffolis. These are diagnostic
counts, not an unchanged official benchmark or a resource record. No
submission candidate, census gate, nonce search or upload was produced.

This screen completed sooner than the initial 10–20 minute estimate. It
does not justify expanding the same cache-removal search. The next research
direction is arithmetic-level scheduling or a different modular-division
construction, with the complete Q × T budget checked before qualification.
That work has not been launched by this experiment; there is no running
job behind this status and no reliable submission ETA.

Sources, rewrite certificates, source hashes, build/test logs, public-record
snapshot, lifetime profiles and actual launcher exit status are preserved
alongside this report. Large generated streams remain on the server.

## Original plan

Started19October2026 at14:06 Singapore on `smu_server`, detached PID536550.
Server directory: `/home/hclau/ecdsa_research/product-width-tradeoff-20261019`.
Launcher/log/PID/exit live in the sibling `product-pareto-20261019` directory
with prefix `width-tradeoff`. Uses four build threads, one scanner thread and
a64GiB address-space limit. Other users' jobs and old suspended experiments
remain untouched.

Public product parent was freshly checked: `9dc3798c`, Q1234/T761096,
product939192464. Its exact native stream is SHA256
`99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683`.

The earlier no-cost wire relabeling study found all1234 wires simultaneously
live. This experiment instead removes proved multi-read caches and recomputes
their AND at each reader. It may deliberately add Toffolis to free scratch
lifetimes. AtQ1233, up to617 additional rounded Toffolis relative to this
record can still improve the product. This is an objective budget, not a
measured result.

The symbolic matcher requires a clean initial cache, unconditional readers,
unchanged Boolean control products, and an isolated measurement with its
exact matching phase correction. Unknown flags are not guessed. Candidates
with up to64 readers are considered, using expression cap1024. Conflicting
rewrite endpoints are excluded. Tests cover multiple readers, changed controls,
extra measurement readers, unknown conditions and late input annotations.

The first screen compares conservative lifetime peaks before and after all
proved removals. Registered quantum wires stay pinned; only guaranteed resets
end scratch epochs, and uncleared final scratch stays live through the final
dirty-ancilla check. If peak width falls, the next step is selecting a low-cost
subset and implementing/verifying interval recoloring. If it does not, this
route is recorded as negative rather than expanded blindly.

No submission source is changed, no statistical gate is declared, and no nonce
is searched by this experiment. Generated streams and counts are diagnostic.
First screening was estimated at10–20 minutes; this is not a submission ETA.
