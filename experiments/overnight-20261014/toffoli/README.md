# Toffoli research checkpoint — 14 October 2026

**No original circuit improvement or submission-ready candidate is established.**
This checkpoint adds exact negative synthesis results and stronger native tests
of the existing public `c5bb1ec876db859a3f9f8a9052c140a145df834e` constructor.
The unchanged public baseline remains the only complete passing point-addition
reproduction; these component figures are not benchmark scores.

## Complete constructor: the 25-AND rank bound cannot be attained

The all-input constructor contract has fourteen raw inputs: six accumulator
bits, three E bits, three Nm bits and the two shift controls. Its outputs are
the 21 correction fields, six low result bits and the carry into bit six.
All **16,384 input states** satisfy the arithmetic/carry identities. The input
affine span has dimension 15, and the span including the outputs has dimension
40. The earlier rank argument therefore required at least 25 ANDs. The existing
constructor uses 31; every original intermediate is independent of prior inputs
and intermediates, so simple gate deletion or affine substitution cannot help.

We now rule out **25 ANDs** for this fixed complete XOR/AND value interface.
The necessary bound is **26 ANDs**, not a claim that a 26-AND program exists.
The original 31-AND constructor is not proved optimal.

The proof is a closed-subspace obstruction. Let W be the input-plus-output span.
An explicit eight-gate program builds a space S of dimension 23 inside W,
containing the complete raw-input affine span. Let P span S and every pairwise
product of S's basis functions. The independent rank checker obtains:

| Space | GF(2) dimension |
|---|---:|
| S | 23 |
| W | 40 |
| P | 228 |
| P + W | 245 |
| P ∩ W | 228 + 40 − 245 = **23** |

Consequently P ∩ W = S: every product of arbitrary affine forms of S that lands
inside W already lies in S. This closure does not depend on the chosen order
of a hypothetical candidate's gates. By induction, any XOR/AND program that
starts with the raw inputs and keeps every new AND inside W stays inside S.
A 25-AND program attaining the dimension-40 output span would have to keep all
its intermediate functions inside W, which contradicts the proper closed S.

The checker uses least-significant-bit elimination, separately from the search's
highest-pivot implementation. Its negative control uses the seven-gate prefix:
S then has dimension 22 but P ∩ W has dimension 23, correctly identifying it as
not closed. The extra eighth gate was found by a small affine-factor SAT query;
both positive-prefix and target queries were SAT and their witnesses were
verified on every source input. **There is no SMT UNSAT claim in this proof.**

Evidence: [compact source netlist](constructor-netlist.json),
[closed eight-gate basis](toffoli-exact-joint-20261014.json),
[independent certificate](closed-subspace-certificate.json), and
[independent checker](toffoli_check_obstruction.py).

This is a fixed value-interface statement, not a lower bound on the entire
point-addition circuit, a phase proof, or a rounded executed Toffoli count.
Different interfaces and separately proved reachable domains remain possible.

## Smaller cuts and unsuccessful synthesis

The smallest promising source cut contains five ANDs: y5, c6, upper3, upper4 and
upper5. Its exported value span has a rank bound of four. Exhaustive closure
examined all 2,096,128 products of the final 2,048 affine forms and showed that
four ANDs cannot attain that fixed interface. Adding both available shift
controls gave 288 exact input patterns and still failed after all 33,550,336
products of 8,192 affine forms. Thus the five-AND cut is already optimal for
both stated interfaces. Other expanded cuts have either negative rank-bound
attainability results or explicit incomplete status; those are not optimality
claims for larger programs.

The narrower `3*(Nm+acc_low)` arithmetic decomposition has a seven-AND lower
bound when it retains the full sum, matching the existing decomposition. A
triple-only interface has a five-AND bound, but discarding the signed sum needed
by the rest of the fold does not establish a complete saving.

