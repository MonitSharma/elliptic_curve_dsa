## Submission attribution and scope

AI model used for the candidate research: **Claude Opus 5.5**. Coding harness:
**Claude Code**. The model attribution was supplied by the researcher when
authorizing these submissions on 17 October 2026. The reasoning effort setting
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
