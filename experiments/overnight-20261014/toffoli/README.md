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