A sparse thirty-AND search considered the 63 codimension-one subspaces of the
six original intermediate directions outside W. It checked **166,699,302 pairs**
and found no value witness. Its sparse affine form limits and time limits make
this an **incomplete negative search**, not a proof that thirty ANDs are
impossible. See [search receipt](toffoli-joint-thirty-and-20261014.json).

## Native baseline verification and its limits

The permitted-source [native fixture patch](native-fixture.patch) adds tests
under `src/point_add/`, leaving production arithmetic and the protected harness
unchanged. The final v4 job passed both tests.

- Width 56, fin 0: all 16,384 low input states and 38 deterministic high words;
  zero measurement outcome plus every one of 79 measurement coefficients,
  totaling 49,807,360 simulated cases.
- Width 57, fin 1, and width 56, fin 2: the same low states and high words, but
  only four measurement words each; 2,490,368 cases per fixture.
- Forward values, input passengers and clean scratch passed. The removed final
  low-carry CZ repair produced detected phase garbage.

The fin-0 fixture structurally rules out measurement-conditioned value changes,
nested measurement conditions and combined direct/stack conditions. Its phase
is therefore linear in measurement outcomes, making the coefficient checks
complete for the **38 tested high words**. These include zero, all ones,
alternating bits, selected one-hot/all-but-one words and carry boundaries.
They do not cover every possible high word. The fin-1/fin-2 runs cover four
measurement words, not all outcomes. No full point-addition qualification was
run for these tests.

The v4 job took 1:29.77 including compilation, with 1,148,664 KiB peak RSS, under
a 16 GiB virtual-memory limit, four build threads and one runtime thread.
Exact command, hashes, server paths and limits are in the
[fixture manifest](native-fixture-manifest.json) and
[checkpoint receipt](first-checkpoint-receipt.json).

Failures were retained:

- The first fixture's positive checks passed, but deleting its first top CZ
  did not exercise a nonzero phase on the chosen two upper-word patterns. The
  negative control failed; it is a verification-coverage limitation, not a
  passing fault check. [Original fixture](toffoli_native_fold_fault_v1.rs).
- A v2 launcher containing CRLF failed before running tests. The original
  [failed launcher](toffoli_native_failed_crlf_v2.sh) and log are preserved;
  its [byte-exact encoded copy](failed-crlf-launcher-bytes.json) survives Git's
  shell-script LF normalization. Later launchers use LF.
- The initial four-AND SAT process was stopped only after exact cut closure
  superseded it. Status is `canceled_superseded_by_exhaustive_closure`, signal
  SIGTERM, exit 143. Cancellation is not an UNSAT result.

Raw logs remain locally under `research-output/overnight-20261014/toffoli/` and
on the server under `/home/hclau/ecdsa_research/overnight-20261014/toffoli/`.
All jobs in this checkpoint are terminal. The source-bound experiment scripts,
compact receipts and permitted patch are tracked; bulk streams and build caches
remain outside Git.

## Reproduce and next experiments

From this project's root, using Python and Z3 only where stated:

```text
python experiments/overnight-20261014/toffoli/toffoli_constructor.py
python experiments/overnight-20261014/toffoli/toffoli_export_netlist.py
python experiments/overnight-20261014/toffoli/toffoli_check_obstruction.py experiments/overnight-20261014/toffoli/constructor-netlist.json experiments/overnight-20261014/toffoli/toffoli-exact-joint-20261014.json --output /tmp/closed-check.json
```

The independent certificate checker requires no solver. Re-running the full
closure search requires Z3 5.1.0 and the recorded `toffoli_exact_joint.py`
command. Apply `native-fixture.patch` to a clean c5bb1ec8 checkout only, then run
the manifest's native test command. The patch must not be applied twice.

The next search should admit one to five temporary directions outside W and
use exact affine-factor closure rather than repeating the sparse search. Any
value witness still needs explicit carry materialization, unchanged live width,
consumption and measurement-phase cleanup accounting before native integration.
Changing the output interface to fit its actual consumer is another open route.

## Second checkpoint: cleanup and complete component costs

