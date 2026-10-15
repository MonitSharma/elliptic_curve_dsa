# Three source-defined exact routes on official b5adb653

This study starts from the complete753721/Q1468 stream, SHA256
`1d8c05eeee7b43dd694506b5efe963c771461b7e690bc62f409947b2306b7d77`.
The current handoff and five most recent research-plan checkpoints were read,
alongside wide15 provenance and product-exact's accumulated negative list.
The old101T direct transfer, larger retained-cache saturation, dirty fanout,
global-LCA cleanup and disjoint restored-endpoint proposals are excluded.

1. **Same-target quadratic factorization (selected).** If two CCX gates add
   `a*b` and `a*c` to an unobserved target under the identical captured guard,
   all three controls retain their values across the interval, and the four
   wires are distinct, replace their combined action by `a*(b XOR c)`.
   A reversible CX conjugation on b implements the XOR control and restores b
   immediately. Complete cost: twoCCX become oneCCX plus twoCX, saving oneT
   whenever that guard executes, with deltaQ/MR/classical slots=0. No donor or
   retained-product reuse is required. This is a distributive refactor of
   different products, rather than a repeated-product cache or fanout query.
   Source feasibility is unknown; ripple carries often read the target too
   early. The selected census uses one fixed64-op window and strict fences.

2. **Three-product majority cone.** For one unobserved target, the exact
   identity `ab XOR ac XOR bc = a XOR ((a XOR b)*(a XOR c))` replaces threeCCX
   by oneCCX plus fiveCX (two reversible affine conjugations plus a targetCX).
   Complete saving: twoT per executing common guard, deltaQ/MR/B=0. It requires
   all three controls and the target to remain independently available, exact
   whole-cone read/guard fences, and phase equivalence of every use. This is a
   distinct three-product synthesis family, not a dirty-target fanout. It is
   not selected or scanned in this experiment.

3. **Execution-guard cofactor simplification.** For a CCX control q, prove
   universally that the gate's exact classical execution condition implies
   q=0 or q=1 using a bounded immutable prefix expression and full conditional
   reset semantics. The complete saving is oneT per firing gate: remove it for
   zero, or replace it by CX for one. It adds noQ/MR/B and leaves all original
   HMR events in place. Global constant simplification has been tried, but a
   nonconstant value restricted by a guard is a different proof obligation.
   This route needs a separate complete cofactor checker and must not infer
   classical control from observed packets. It is not selected or scanned.

No claim of available gain is made before structural census. Only hypothesis1
is selected. A zero/low-count result terminates this bounded front; no window
retuning, alternative ranking, renderer, candidate or sampled circuit follows
without a new explicit declaration and review.
