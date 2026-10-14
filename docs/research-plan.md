# Research state and next experiments

Updated 14 October 2026, Singapore time. Our three targets are Q ≤ **692**,
rounded mean executed T ≤ **761,155**, and Q × T ≤ **939,681,127**. The
[public API snapshot](data/latest-leaderboard.json) binds these targets to source
revisions. The minimum-width leader is now Q693; the historical Q694 target is
obsolete. No new record from this workspace has qualified or been submitted.

[Experiment outcomes](experiment-outcomes.md) separates passing baseline
reproduction from failed and unfinished research. Only complete verified
benchmark results belong in the README plots. Start Toffoli/product changes on
the reproduced Q1234 baseline while retaining a separate qubit diagnosis track.

## What changed in this iteration

The Windows copy had three empty gitlinks and no `.gitmodules`, plus a tracked
shared Git cache whose alternate object path pointed to the earlier Mac. We
restored public sources through explicit submodules, updated the qubit pin to
`c95b9325`, removed the cache from tracking while preserving its local files,
and audited Rust include files. No literal source data include is missing.

The earlier experiment streams, proof checkpoints and uncommitted helpers were
not present. Their reports remain historical, with an evidence-gap notice and
[a machine-readable audit](data/workspace-audit.json). We reconstructed the
reciprocal experiment from its mathematical identity and the current source;
we did not recover the earlier native implementation.

The earlier public Q1234 product baseline (`c5bb1ec8`) passed the unchanged full benchmark on the
CPU server: 9,024 shots, zero classical/phase/ancilla failures, exact public
metrics and the earlier replay's stream hash. The server setup and source
checkouts now work; [verification receipt](data/server-verification.json).
The refreshed standings now have a newer Q1234/T761,492 product leader at
`143731ef`, score939,681,128. The earlier reproduction remains valid evidence;
it is not a reproduction of this new leader.

## Qubit track: compact restoring reciprocal

The current Q693 circuit uses a 276-lane ring and a 24-bit divisor head. It
temporarily makes the divisor's aligned leading one virtual so its physical
lane can hold reciprocal scratch. The old reciprocal remainder had 25 lanes.
Our new form uses **24 remainder lanes and the existing quotient flag**:

1. Save the remainder's overflow bit in that flag before rotating the lane view.
2. Clear the rotated low lane. The odd-divisor comparator needs a **zero**
   carry-in; inserting the dividend one before comparison is wrong.
3. XOR the overflow and low-word comparison to get the quotient decision, then
   subtract conditionally. Within `D` odd, MSB set, `0 ≤ R < D`, the two decisions
   cannot both be true.
4. Append the dividend one and use the resulting remainder parity to clear the
   flag. Recorded inverse playback supplies the corresponding cleanup.

The virtual leading-one comparator avoids the old virtual high-zero work.
In the actual N276 frame, `ring[18]` becomes free of reciprocal scratch. The
24-bit precision, TC26 comparison window, QB23 quotient cap, EMAX21 map
envelope, seven crossing-reserve lanes and inherited tail are unchanged.

| Evidence | Result | Scope |
|---|---|---|
| Z3 restoring identity, widths 2–8, 16, 24 | No domain counterexamples; missing-overflow faults detected | Arithmetic identity |
| Virtual leading-one comparator | 43,688 exhaustive cases, forward/inverse | Small target widths and arbitrary flags |
| Compact restoring step | 16,383 exhaustive cases | Precisions 2–8, all odd normalized divisors and remainders |
| Native N276 V-form | 1,536 cases; 1,089,536 independent measurement-phase coefficients | Active/inactive mixtures, boundary sizes, dirty passengers, forward/inverse |
| Focused K24 suite | 17 passed, one existing ignored research test | Component regression |
| Fixture emitted Toffoli saving | **572 per complete V-form** in each tested helper-bank size | Not a full-circuit mean count |

The first implementation failed at `k=2, D=3, R=1`, exposing the comparator
carry-in order. That defect was corrected and the negative evidence preserved.
A later integration compile error came from shadowing the column-stage callback;
it was renamed before starting circuit generation.

