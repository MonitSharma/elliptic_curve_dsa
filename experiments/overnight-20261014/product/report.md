# Exact product controls and independent boundary inputs

Baseline: public `c5bb1ec876db859a3f9f8a9052c140a145df834e`, whose earlier complete
reproduction passed Q1234/T761658. These experiments are research diagnostics,
not a new score or public submission. The inherited identity tail is unchanged.

## Seven-atom control reasoning: no stream improvement

Hypothesis: extend the baseline six-atom exact Boolean abstraction to seven
atoms/u128, and check whether a conditional Toffoli toggle equals zero, its
condition, or either conditioned control. This covers exact absorption and
disjointness that operand equality alone misses. Universal identities are
proved on all valuations of the retained immutable atoms, a superset of their
possibly correlated reachable valuations. Unsupported unions become distinct
fresh atoms for the whole function; no partial terms are retained.

The extra pass runs after fingerprint-bound public rewrites and before the
unchanged tail. Existing six-atom passes remain intact. It creates no quantum
scratch, measurement, reset, or phase operation. Every replacement retains the
original per-op condition and classical condition stack.

The first test run ended 101 because the **negative-test count assertion** was
incorrect: deleting a complement changes a retained ancilla on all 128 inputs,
rather than the expected one. Forward/inverse equality checks had passed. The
failed source and log are preserved; the corrected fault deliberately substitutes
CX for a disjoint CCX, with the all-one input detecting the error.

The corrected suite passed five tests: seven-way conjunction/complement over
128 basis inputs with inverse/scratch and fault checks; 512 conditioned
measurement cases with classical snapshot mutation; 32 implication/disjointness
cases with nested mutable conditions; u128 boundary canonicalization; and
conservative fresh fallback. Measurement tests currently fix one transcript,
so their scope is finite rather than an exhaustive quantum-channel proof.

Complete generation ended 0. Its **entire compressed operation stream is
byte-identical to the passing public baseline**, SHA256
`49b35cf7640ebd529d76894eb8bef93ebf57e7e970fe14b3c27c8c5feb6e73e4`.
No new rewrite fired: 11,459,514 operations, 813,269 emitted CCX and zero CCZ.
The depth-based count proxy is 761,656.28125, **not scored mean Toffolis**. The
source changed, but the circuit did not. Repeating the unchanged full benchmark
would add no evidence of a resource improvement, so none was run.

Source patch, local and server manifests, protected-file hashes and stream
diagnostic are preserved alongside this report. Server generation PID2313907
has exited; the later paired diagnostic PID2319265 has also exited 0. Raw logs
and packets are under `research-output/overnight-20261014/product/` and
`/home/hclau/ecdsa_research/overnight-20261014/product-evidence/relations7/`.

## Identical-point and structured cases

An external research crate copies the loader and curve constants from the
protected clean product evaluator; it depends on that checkout's unchanged
shared library and writes no score/results file. It compares every final
quantum/classical slot and phase, using the same measurement transcript. Both
streams have the same measurement/reset order.

256 independent domain-seeded point pairs passed values, phase and scratch;
all paired states agreed. This is finite independent-input evidence.

256 structured on-curve pairs alternate `P = -2A` and zero-slope cases.
For zero slope, choose a nontrivial cube root beta modulo p and set
`P = (beta*A.x, A.y)`. Since beta cubed is one, both points lie on secp256k1;
their x coordinates differ. Inputs are checked against the official exclusion
of equal x coordinates or infinity. The protected curve reference supplies the
expected sum. Both byte-identical streams fail **191/256 classical outputs**
and all four phase batches, with no dirty ancillas. They agree in every state.
These are inherited baseline failures, not failures introduced by the extra
control pass. Detailed replay establishes **128/128 failures for -2A** and
**63/128 for zero slope** on this packet. Four exact counterexamples per family
are in [the compact receipt](structured-receipt.json), with both expected and
actual coordinates, source hashes and packet/log hashes.

