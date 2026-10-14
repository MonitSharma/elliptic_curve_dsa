# Optimization proposal and continuation priorities

Updated for the CPU-server handoff on 14 October 2026. The objective is improvement
on all three fronts: width, Toffolis and product, in separate code tracks. The
initial scalar-only recommendation below is retained as historical analysis;
it no longer defines the user's objective or the product-leading revision.

Read [SERVER_HANDOFF.md](SERVER_HANDOFF.md) for exact resume commands, and
[parallel-campaign.md](parallel-campaign.md) for the measured experiments.
**No new original full-benchmark result has qualified.**

## Current priorities

1. **Qubits:** integrate `stage1_v_compact` in the Q694 Scheme G branch with a proved
   quotient-owner schedule. The 693-wire component and104-T per-call saving are
   tested; complete693-Q point addition remains unfinished. Solve SX6/q23 and
   the seven-lane crossing reserve before changing production constants.
2. **Toffolis:** pursue synthesis across the complete fold-core interface or
   shared phase-repair prefixes. The new phase-only CZ-reader pass is a checked
   primitive but finds zero savings in both leading final streams. The earlier
   implication cleanup saves only about1.49T and fails its official packet.
3. **Product:** use Q1234 source `c5bb1ec8`. Complete, re-prove missing square guard
   lifetimes rather than copying partial matched tables. Our five partial
   transplants were not qualified. New width/gate combinations must beat939885972.

The saved records to beat are Q694, T761156, and product939885972. For product,
use `floor((939885972 - 1) / Q)` as the strict maximum rounded T at a chosen width;
the940027660 thresholds in the archived section are obsolete for the newer leader.

Universal arithmetic proofs, finite gate fixtures, population estimates, and a
passing canonical packet are different evidence. Existing leaders are approximate;
therefore maintain paired and independent checks and do not equate an identity
rewrite with a universally exact full oracle. No nonce search was performed here.

## Archived initial analysis — earlier saved snapshot

The following proposal used1,557 records/41 frontier points and the older
Q1235 product leader. Its figures, initial product-only preference and untested
forecast are historical. The current multi-objective priorities above supersede them.

---

# Proposal to improve the ECDSA.fail record

Prepared 14 October 2026 (Asia/Singapore). Recommendation: keep the current
1,235-qubit Leapfrog circuit and search for exact savings in its repeated fold
cores. The first substantial experiment should synthesize the quotient
construction and its addend outputs together, rather than optimize each side of
that interface separately. This is a research hypothesis, not a measured win.

## What was reviewed

The public API returned 1,557 records: 626 accepted, 700 rejected, 228 failed,
and 3 cancelled. All records were screened by status and official metrics;
1,541 available submission notes were saved and indexed. Detailed reading
focused on the current leader and its predecessors, the strongest narrower
circuits, recent low-qubit results, and relevant unsuccessful approaches.
This is not a claim to have independently reproduced every circuit or manually
read every historical note in full.

There are 1,216 records with positive, consistent official scores that either
were accepted or were rejected specifically because their product did not
improve the incumbent. They yield 41 nondominated resource pairs. Benchmark
failures, claimed-only scores, and other rejection categories are excluded.
The API currently reports **scalar** promotion mode, although the website also
displays a Pareto chart. Score-only rejection therefore does not necessarily
mean an invalid circuit. See [the benchmark metadata](https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74)
and [all submission records](https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74/submissions).

The full derived frontier is in `docs/frontier-results.md`; the data and notes
are under `research-output/`. The baseline we already reproduced matches the
live best score and source commit `b3c9fdd6`.

## The results that determine our choice

| Circuit / resource region | Peak Q | Rounded average T | Product | Interpretation |
|---|---:|---:|---:|---|
| Current Leapfrog leader | 1,235 | 761,156 | 940,027,660 | Our starting circuit and the best product |
| Strongest narrower Skywalk product | 1,170 | 946,553 | 1,107,467,010 | About 17.8% above the best product |
| Lilypad-G, narrow arithmetic route | 877 | 2,331,376 | 2,044,616,752 | About 2.18 times the best product |
| Frogdrop at Q770 | 770 | 115,382,810 | 88,844,763,700 | Very expensive in gates |
| Lowest reported scored width, Scheme G | 694 | 336,751,889 | 233,705,810,966 | About 249 times the best product |

