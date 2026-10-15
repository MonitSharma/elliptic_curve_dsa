# Rail arithmetic continuation, 15 October 2026

**No qualified Toffoli or product improvement.** This completed experiment
localizes fourteen more fixed-packet failures, proves a widened choice primitive,
and establishes that fixing one overflow can expose another at the next tick.
All seven launches are terminal. No official benchmark or submission was run.

## Public targets

The public API fetched at **10:28 Singapore** now gives minimum product
**939,347,948 = Q1234 × T761,222**, revision `4b2ec52f`. Minimum Toffolis
remains **761,156 at Q1235**. Strict targets are T ≤ 761,155 and
Q × T ≤ 939,347,947. At Q1235 a product improvement requires T ≤ 760,605;
at Q1234 it requires T ≤ 761,221. These are independently scored public
records, not reproductions performed in this experiment.
[Dated API snapshot and raw-input hashes](public-frontier.json).

The README figures and current public data have been refreshed. Existing local
Q692 evidence and all previous failed or passing experiments remain preserved.

## Forward rail diagnosis

The corrected observer inspects the original B3 forward rail maps **before**
the retrospective Y33 measurement rewrite. At each tick it checks the actual
incoming rails and recorded signs/shifts against exact field arithmetic. A
separate Python calculation confirms the fourteen packet counterexamples with
unbounded signed integers: every division is exact, and every discrepancy is a
power of two. Three cases corrupt the source rail rather than the target.

| Preserved family | Inputs | Forward rail failures | Final wrong points |
|---|---:|---:|---:|
| Independent | 256 | 0 | 1 |
| Structured | 256 | 129 phase/shot pairs | 189 |
| Earlier cache candidate packet | 9,024 | 14 distinct shots | 16 |

All fourteen packet rail failures occur among the sixteen wrong final points.
The two remaining packet failures, shots **421 and 6972**, have no observed
forward rail-map failure; their previously observed payload/endpoint issues
remain separate. A forward-only diagnostic does not exclude reverse failures,
prove the tape choices or convergence, or identify the first error anywhere in
the complete circuit.

The observation simulator matches the unchanged protected simulator on every
quantum slot, classical slot, phase, and executed count over all 9,536 inputs.
The generated final raw stream is byte-identical to the preserved original B3
raw stream. The provisional first tracer observed after Y33 at pre-Y33 indices;
it is retained but superseded by the explicitly pre-Y33 second version.
[Trace](trace-v2.log) · [Independent certificates](trace-analysis.json) ·
[Reproduction script](analyze-trace.py).

## One-bit choice repair and its limits

The previously diagnosed multiply tick 109 needs a 60-bit signed even result,
but its original choice operation uses only 59 physical output bits. The
experiment raises both the choice and pre-barrel widths by one. The first
ordinary build stops with exit 101: the old fixed allocator table has no entry
for the changed forward tick 109. Its failure and exact patch are preserved.

A matched baseline and repair then use the source's existing dynamic allocator
branch, which checks scratch return and restores the entry allocation order.
Optional optimizations bound to the old stream are omitted; their code, tables,
and assertions remain intact. Both ordinary builds succeed. The repair also
retains the earlier tick-104 fold mitigation, without its now-unneeded fixed
allocator adapter.

The choice primitive passes **43,680 exhaustive signed-input cases at widths
3–8**, plus the saved width-60 case. The archived unchanged decision-diagram
kernel proves all internal measurement outcomes for forward and inverse maps,
checking every quantum slot and zero incremental phase. Native checks agree
under three measurement patterns with dirty classical scratch and incoming
phase. The original narrow output reproduces the signed overflow; an added
phase fault is detected. This proves the finite primitive domain, not a
complete tick or point-addition circuit.
[Exact test source](rail_choice_tests.rs) · [Passing test log](choice-tests.log).

## Complete circuit outcomes

| Fixed input family | Baseline wrong points | Repair wrong points |
|---|---:|---:|
| Independent, 256 | 1 | 0 |
| Structured, 256 | 189 | 189 |
| Earlier cache packet, 9,024 | 16 | 16 |
| Earlier fifteen counterexamples | 15 | 15 |

Every replay has zero dirty final quantum-scratch batches. The repaired
independent packet also has zero phase failures. Other families retain phase
failures. Their measurement events are **not aligned** across sources, so
differences in phase counts or total executed gates are not paired improvements.
The fifteen-point replay has inactive simulator lanes; its raw executed total
must not be converted to a per-point cost.

The focused pre-Y33 trace explains why known point 249 remains wrong:

- Baseline first multiply rail error: **tick 109**, exact target
  `90,838,982,128,839,835`, observed target `−53,276,205,947,016,037`.
- The repaired tick 109 is correct. Its first multiply rail error moves to
  **tick 110**, which also overflows on the corrected trajectory.
- The repaired walk then ends with rails **(−3, 3)**, violating the endpoint's
  ±1 assumption. The complete result now has both x and y wrong; the baseline
  had only y wrong. This is not an accepted repair.

The result demonstrates a sequence of width/convergence failures, rather than
an isolated tick-109 defect. Correcting one step changes the later trajectory;
checking only that local step is insufficient.

## Evidence and next work

[Terminal receipt](evidence/receipt.json) binds eight isolated checkouts, exact
tracked patches and added source files, input packets, logs, binary hashes,
stream hashes, preflights, process IDs, and exit codes. All seventeen tracked
files outside `src/point_add/` are byte-identical to the original revision in
each checkout. Existing local submodule edits were untouched. Large streams
remain in `/home/hclau/ecdsa_research/rail-repair-20261015/`.

Next arithmetic work needs a width invariant spanning the forward/reverse
trajectory and endpoint, including zero-denominator structured multiplication.
Do not treat further one-tick patches as complete repairs. Independently, the
exact caching work remains a route to lower executed Toffolis; investigate its
symbolic-expression retention limits and measure any extra savings with aligned
events. Neither objective permits promoting failed-stream diagnostic counts to
scores or selecting a lucky hash-derived packet.