The compact form is integrated into the current **Q693 research branch**. Full
circuit generation completed: **1,128,046,998 operations**, peak **693 qubits**,
and **337,360,828 emitted Toffolis**. Compared with the public Q693 author's
recorded 338,637,532 emitted Toffolis, that is 1,276,704 fewer emitted Toffolis.
It is not the rounded mean executed metric used for scoring. The generated
compressed stream SHA256 is
`256422fd6e3520191300810546cb80974cb86c36354065d4c28fe564e078407d`.
The unchanged full benchmark's trusted scorer ran on `smu_server`,
under `nohup` and a
128 GiB process memory limit. Source and tests are preserved in
[the exact patch](../experiments/qubits/compact-reciprocal.patch) and
[manifest](../experiments/qubits/manifest.json). Server log:
`/home/hclau/ecdsa_research/logs/qubits-compact-candidate.log`; PID and exit marker
are adjacent. The run has now **failed validation** after all 9,024 shots:
6 classical mismatches, 3 phase-garbage batches and 6 ancilla-garbage batches.
The first reported classical mismatch is shot 1170. Exit status is 1; there is no
qualified score. The failed-run diagnostic mean in `results.tsv` is
335,575,751.423 Toffolis, which must not be treated as a valid leaderboard result.
The full benchmark took 38:17.50 and peaked at 62,572,324 KiB RSS (about 59.7 GiB).
Both job processes have exited. The complete log hash and stream hash are in
[the experiment receipt](data/qubit-experiment.json). Component and traversal
tests remain valid within their tested scope; they do not override this failure.
The follow-up automation is paused after collecting the terminal result.

**Immediate diagnostic:** replay the exact failed inputs, starting with shot 1170,
against the unmodified c95b9325 base and the compact variant. Capture the first
column/state divergence and compare value, ancilla and phase failures. Do not
assume inherited approximation or a new bug without this paired evidence.
Repair the relevant arithmetic or lifetime, add a targeted regression and rerun
full validation before preparing any submission.

A broad two-thread regression run hit its 8 GiB memory limit and aborted;
that is not a passing full suite. The relevant 203-column delayed-crossing test
also exceeded a 16 GiB allowance. With a 64 GiB allowance it **passed all 203
columns with 64 varied payloads and zero phase**, using about 19.2 GiB peak RSS
and 110 seconds. The source has matching hashes on Windows and the server.

**Next width experiment:** move from N276 to N275 only after proving the complete
quotient-owner schedule. The current q18..q22 owners occupy SX1..SX5; changing
the physical headroom moves q17 outside the ring as well. SX6 is the gate-on
accumulator, so simply adding it as a sixth owner conflicts with its lifetime.
The freed window-top lane is also the binary-search predicate lane. Neither is
automatically available between V calls. Prove parking/recomputation, delayed
payload padding and every direct/delayed crossing before reducing width.

## Toffoli and product tracks: change the interface

The public product source's forward and reverse Y16 tables were extracted and
checked on every signed input in `[-7,70]`. They produce exactly
`-(2^32+976)k` and `+(2^32+976)n` modulo `2^54`. Removing each program's final
AND produces detected counterexamples.

An XOR/AND program with m ANDs can increase the span of input affine functions
by at most m. On these 78 inputs, the forward output fields raise the GF(2)
rank from 9 to 23; reverse raises it from 9 to 21. Thus **14 forward and 12
reverse ANDs are necessary for these fixed interfaces**, exactly matching the
current programs. Resynthesizing those tables alone cannot lower their AND
counts while preserving all 21 fields on this domain. This conclusion excludes
different interfaces, smaller proved reachable domains, phase-only computation
and changes to surrounding construction/cleanup.