These are distinct resource tradeoffs. One new circuit need not simultaneously
beat the smallest width and the lowest gate count to establish a new product
record. Our first objective should be the official scalar product.

Sources: [Leapfrog leader](https://api.ecdsa.fail/api/submissions/26dd1d00-8e45-4f13-adcf-5eac665ca15f),
[Skywalk Q1170](https://api.ecdsa.fail/api/submissions/b72ce1ae-c5e0-46b8-a562-b5f1ac4d074a),
[Lilypad Q877](https://api.ecdsa.fail/api/submissions/7be7b9a5-99c3-4fd1-9d27-310f4f2d33c1),
[Frogdrop Q770](https://api.ecdsa.fail/api/submissions/978d89f5-6938-48a3-b37a-b5131326e9e2),
[Scheme G Q694](https://api.ecdsa.fail/api/submissions/3bcef1d9-8c99-4cb8-b89b-0b2a774e19a5).

## A limitation of the benchmark result

Our baseline passes its official 9,024-shot packet. That does not establish
correctness on every possible input. The leader's author reports failures on
other packets and describes approximate components and a searched identity-tail
nonce. The source also contains that tail. Changing the circuit changes its
Fiat-Shamir test inputs and can change the measured mean even without a useful
arithmetic improvement.

Consequently, an optimization must be assessed on common inputs and with
measurement histories aligned where needed. An exact local rewrite should
preserve the incumbent's values, cleanup and phase behavior within its proved
domain; it does not make the inherited approximate circuit universally exact.
The final official benchmark remains necessary, but is insufficient evidence
of a population improvement by itself.

## Where the cost is

Our saved builder diagnostics give the following expected executed counts
before the final stream passes. They are a location guide, not a decomposition
of the final official score.

| Stage | Builder expected T | Share of builder total |
|---|---:|---:|
| Division | 358,258.0 | 47.0% |
| Multiplication | 362,967.9 | 47.6% |
| Square | 40,238.0 | 5.3% |
| Coordinate operations | 635.0 | 0.1% |

The terminal clearing step then saves 56 expected T, leaving builder total
762,042.9 before the later stream passes.

Division and multiplication dominate. The current recipe already contains
fused one-fold payload ticks, early wire recycling, deferred rail-boundary
phase repair, and several exact stream rewrites. Simply adding generic
measurement-based uncomputation would repeat existing work.

## Main experiment: synthesize across the fold-core interface

In `src/point_add/y15_onefold.rs`, the forward fold constructs a small signed
quantity `k`, then feeds its eight-bit representation into `Y16_FWD_GATES` to
produce the correction fields. The reverse fold similarly constructs `n`
before `Y16_REV_GATES`. Those addend programs use 14 and 12 AND gates
respectively; construction of their inputs also consumes nonlinear work.

The proposed change is to synthesize the **complete collection of needed
outputs directly from the original low bits and shift/sign controls**:

1. Extract a precise Boolean reference for the quotient inputs, correction
   fields, and any carries actually read downstream.
2. Search XOR/AND networks jointly across the construction/addend boundary,
   allowing shared intermediate products. Keep the same mathematical outputs
   and the same admissible domain. Any restricted domain must be proved from
   the caller, not inferred from random samples.
3. Include cleanup and phase repair in the objective. A network with fewer
   forward ANDs may still cost more when uncomputed or require too many live
   wires. Rank by complete expected Toffolis at peak Q no greater than 1,235.
4. Test the resulting core independently before porting it into the repeated
   forward and reverse ticks. Try forward and reverse variants separately
   before combining them.

Why it is plausible: the source exposes two separately optimized nonlinear
stages, while the outputs are related small integer functions. Joint synthesis
can sometimes reuse products that a fixed eight-bit interface obscures.
Even one saved nonlinear operation per repeated occurrence could accumulate
into hundreds of Toffolis. Actual occurrence counts, conditional execution,
and cleanup costs must be measured; no saving is guaranteed. The public-note
search found no documented joint synthesis of this specific interface, which
is a lead rather than proof of novelty.

Start with exact truth-table checks of the small functions, then use Boolean
or SAT equivalence to verify value and phase identities. Do not reduce the
walk length, arithmetic windows, or compare widths in this experiment.

**Research target:** save 1,000 rounded average Toffolis at Q1235. That would
give T=760,156 and score **938,792,660**, a 0.131% product improvement. This is
a stretch target for the experiment, not a forecast.

## Two complementary experiments

**A small first check: finish the square's remaining reader guards.** The
leader's note identifies 370 depth-6 and 182 depth-7 configurations not yet
run. Under its per-site saving formula, all of those qualifying would save
only `370/64 + 182/128 = 7.203125` expected Toffolis. This is useful for
validating our extraction/proof workflow but is too small to be the main
strategy. Unscreened deeper sites may fail the required premises, and their
returns diminish. Source: the leader's submission, section 4.

**A second substantial route: shared phase-repair recomputation.** Search
remaining erased carry values that share a recomputation prefix or are
regenerated later. Either share the Boolean work needed to repay their phases
or defer a repair to a proved identical value. Keep every measurement debt
keyed to its exact operands and condition, and assert that all debts are
consumed. This extends the existing idea only at newly identified sites:
`Y28_DEFER` already covers 208 rail-boundary debts in our baseline. Lilypad's
paired carry-repair layer is evidence that this mechanism can have substantial
value in another architecture, not evidence that its reported saving ports
unchanged to Leapfrog. See [Lilypad's layer description](https://api.ecdsa.fail/api/submissions/457ccb7a-4436-4e8c-8e8c-f7d22c3c81b5).

## When narrowing the circuit is worthwhile

The score uses rounded T. To beat 940,027,660, the integer gate limit is
`floor((940027660 - 1) / Q)`:

| Candidate Q | Maximum rounded T for a strict win |
|---:|---:|
| 1,235 | 761,155 |
| 1,234 | 761,772 |
| 1,230 | 764,250 |
| 1,200 | 783,356 |
| 1,170 | 803,442 |
| 893 | 1,052,662 |
| 877 | 1,071,867 |

At Q1234 we can afford 616 extra rounded Toffolis relative to today's
761,156. The leader's author estimates a cap reduction would cost about 665,
so it misses by roughly 49. The raw estimate is unverified here and a lower
cap can also cause a different subroutine to own the physical peak. Joint
core savings could make the combined change worthwhile, but target a margin
of at least hundreds of T rather than a noise-sized win. All divide,
multiply and square peaks must be replanned together.

Starting with Q1170 would require about a 15.1% gate reduction to win. Q877
would require about 54%. Those are attractive longer research programs but
have a much larger first hurdle than improving the circuit we already have.

## Verification and stopping rules

1. Preserve the baseline source and ops packet. Emit stage-tagged cost and
   live-wire traces from contestant-side diagnostics; keep the harness intact.
2. Prove each replacement on its complete small domain, including phase and
   scratch. A missing phase correction, wrong carry, or dirty scratch should
   make deliberate negative-control variants fail.
3. Compare base and candidate on the same fresh inputs. Align corresponding
   measurement words or explicitly account for changes in measurement order.
   Measure output disagreements and all three failure channels separately.
4. Screen with a small paired corpus, expand promising candidates, then use
   a held-out corpus to avoid choosing a sampling fluctuation. Population
   checks supplement proofs; they cannot prove exactness by themselves.
5. Stop a core search if it cannot save complete Toffoli cost under the width
   constraint. Stop a Q1234 route if its measured net T remains above 761,772.
6. Rebuild the integrated source and run the unchanged official benchmark.
   Existing rewrite tables are bound to full prefix hashes and op indices;
   re-discover/revalidate them when the underlying gate stream changes.
   Never simply disable their checks or change a hash to force acceptance.

The work is technically related to the Classiq optimization effort through
dependency analysis, shared subexpressions, ancilla lifetime and constrained
resynthesis. Here the winning objective is Toffoli count times peak logical
qubits, so a shallower circuit is useful only if it also improves those
resources.
