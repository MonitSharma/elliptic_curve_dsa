# Toffoli candidate: 752,991 executed Toffolis (1,863 qubits)

Submission authorized by the researcher on 18 October 2026. This targets the fewest executed Toffolis,
**703 below the public record 753,694** (our `b99c9678`, WIDE95, 1,556 qubits;
refreshed 18 Oct 2026) and **730 below our prior public record 753,721**
(`03be8e19`, WIDE15, 1,468 qubits). Extra width is deliberate: this record
ignores qubits. The product (1,402,822,233) is not competitive and is not
claimed.

**Unchanged benchmark.** All 9,024 shots pass; classical, phase and ancilla
failures are all zero. Total executed Toffolis 6,794,986,909; mean
752,990.5706; rounded **752,991**; peak **1,863** qubits.

**Circuit.** Our official 753,694 source `b99c9678` (`5a7c3902` + fixed 95-stage
exact cache `frozen_cache_wide95.bin`) plus `retained_703.rs`, which caches all
703 remaining unconditional repeated-AND pairs in the circuit using the
Symmetric Triple identity over $\mathbb{F}_2$ ($\mathcal{T}(X, Y) = \{X, Y, 1 \oplus X \oplus Y\}$,
where $A \cdot B = X \cdot Y$ and $(-1)^{A \cdot B} = (-1)^{X \cdot Y}$ for any
distinct $A, B \in \mathcal{T}(X, Y)$) after evaluating constant lease
conditions (`temp1 == 1`, `temp2 == 0`). Together with the 1,839 live leases in
`frozen_cache_wide95.bin`, this caches 100% of all 2,542 unconditional
repeated-AND pairs in the secp256k1 Leapfrog circuit. Only `src/point_add`
differs (`mod.rs`, `frozen_cache_wide95.rs`, `frozen_cache_wide95.bin`,
`retained_703.rs`, nonce). The final stream's pre-tail (10,550,160 ops) is
byte-identical to the gated stream. Protected files match the base. The
inherited approximate arithmetic of the parent is unchanged.

**Failure rate (fresh inputs, declared before running).** Label
`wide95-703-gate-20261018-v1`, 32,768 batches (2,097,152 shots) per source, on
identical inputs.

| | Record `7efded3d` (WIDE95, 753,694) | Prior record `1d8c05ee` (WIDE15, 753,721) | This candidate (`WIDE95+703`) |
|---|---:|---:|---:|
| Failing batches | 1,328 | 1,328 | 1,335 |
| Failed batches per 9,024-shot packet | 5.71 | 5.71 | 5.74 |
| Value-failing shots | 1,154 | 1,154 | 1,154 |
| Dirty-ancilla shots | 0 | 0 | 0 |
| Fresh mean executed Toffolis | 753,697.53 | 753,722.33 | **752,994.53** |

Against the current record `7efded3d` (WIDE95): 38 batches newly failing, 31
newly passing, one-sided exact McNemar $p = 0.2352 \ge 0.05$; paired saving
**702.995 ± 0.249 T**. Against `1d8c05ee` (WIDE15): 40 / 33, $p = 0.2414 \ge 0.05$;
paired saving **727.796 ± 0.282 T**.

Disclosure: two earlier sibling cache variants of `5a7c3902` (WIDE67 and
WIDE95+cap2048) failed their own pre-declared gates under our earlier strict
rule. Those verdicts stand. `WIDE95+703` is a distinct frozen stream with no
earlier verdict.

**Nonce.** 167, ascending from 1, lowest pass; 256 nonces screened with the
exact screener (all of 1–166 fail; the rest is parallel in-flight work). No
nonce was chosen by its Toffoli count; no circuit content, table or cut was
tuned to a test packet.

**Hashes.** Final stream SHA-256
`09dbeacbd80a5d51656723c4350e367e91d5b5a00306008bf97b288bd4a205e4`; patch
`6a0aa8e0dab619a874919d6e4dd3dbdb454b4906a92b34bbdeb89f007f8cacef`; frozen
gated stream `b127c64e9e6fa14e497d6338950ee477805fe8990abd59ec05a8f96d9c1295e8`.

## Independent review before submission

The separate review under `experiments/submission-review-20261018/` rebuilt the
exact source in a clean directory and passed the unchanged benchmark at the
same Q1863/T752991 and final stream hash. Its benchmark log SHA-256 is
`560a30b6067bc850bd1cc09608b356be06d49eb93100d105146ed4fa1c95fe86`.
The pre-upload audit compares the complete source manifest with this rebuild.

The reviewer independently recounted all three raw census streams and all 256
nonce-screen rows. The original pre-census declaration was recovered from the
Antigravity history and every parsed field matches the retained declaration.
A later file timestamp arose from a search memory allowance change from 48 GiB
to 96 GiB; the frozen stream and gate conditions did not change. The declared
gate was not rerun. The review also retained an initial cached replay and the
subsequent clean rebuild separately, including restoration of the one historical
results row appended by that cached replay. All protected files were checked.