No new resource record was established. The frozen
[second checkpoint receipt](second-checkpoint-receipt.json) binds the reports,
patches and terminal evidence below.

The [63-plane search](exact-planes-summary.json) found no constructor with at
most 30 ANDs whose functions all remain in the original 46-dimensional function
span. Four planes closed by exact quadratic-span obstructions; 59 required Z3
affine-factor UNSAT results without saved formal proof certificates. Circuits
that introduce new functions outside this span remain open. The raw 553,853-byte
receipt is retained outside Git and bound by SHA256.

The [changed two-step consumer contract](consume-two-exact-summary.json) has
raw rank 17 and desired rank 41. Its rank-only 24-AND value count is unattainable
under the recorded trusted solver result. This interface includes the constructor
and two ladder carries, but its changed phase ownership and cleanup were not
implemented; this is not a complete Toffoli lower bound.

A [bank basis](bank-phase-basis.json) permits six exact early measurement erases
while preserving all values needed by the ladder. The native implementation
retains 31 constructor ANDs, runs the ladder with 25 bank directions, then pays
six unconditional ANDs to restore the original cleanup interface. The
[native patch](bank-loan-native.patch) reproduces the exact source whose hashes
were recorded in the passing native job. All three tests passed, including
53,542,912 cases over every low input state, 38 upper words, and zero plus 85
individual measurement-phase coefficients. The planted early phase-repair fault
was detected. Arbitrary upper words were not exhaustively covered.

This implementation loses gate cost. The [component receipt](bank-component-receipt.json)
records all 11 paired fold rooms and 55 complete payload-body allocation pairs.
Affected payload bodies add 3–6 diagnostic mean Toffolis. The body pairs measure
resources only; they do not constitute body correctness tests or scored results.
Some component peaks fall by 1–6 wires. All
[136 canonical component streams](bank-component-streams.json) are SHA256-bound;
enabling the existing diagnostic report changed none of their bytes.

Free phase cleanup remains open. The bounded
[interleaved schedule search](bank-phase-schedule.json) did not finish a cleanup.
At its separately recorded greedy six-bank endpoint,
[all 63 linear bank rebases](late-phase-rotations.json) reject a quadratic phase
erase, and the [cubic phase search](cubic-cleanup.json) finds no erase of an
individual retained bank direction. These are exact limits of those interfaces,
not lower bounds on every cleanup schedule or higher-degree phase synthesis.

The separate production-enabled [product candidate patch](bank-product.patch)
preserves the old cleanup, nonce and protected harness. It includes only the
public content-rebinding files from 143731ef, excluding that public revision's
census and zero-force changes. Its complete builder
[failed at the inherited allocator boundary](bank-product-failed-builder.json)
on forward tick 87: earlier changed folds returned their scratch with a different
free-list order. The existing assertion remains intact. No complete peak or
stream was obtained, so the product-width tradeoff remains unmeasured. The next
integration step must restore the baseline allocator interface exactly.

The short fixture compilation failure and two inactive diagnostic-counter
attempts are preserved explicitly in the component receipt. They are not
passing resource measurements.

## Third checkpoint: width route closed, broader constructor search

The bank-only PRODUCT width route is closed under the retained table interface.
The [exact width floor](bank-table-width-obstruction.json) identifies two emitted
HMR rows of `y42_bound.bin` that reference qubit 1233. Every expected and replacement
row in `linear_restore.bin` references qubits at most 1200, so that pass cannot
remove either row. The unchanged scorer counts the maximum referenced qubit ID
plus one, regardless of its conditional execution. A candidate retaining these
tables therefore cannot score fewer than 1,234 qubits. This is a structural
conditional floor, not a completed builder measurement. No conditional row was
deleted based on sampled controls.