We also extracted the complete forward constructor's value interface from 14
raw input bits: six accumulator bits, E and Nm (three bits each), and two shift
controls. All **16,384 inputs** satisfy the arithmetic and carry identity; all
78 k values are reachable. Targets include 21 correction fields, six low result
bits and the carry into bit six. Their value-interface lower bound is **25
ANDs**. The current unshed construction accounts for 31 forward ANDs (six low
carries, four gate wires, seven k-construction ANDs, fourteen addend ANDs).
The six-AND gap is search room, not an attainable saving or complete-cost claim.
Cleanup, retained carries, phase repair and live width remain part of the cost.
The overnight cycle subsequently strengthened this fixed complete value-interface
bound to **26 ANDs** with a source-bound closed-subspace obstruction, independently
checked on all 16,384 inputs. Thus at most five constructor ANDs remain below the
current 31 within that interface; no saving is implemented or scored by this
bound. [Proof, negative controls and native scope](../experiments/overnight-20261014/toffoli/README.md).

Reproduce the source-bound targets and rank analysis with:

```bash
python scripts/analyze-fold-core.py
```

[Fold-core evidence](data/fold-core-analysis.json) records source and target
hashes. Full joint targets are generated under `research-output/fold-core/`.
The next gate experiment should synthesize across this complete constructor
and consume/cleanup interface, then emit and prove a native replacement.
Do not repeat the missing earlier phase-reader scans without a new hypothesis.

For product, preserve Q1234 and target T ≤ **761,491**; at Q1235 the strict
product target is **760,875**. An improvement must survive the final rounded
mean count. Prefer material savings that persist on paired and independent
inputs over a one-unit change in a hash-derived packet's mean.

The [new product leader's author](https://api.ecdsa.fail/api/submissions/7927f4b0-83de-4e77-a16e-dd3a620a2b11)
reports rare-event census cuts and a searched validation nonce. Its observations
are useful leads, but absence of a control pattern in a sampled census is not
a proof that its gate can be deleted for all admissible inputs. Study the exact
changes and their assumptions before rebasing; preserve our reproduced c5bb1ec8
base and do not adopt test-packet tuning as an optimization method.

## Primary-source research

- [Schrottenloher, optimized point addition (2026)](https://arxiv.org/html/2606.02235v1):
  separates Euclidean decisions from coefficient replay, implements in-place
  multiplication directly and exploits the secp256k1 pseudo-Mersenne modulus.
  These mechanisms already underlie this code; useful work is in the fused
  implementation and allocation, rather than simply porting the paper.
- [Efficient record-and-replay arithmetic (2026)](https://arxiv.org/html/2609.28882v1):
  documents Jump-2 compression, ping-pong GCD and fused replay. Its fresh-input
  checks and remaining structured counterexamples reinforce the need to keep
  population testing separate from an all-input proof.
- [Space-efficient ECDLP point addition, v2](https://arxiv.org/html/2607.13816v2):
  provides an exact register-sharing construction and location-controlled
  arithmetic, with 835 logical qubits for its complete ECDLP construction.
  Its interface and whole-algorithm accounting differ from this benchmark;
  compare primitives and proof methods, not headline gate counts directly.
- [Litinski, controlled add/subtract multiplication](https://arxiv.org/html/2410.00899v1):
  the controlled add/subtract primitive reduces schoolbook multiplier cost.
  Audit whether a target operation really needs a controlled add before
  proposing a replacement; this source is already highly optimized.
- [Gidney, temporary logical ANDs](https://arxiv.org/abs/1709.06648):
  explains measurement-based cheap uncomputation. Here, altered controls and
  shared wire lifetimes require the correct phase repair; dropping the erase
  cost alone is not a valid optimization.
- [Challenge rules](https://ecdsa.fail/terms) and the
  [official source](https://github.com/Layr-Labs/ecdsafail-challenge): protected
  files and dependencies stay untouched. Do not tune test inputs. The current
  evaluator checks forward values, phase and ancillas; its implementation
  does not explicitly perform the forward/reverse test described in the prose.

## Admission for a claimed record

Bind proofs and tests to the exact source and operation stream. Verify arithmetic,
wire ownership, inverse behavior, measurement phase and clean scratch. Check
meaningful faults. Run relevant component and column checks, then paired and
fresh inputs. Rebuild final source and run the unchanged full benchmark. Preserve
its log, return status, score and stream hash; compare with freshly fetched public
metrics. A component saving, incomplete job or failed packet is not a record.