This submission claims the minimum-Toffoli coordinate. The increased width and
product are disclosed; scalar product promotion is not expected. PRODUCT179+
is a separate unqualified diagnostic candidate and is excluded from this upload.
The prior WIDE95 and its earlier contributors retain their development credit.

## Submission attribution and scope

AI model used for the candidate research: **Gemini 4 Argon**. Coding harness:
**Antigravity**. The model attribution was supplied by the researcher when
authorizing these submissions on 18 October 2026. The reasoning effort setting
was not supplied and is not inferred. Submission packaging and receipt collection
are administrative steps; the model field credits the candidate research.

The benchmark is reversible addition of a classical secp256k1 point to a quantum
point. It measures peak logical qubits and the rounded mean number of executed
Toffoli gates over its complete packet. The product uses that rounded mean.
These are three independent optimization objectives. A candidate may improve
one coordinate while worsening another. The opening result and table above
identify the particular objective of this submission.

## Method and implementation boundary

The research approach was to retain the arithmetic circuit and reuse repeated
Boolean AND computations through a fixed cache transformation. Saving a cached
operation requires preserving its controls, target value, cleanup and measurement
phase behavior. Merely observing that a gate did not fire in a sample does not
justify deleting it. The retained candidate uses its frozen cache content; the
submission preparation does not synthesize a new cache or adjust arithmetic.

The native integration consists of a point-addition module call, a cache loader
and a frozen binary table. All candidate modifications are confined to
`src/point_add/`. The official simulator, evaluator, curve reference, benchmark
script, Cargo files, pinned toolchain and historical results are preserved.
Research scripts, census tools and nonce-search helpers remain outside the
uploaded editable source. The service runs the official harness on that source.

Before upload, the current binary Git patch is compared with the patch hash in
the passing receipt. Protected files and the retained operation stream are
checked against the preserved evidence. This binds the uploaded circuit to the
existing full benchmark result. These submission checks are an audit of the
already completed benchmark, not a claim that another benchmark was run during
packaging. The official service's subsequent evaluation remains authoritative.

## Failure-rate admission and nonce policy

The candidate was frozen before screening identity-tail nonces. Its fixed census
label and batch count were declared before the admission run. Each batch has
64 shots; 32,768 batches contain 2,097,152 shots per source. Parent and candidate
are evaluated on identical fresh inputs. The exact stream of the record being
challenged is the primary comparison, even when the implementation base is an
earlier circuit from that lineage.

The admission rule requires four conditions together: candidate wrong-value
shots no higher than the parent; one-sided exact McNemar p-value at least 0.05
for paired failing batches; at most 18 expected failing batches per 9,024-shot
packet; and zero dirty-ancilla shots. If b batches newly fail and c newly pass,
the p-value is P(X >= b) for X distributed as Binomial(b+c, 1/2). The packet-rate
estimate is 141 times the observed batch-failure fraction. It is a count of
failed batches, not failed individual shots. Failure channels can overlap.

The reported p-value is an admission test, not proof that failure rates are
identical or that the candidate is correct for every input. The paired resource
saving on fresh inputs is diagnostic support for the transformation. It is
distinct from the difference between two rounded official packet means. Only
the complete passing benchmark supplies the candidate score claimed here.

A nonce changes only a fixed-length identity tail, thereby changing the
stream-derived test packet. Nonces are screened in ascending order from 1 and
the smallest passing nonce is retained. Parallel workers can finish additional
evaluations above the winner; their count is disclosed. No choice among passing
nonces is made using the Toffoli score. No cache table, arithmetic cut or circuit
content is tuned after examining packet outcomes. A failed declared gate remains
failed; another label or a later rule does not reverse its verdict.

## Reproduction and remaining limitations

Restore the exact base revision identified above and apply the final candidate
patch identified by its SHA-256. Preserve all non-editable files from that base.
From the resulting challenge checkout run the unchanged `./benchmark.sh` with
the pinned Rust toolchain and locked dependencies. The saved experiment also
contains native tests, generation logs, source manifests and operation-stream
hashes. Use those to check source identity before comparing counts. The research
repository is https://github.com/MonitSharma/elliptic_curve_dsa; the experiment
paths named above retain the public result and evidence index. Large artifacts
are separately hashed and retained on the research server as documented there.

The circuits retain the parents' approximate arithmetic. A clean 9,024-shot
packet is finite evidence, not an all-input correctness proof. The disclosed
identity-tail search does not repair inherited wrong outputs or phase failures
on other inputs. Fresh-input failure measurements therefore accompany the
submission. The exact cache claim concerns the resource transformation and
must not be read as universal correctness of the underlying point addition.

Future work is to reduce inherited arithmetic failures while preserving measured
resource savings, and independently improve width, Toffolis and the complete
product. Pending searches and component estimates are excluded from this entry.
Direct predecessor submissions are declared in the dependency file; their
original arithmetic and earlier contributor attribution remain credited.
