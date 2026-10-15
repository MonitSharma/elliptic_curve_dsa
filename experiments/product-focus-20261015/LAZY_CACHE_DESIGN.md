# Lazy caching of repeated AND values

This experiment is separate from the 692-qubit submission work. Its baseline is
the reproduced public C5 point-addition source. A passing rewrite test does not
repair that baseline's known arithmetic or phase counterexamples.

## Exact transformation argument

The existing conservative symbolic interpreter assigns immutable expressions
to quantum values. AND expressions are interned by their entire operand
expressions, with exact equality checks. When a size/cache limit is reached,
fresh atoms forget correlations; they cannot introduce an identity. A group
contains CCX operations whose unconditioned operand product is the same Boolean
function h at every occurrence. This is not a sampled-control census.

Each group obtains a physical wire proved zero at a condition-depth-zero entry.
The original stream does not touch that wire until the lease ends, except for
resets. Those original resets act on zero and can be omitted. Multiple leases
may coexist only on distinct physical wires. Starts and ends are condition-depth
zero boundaries, with ends processed first when leases meet. The last operand
pair remains unwritten through the end boundary.

An owned classical valid flag starts at zero. At an original occurrence with
classical predicate G:

1. If G and not valid, compute h into the leased wire and set valid.
2. If G, XOR the leased wire into the original target.

The maintained identity is `leased = valid * h`. If G is true, the second step
therefore performs the exact original CCX toggle. Original explicit conditions
are captured in a new condition-stack frame; original stack snapshots and
mutable input bits remain intact. The temporary flag is cleared after each use.

At lease end, measure the leased wire only under valid. The phase incurred is
`m * valid * h`; a CZ of the final original operand pair, under valid and m,
cancels it exactly. The leased wire returns to zero. All three owned classical
flags are unconditionally cleared. No additional logical qubit is introduced.

For any fixed original measurement transcript, a group with k active uses costs
one Toffoli when k is nonzero, instead of k. The saving is exactly
`max(k - 1, 0)` and is never negative. Added measurement outcomes cancel from
the net transformation. The challenge's deterministic transcript changes when
operations change, so a fresh unchanged benchmark remains mandatory.

## Evidence categories

- Opportunity scans and their depth-based estimates are unscored diagnostics.
  The estimates do not assume that nested or repeated predicates are independent
  when making a correctness decision; they only rank candidate leases.
- Native tests use the protected simulator and cover data/classical inputs,
  dirty newly owned classical slots, condition snapshots changed after a push,
  controls changed and restored, an intervening phase gate, a removed zero reset,
  multiple measurement words, and a detected missing-phase-correction fault.
- The final candidate changes only point-addition files. It preserves the old
  tail, source-bound tables, simulator, scorer, curve, manifests and toolchain.
- Independent replay reconstructs every emitted edit from the lease log and
  checks the entire candidate stream against that reconstruction. It aligns
  each original measurement event with its surviving candidate event, supplies
  independent outcomes for the newly added measurements, and checks all quantum
  slots, original classical slots, phase, and zero fresh flags.
- Complete official evaluation and event-aligned replay are separate. A failed
  official run has no qualified resource score, even if replay proves an exact
  saving relative to the failing baseline on the same inputs.

The first external native launcher failed to compile because its research-only
crate lacked a direct sha3 dependency. Its source/log are preserved as v2.
The corrected external v3 adds that dependency only to the research crate;
contestant Cargo files remain untouched. The two corrected native tests pass.

The completed full candidate failed official validation. Paired replay across
9,536 shots matched the baseline but measured only three saved Toffolis per
shot; depth-based estimates overpredicted reuse across mutually exclusive
branches. The extended external v4 suite passed three tests, adding overlapping
leases and all eight independent measurement patterns. See [the final report](REPORT.md)
for exact scope, failures and source bindings. No product record qualifies.
