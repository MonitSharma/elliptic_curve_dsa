# Source-bound payload model diagnosis and correction

Research only; no direct rejection, nonce search, circuit modification or
submission is enabled by this experiment. The source is the frozen public
product record `4b2ec52fc55da796aa8f5ef851290297e8706424`.

## Four false positives explained

The old model used a57-bit forward fold window through tick55, while the
public source uses57 bits through tick99 (`y15_onefold.rs::fold_window`).
The four false positives first diverged locally at these payload ticks:

| Preserved census batch/lane | Divide tick | Incorrect modeled loss |
|---|---:|---:|
| 694/38 | 91 | 2^51 |
| 1318/50 | 86 | 2^51 |
| 1658/27 | 84 | 2^52 |
| 3184/27 | 87 | 2^50 |

The sole55→99 source-setting correction removes all four false positives on
the complete262144-shot preserved population: **243TP,0FP,261713TN,7FN,
181UNKNOWN** (all unknown inputs are known value failures). It preserves all
243 previous true positives. The run used eight workers and219.31 seconds.
This is finite validation, not an all-input certificate or a new fresh census.
The original incorrect model and its divergence receipts are retained.

## Independent gate-inert observation

A private source copy traces35 inputs: the four false positives, eight nearby
passing controls, eight true positives, seven missed failures and eight unknowns.
It records9625 payload transitions plus forward/reverse rails and coordinate
boundaries. Every qubit, classical bit, phase and executed Toffoli count agrees
with the protected simulator. The complete final stream remains byte-identical:

`2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e`.

All four false-positive inputs pass the raw-builder circuit. To independently
exclude inherited-cut repairs, the final stream was reversed through74 gate
deletions and70 CCX→CX reductions. All144 source neighbourhood SHA3 anchors
match exactly. These inputs also pass before census edits, and activate no
nonequivalent edit on either path. Thus their false positives were model
window errors, rather than accidental repairs by inherited cuts.

`before-census.bin` remains on the server; its SHA256 is recorded separately.
`cut-guards.csv` exports the exact original indices and local inactive predicates.
All144 are CCX edits. The local Boolean equivalence lemma passes2304 exhaustive
assignments. This does not prove the arithmetic model can evaluate those
internal control wires cheaply or soundly; that obligation remains open.

## Separate source-exact seed and tick0 model

The private `source-t0-model/` version additionally implements the literal
finite53-bit seed halving and `P3_T0_ONE_ADD` integer expression. It retains
unsigned source seed/tick0 words. The threshold-only corrected version remains
separate, so the population correction is independently reproducible.

The production seed and optimized tick0 gates match the integer formulas on
928 boundary cases at the exact live budget1105, including128 cases where the
seed differs from ideal modular halving. Every qubit, bit, phase and Toffoli
agrees with the protected simulator. The exported primitive stream is
`t0-probe-ops.bin`; it is component-only.

Two useful source-contract counterexamples are preserved:

* T=1: the53-bit seed halve differs from ideal halving by2^52.
* T=f=2^32+977, ideal seedS=2^255, signs=(1,0,1), extra=0: the optimized source
  output is correct while the old generic three-add model differs by+2^54.
  Eight independent protected MR replays confirm this primitive witness.

No full valid-curve point-addition counterexample with those special payloads
is claimed. They demonstrate primitive contracts that a universal arithmetic
certificate must handle. `CONTRACTS.md` and `source_payload.py` give the exact
source-derived formulas and the remaining proof obligations.

The separate model's35 state-boundary fixtures check every seed; all first12
false-positive/control inputs match every checked stage. Overall matches are
35/35 seeds,31/35 divide payloads,26/35 coupled square states,30/35 multiply
payloads on observed inputs, and35/35 recovered multiply denominators. The
remaining mismatches coincide with documented dirty-loan, square-window and
late-cell limitations; they have not been silently admitted as certified cases.

The separate Python implementation's928-case table passes protected component
replay for **all eight MR seeds (7424 shots)**, with every qubit, bit, phase
and Toffoli count equal. Its eight-seed one-sided witness also passes. The full
262144-input population completes in253.59 seconds with seven workers:
**243TP,0FP,261713TN,7FN,181UNKNOWN**, unchanged from the threshold-only fix.

The original32-entry state-boundary fixture set also passes all eight passing
controls. Its model matches are28/32 divide payloads,28/32 coupled square
states,27/32 multiply payloads on observed inputs, and32/32 recovered multiply
denominators. Those original fixtures lack seed-entry logs, so no new claim
about their seed-word observation is made. The corresponding35-entry set
provides the direct35/35 seed checks. All mismatches remain preserved.

## Remaining certificate work and provenance

Inherited-cut inactivity and remaining primitive/representation/borrowed-scratch
contracts are unresolved. No direct skip follows from a finite zero-FP count.
Parent and sibling tasks are independently exploring exact symbolic evaluation.

All work stays in `payload-model-20261016`; parent experiments and frozen streams
remain unchanged. Source snapshots, all four original cases, scripts, logs,
PIDs, exit markers, hashes and failed setup/build attempts are preserved.
The source primitive probe initially needed explicit Rust integer annotations;
those failures are retained. Build threads are capped at four; the population
check uses seven or eight workers, with workloads scheduled within the8-worker
budget. The35-input observer source is snapshotted before adding the separate
research primitive probe.

All experiment jobs are terminal. The source-exact seed/T0 model is available
for further arithmetic certification; a complete direct-rejection certificate
has **not** been established.