The [generic allocator integration](allocator-v3-native-receipt.json) preserves
the original body’s exact allocator ordering with a separate baseline emitter.
It snapshots operational and diagnostic contexts, leaves tick 0 and its original
`Y26_T0=5` setting untouched, and checks the original scratch ownership through
the unchanged y42 setter. Both primed and initially fresh pools passed: 110 exact
allocator-state pairs and 110 disabled-bank operation-vector pairs. The
[v3 patch](bank-product-allocator-v3.patch) and
[source receipt](bank-product-allocator-v3-source.json) preserve the tested source.

The independent field-payload checks were intentionally kept separate. Old/new
outputs, passengers and scratch matched over 56,320 extended-domain cases, but
both sides fail the separate modular reference and sampled phase diagnostics:
3,520 reference mismatches and 5,249 total sampled phase failures. Whether those
arbitrary payload/tape-letter combinations are admitted by the actual rail
producer is unproved. These are failed/unadmitted body-phase diagnostics, not
passing component-phase qualification or inherited full-circuit defect claims.

The [v2 complete builder failure](bank-product-failed-builder-v2.json) exposed a
legitimate fresh scratch frontier that its primed fixtures missed. The original
assertion was preserved; v3 adds explicit fresh-frontier tests. No further bank
builder was launched after the static width floor closed the route. Neither
builder attempt produced a complete stream, peak or full-circuit gate count.

For cleanup, the independently ranked
[closed low-interface subspace](phase-closed-interface-v1.json) contains final
data but is smaller than the post-loan bank span: S has rank 23 and W has rank 40,
with `P2(S) intersect W = S`. This excludes an all-free quadratic cleanup chain
inside that interface, beyond the earlier greedy ordering failure. The
[upper-coordinate extension](phase-upper-extension-v1.json) checks all 65,536
low-plus-two-upper-input states: upper addition is a bijective translation in
every fixed low-input group, and the corresponding ranks are 25/42/275/292 with
intersection 25. Independent arbitrary upper-result coordinates preserve the
obstruction. Charged nonlinear gates, retained helpers outside W and restricted
producer domains remain outside this proof.

The [first outside-direction sweep](outside-direction-v1-summary.json) tested
90 selected rank-45 value interfaces. Eighteen closed by quadratic-span
obstructions and 72 by trusted affine-factor UNSAT results without formal proof
certificates. No 30-AND witness was found. A separate bounded job now examines
all 651 four-dimensional subspaces of the six old temporary directions, adjoining
the selected `acc3*k1` function outside the old span. The
[third checkpoint](third-checkpoint-receipt.json) records its pending status,
limits and process identity; it is not a negative completed result.

## Fourth checkpoint: changed consumer phase interface

The earlier pending search completed. The selected `acc3*k1` extension found
no 30-AND value witness in either its [651 direct-containing planes](external-planes-v2-summary.json)
or its [1,953 mixed planes](external-mixed-v4-summary.json). An independent
enumeration agrees on the complete selected family; together with the 63
original-span planes, this covers rank-45 interfaces in that one rank-47 span.
The [consumer-sum external direction](external-planes-v3-summary.json) also
completed all 651 selected planes without a witness. These negative results
include trusted solver UNSAT, with no saved formal proof certificates; other
external functions and larger spans remain open.

A separate [reverse joint model](reverse-constructor-model-v1.json) combines
the quotient prefix with its fixed 12-AND table. All 16,384 primitive inputs and
78 integer quotient values pass reconstruction. The raw rank is 15, the full
value-interface rank 34, and the source uses 25 ANDs. Its
[63 original-span planes](reverse-planes-v1-summary.json) and
[2,604 selected external planes](reverse-external-v2-summary.json) found no
24-AND witness. The early kp1 requirement is preserved. No global 25-AND
optimality or complete reverse-fold cost claim follows.