The primary [record-and-replay paper](https://arxiv.org/html/2609.28882v1)
motivates these structured inputs. Its restrictions differ from the official
benchmark's input filter. Neither a passing public packet nor 256 passing
random examples establishes arbitrary-point correctness.

## Next exact hypothesis

The baseline quadratic interpreter forgets products above degree two. An
external analysis extended it to square-free Boolean ANF through degree eight,
at most 32 monomials. Two Boolean-ring/fallback property tests passed; complete
stream analysis found **zero savings**. A conservative commuting-window pass
also passed dirty-basis/phase and target-read/control-mutation fault checks,
but found **zero cancelable CCX pairs** in the complete stream. Both jobs ended 0.

At the coordinator's peak operation 1,444,991, ANF8 proves only qubit1233 zero,
matching the smaller abstraction; that wire is the next CCX target. It supplies
no additional parking lane.

A native fault check also confirmed that the existing PSCAN rewrite's value
restoration/dead-bit guards do **not themselves prove its phase premise**.
Measure a clean zero wire into m, then condition a CCZ on m: all other wires
stay unchanged, and the measured value has empty affine span. PSCAN drops the
block, but the all-one basis input's phase changes from 1 to 0. This is a generic
counterexample to using that pass without an independent phase argument. Its
zero span hits on our baseline make it inert here. We did not expand its search
or adopt a phase rewrite on the strength of value restoration alone.

## Exact classical factors: eight structural gate reductions

The original product index looks for a quantum wire holding the exact product;
it does not use an already available **classical bit**. If a quantum control
equals a current classical bit b, replace CCX(a,q,t) with CX(a,t) under b.
More generally, the exact truth abstraction can establish that the conditional
toggle factors as condition*a*b or condition*a*(1-b), even when neither original
control itself equals b. The latter is a XOR a*b: one original-conditioned CX
followed by the same CX additionally conditioned on b. All original classical
conditions and captured stack values persist; no bits are mutated.

The index removes and reinserts current bit values on HMR, store and invert.
It consumes every **original** operation, so the proof state never depends on
its own replacement stream. Equality compares whole exact tables, and opaque
overflow only loses proofs. No sampled input pattern is used to select gates.

Positive-control-only analysis passed two native suites and lowers four
unconditional CCX gates. A prototype storing a complemented bit in fresh
classical scratch failed two of three full-state tests because it left that
helper nonzero; its source and failed log are preserved. The XOR version
eliminates that scratch and passed all three native suites, covering mutable
bits, nested snapshots, independent measurement patterns, original-condition
aliasing and a deliberately stale-bit counterexample.

Complete external analysis lowers **eight emitted CCX gates**, four involving
complemented classical factors: 813,269 to 813,261. The condition-depth proxy
falls by **6.5**, with no added qubits, bits, measurements or resets. This is
structural complete-stream evidence, **not a scored mean or a record**. The
saved stream hash is
`b026a2d0c7e346158e665dada830d636a010ca93097a1f60b3daa87219b6505a`.

Full-state paired replay agrees on every final quantum/classical slot and phase
for all **9,024 baseline point inputs**, using a common independent measurement
transcript. Values and ancillas pass, but both streams have **one inherited
phase-garbage batch** under that transcript. This is not the official passing
baseline transcript or a passing full benchmark. Another 256 independent point
pairs pass values/phase/scratch in both streams. The 256 structured cases retain
the identical inherited failures above.

The clean-base [candidate patch](classical-xor-candidate.patch) changes only
four `src/point_add/` files and retains the exact inherited nonce tail. The
unchanged official builder subsequently produced the **byte-identical** external
candidate stream, exit0, and its three native suites passed. The
[source/protected-file receipt](candidate-builder-receipt.json) binds that run to
the clean-base candidate. All protected files and historical results are
unchanged. [Complete stream counts](candidate-builder-stream-diagnostic.json)
retain the diagnostic/scored distinction. Standalone official scoring
is deferred because this reduction alone cannot bridge the public record gap;
it can be integrated into a larger exact improvement. [Compact source, test and
paired evidence](controls-receipt.json) separates the failed prototype and
every diagnostic from a qualified score. **No original candidate is qualified.**

All source versions, including failed and negative experiments, can be recovered
from [the complete analysis patch](analysis-modules-completed.patch); that patch
is research preservation rather than the minimal candidate submission patch.

This strategy is independent of the Toffoli agent's joint fold arithmetic and
the coordinator's physical-wire lifetime study.
