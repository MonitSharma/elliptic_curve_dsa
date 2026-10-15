# Product research: separate cycle, 15 October 2026

**No product improvement qualified.** A new lazy AND-cache transformation was
implemented at 1,234 qubits and completed the unchanged 9,024-shot benchmark.
That benchmark failed. Event-aligned comparison against its C5 baseline matched
all checked states and phases across 9,536 shots, but saved only three executed
Toffolis per shot. This is a diagnostic relative saving, not a scored result.

## Target and isolation

The [public snapshot](public-frontier.json), refreshed at 07:47 Singapore on
15 October, still reports product **939,396,074 = 1,234 × 761,261**.
At Q1234, a strictly better rounded mean must be at most 761,260. Relative to
the historically passing C5 reproduction's 761,658, the gap is 398 Toffolis.
At Q1235 the target is 760,644. Lower width alone need not improve the product.

This cycle read the other chat, “Run ECDSA.fail research cycle”, to establish
ownership. Its Q692 checkout, source, jobs and evidence were not changed.
Research here uses this directory and
`/home/hclau/ecdsa_research/product-focus-20261015/`. Shared summary documents
and the three existing track checkouts were not edited by this cycle.

## Implemented candidate and complete evaluation

Baseline revision: `c5bb1ec876db859a3f9f8a9052c140a145df834e`.
The [candidate patch](evidence/candidate/terminal/candidate.patch) changes only
three files under `src/point_add/`. It leases existing wires proved zero and
untouched during each lease, computes an identical AND only on its first active
use, reuses the value, and measures it away with the corresponding phase
correction. Classical validity flags handle conditional execution. See the
[transformation argument](LAZY_CACHE_DESIGN.md).

The generated circuit uses 1,700 leases and remains at Q1234. It has 11,519,190
operations and 45,102 classical slots. No original resets were removed in this
full candidate. These are generated diagnostics, not scored resource records.

The unchanged full benchmark completed all 9,024 shots with **12 value
mismatches, nine phase-garbage batches and zero ancilla-garbage batches**. Its
exit status is 1 and qualified score is null. The first value mismatch was shot
154. Total build/evaluation time was 4:21.89 and maximum resident memory was
4,221,320 KiB. See the [receipt](evidence/candidate/terminal/receipt.json) and
[complete benchmark log](evidence/candidate/benchmark.log).

Source, stream, protected evaluator and logs are bound in that receipt:

| Artifact | SHA256 |
|---|---|
| Candidate patch | `8e61689e4166db4b1c975a05f6d08c347dd0b75de0349974c7c1e949a0f07c26` |
| Complete stream | `a1657cb6932a2ab1efe870559ffa2b3ff5a14db0160344772d94904305b04882` |
| Official benchmark log | `e67c6d6343967a34285474cadb3b3c188a3d388ca65da7a91c617df1d3fe5569` |

No protected tracked file changed. The official benchmark appended its failure
to the private checkout's generated results file. No candidate was submitted.

## Separating transformation errors from inherited failures

The external replay reconstructs every operation in the candidate from the
baseline and recorded leases, including the unchanged final tail. It maps
original measurement events between streams and supplies separate outcomes for
the new cache measurements. It compares all quantum slots, original classical
slots, phase and zero cleanup of fresh classical flags.

| Input family | Shots | Unequal state/phase batches | Value failures, baseline/candidate | Phase batches, baseline/candidate | Paired Toffoli saving |
|---|---:|---:|---:|---:|---:|
| Candidate's official packet | 9,024 | 0 | 12 / 12 | 9 / 9 | 27,072 total; 3 per shot |
| Independent | 256 | 0 | 1 / 1 | 1 / 1 | 768 total; 3 per shot |
| Structured | 256 | 0 | 189 / 189 | 4 / 4 | 768 total; 3 per shot |

All three families had zero dirty-ancilla batches on both sides. The replay's
complete summaries and file hashes are in [the evidence manifest](evidence/manifest.json).
These finite comparisons support the rewrite; they do not establish correctness
of point addition on arbitrary inputs. They also demonstrate that the baseline
already fails on this candidate's packet. Changing the circuit changes the
official hash-derived packet; the historical C5 pass does not qualify this new
source. No nonce or packet search was performed.

The frozen candidate passed its two native rewrite tests. A separate extended
test crate passed three tests, including 3,072 single-lease cases, 4,096
overlapping-lease cases with all eight independent measurement patterns, dirty
classical inputs, mutable condition snapshots, controls restored after changes,
and detection of an intentionally missing phase correction. The extra test did
not modify the frozen candidate. See [native test output](evidence/lazy-cache-native-v4/tests.log).

**The earlier depth-based estimate of about 307 saved Toffolis was not an actual
measurement and is superseded by the paired saving of three.** Many repeated
occurrences lie on mutually exclusive branches. Structural repetition and
condition depth alone are poor estimates of executed reuse. The estimate was
used for ranking, never as a proof of correctness or a qualified score.

## Other searches completed

| Approach | Result | Limitation |
|---|---|---|
| Additional measurement-based cleanup after existing bound rewrites | One emitted CCX replaced | Too small; diagnostic only |
| Borrow an existing exact AND for the highest-index wire | 134 of 2,550 spans admitted | Cannot remove that wire throughout the circuit |
| Borrow an affine combination of stable values | 1,335 of 2,550 spans admitted | No complete lower-width circuit |
| Cache repeated ANDs using an additional wire | 53 selected intervals; depth proxy 45.75, unconditional lower bound 34 | Extra width is too expensive; no scored candidate |
| Two-Toffoli synthesis of the first five-data-wire carry block | No witness in the enumerated zero-preserving linear-conjugation family | Scoped component search, no general optimality claim |

The synthesis script checks its literal source model on all 32 data inputs and
both measurement outcomes. It does not prove that no wider rewrite or alternate
arithmetic construction can improve the circuit. Complete scan logs, launch
scripts, resource preflights and PID records are retained under `evidence/`.
The first native build failed due to a missing dependency in the external
research crate; the first replay preparation failed due to a missing copied
toolchain file. Both failures and the corrected runs are preserved.

## Consequence for further product work

This cache pass is not worth submitting or extending through additional
branch-depth ranking. Its measured saving is far below the target, and it
retains the baseline's arithmetic failures. Keep it as an exact transformation
to reconsider after a sound arithmetic base exists.

The productive next step is to localize and repair the existing product
baseline's arithmetic/phase counterexamples, then measure the cost of that
repair. Further reductions must exceed that cost plus the leaderboard gap.
The unresolved high-wire spans also require a different arithmetic schedule or
reversible construction, rather than more of the same limited loan search.
Any final source must pass the unchanged full benchmark and independent tests;
a lucky hash-derived packet is not a repair.

All jobs belonging to this cycle had finished at the final process check.
There is no continuing background search from this chat. Large streams and
replay packets remain on the server with hashes in the evidence manifest;
bounded logs, the exact patch and research sources are copied into this folder.