The [new carry-cleanup report](carry-cleanup-report-v1.md) changes the consumer
interface rather than retaining original acc3. After its final bit3 write and
y3 rebase, the remaining 30 physical helpers admit an exact quadratic cleanup
basis. The [truth/rebase proof](carry-cleanup-rebase-v1.json) verifies every
16,384-row identity, 164 reversible linear gates and 745 quadratic phase terms.
The [passing native receipt](carry-cleanup-native-v1r2-receipt.json) preserves
100,925,440 positive cases, all measurement coefficients for 38 tested upper
words, dirty passengers/scratch, a detected phase fault, and seven paired
complete-component costs that save exactly one executed AND per shot. Previous
compile and fixture-assumption failures remain preserved.

The full c5 builder's independently reported guard census finds **zero calls**
to that existing guarded interface. It is therefore a positive component
result, not a full resource record. An early loan expansion is being researched
separately by the product track. The resource-only
[tight-room trace](carry-trace-v2-receipt.json) preserves all 93 successful and
33 failed room/tick contexts; those recipes are not full-circuit frequencies.

The actual deferred lean route has an exact
[one-AND c6 phase factor](actual-lean-c4-swap-v2.json) with a prospective mean
saving of 0.5 per admitted fold. Physical scheduling and native proof are
pending. Its abstract E2-missing case is unadmitted for actual fin4 because ESh
also changes E0/E1. Fin3 retains all E inputs; broader transfer needs exact
producer lifetime evidence. No new full qualified score is claimed.

The [fourth receipt](fourth-checkpoint-receipt.json) freezes the completed files
and records these pending scope obligations.

## Post-checkpoint: actual fin3 native cleanup

The narrowed deferred lean interface now has a [passing native report](actual-lean-native-report-v3.md)
and [source-bound receipt](actual-lean-native-v3r1-receipt.json). All262,144 fixed-input/layout
phase proofs and786,432 native cases pass, with every quantum wire, dirty passengers,
512 classical ABI bits and a detected phase fault. The actual tick128 source caller
hits the new guard and emits one fewer CCX at unchanged peak1234; sampled mean
execution saves0.5 per eligible fold. The original failed emitted-count assertion
is preserved separately. This is component evidence, with full producer and broader
fin/drop interfaces still pending; it is not a complete resource record.

The [drop1 receipt](actual-lean-native-v3r3-receipt.json) now qualifies an actually
dropped ladder carry, with131,072 all-measurement proofs and393,216 native cases.
Its source caller is tick129/room39/cap1234, again saving one emitted CCX at the
same peak. The unmatched v3r2 caller and its merged-plan limitation are preserved.
The [top1/direct/nondeep ESh contract](actual-esh-contract-v4.json) independently
verifies all128 seven-bit producer states and their measurement corrections;
producer-aware fin4 native scheduling is a separate pending experiment.

The narrowed producer-aware fin4 schedule subsequently passed; see its
[report](actual-lean-native-report-v4.md) and [receipt](actual-lean-native-v4-receipt.json).
All18 producer/fold inputs are covered in2,097,152 exact phase-layout proofs and
6,291,456 native cases. The actual two dropped chunks and fresh ESh targets are
checked. Source-caller tick130/room37 retains peak1234 and saves one emitted CCX.
This admits only top1/direct/nondeep ESh, with full-body qualification separate.

The [lazy cleanup v5](actual-lazy-native-report-v5.md) and
[producer-aware v6](actual-lazy-native-report-v6.md) subsequently establish
mean component savings of 7/8 AND per eligible deferred fold, with one extra
emitted CCX. All newly owned classical flags are cleared before free in v6;
the full 18-bit producer/fold domain has exact all-measurement phase proofs and
33,554,432 native cases. Full-body and broader high-coordinate qualification
remain separate. This small late-fold saving alone does not bridge a record.

The [minimal-auxiliary constructor report](minimal-aux-constructor-report-v10.md)
archives the completed v8 through v11 exact value-interface probes. The 89
selected raw-product interfaces, 236 reachable-basis-product interfaces and
256 symplectic-transformation interfaces found no complete constructor. A
three-product partial identity is exact but its selected completion also
closes negatively. These restricted negatives are not global constructor
optimality proofs, and none is a scored resource result.
