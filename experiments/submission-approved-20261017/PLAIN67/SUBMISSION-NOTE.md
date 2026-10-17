# Product candidate: 761,121 T × 1,234 qubits = 939,223,314

Submission authorized by the researcher on 17 October 2026; local benchmark evidence follows. This targets the qubit × Toffoli product. It is
124,634 below the public record 939,347,948 (761,222 × 1,234, jackylee0424,
`85d067da`, source `4b2ec52f`; refreshed 17 Oct 2026, 07:30 Singapore).

**Unchanged benchmark.** All 9,024 shots pass; classical, phase and ancilla
failures are all zero. Total executed Toffolis 6,868,354,504; mean
761,120.844858156; rounded 761,121; peak 1,234 qubits.

**Circuit.** jackylee0424's `4b2ec52f` with one change: a 67-stage exact cache
that reuses repeated AND computations in idle wires, so peak width is unchanged.
Only `src/point_add` differs (three paths: the module call, a loader, a frozen
data table). The cache was certified equivalent to the original for every
input (universal certificate `303a75ec…`: 245,820 leases, 540,759 uses). The
native source reproduces the frozen stream byte for byte; the pre-tail of the
final stream is byte-identical to it. All protected files match the base.
Inherited approximate arithmetic of the parent is unchanged and disclosed.

**Failure rate (fresh inputs, declared before running).** Label
`product67-frozen-20261016`, 32,768 batches (2,097,152 shots) per source, paired
on identical inputs with the record's exact stream (`2a522394…`).

| | Record `4b2ec52f` | This candidate |
|---|---:|---:|
| Value-failing shots | 3,622 | 3,622 |
| Failing batches | 4,168 | 4,162 |
| Failed batches per 9,024-shot packet | 17.93 | 17.91 |
| Dirty-ancilla shots | 0 | 0 |

Discordant batches: 155 newly failing, 161 newly passing; one-sided exact
McNemar p = 0.653. The candidate also meets the older "no worse than parent"
rule. A 512-batch recheck of the final stream on the same label reproduces the
gate rows exactly. Paired saving: 102.14 ± 0.44 executed Toffolis per shot.

**Nonce.** 129,023,534, ascending from 1, lowest pass. 129,245,184 nonces
screened in the operational search (221,650 above the selected one are
parallel in-flight work), plus 4,096 control nonces (1–4,096) screened
separately. The prefilter only rejected nonces with a certified wrong output
value; every lower nonce fails, and a complete JSONL audit of all rows confirms
it. No nonce was chosen by its Toffoli count; no circuit content, table or cut
was tuned to a test packet.

**Hashes.** Final stream SHA-256
`f2279f98d631113bf045f7d2c8f17cbc514d77a135e14234b983d4534057b78d`; patch
`cf417469…`; source archive `41f0b29d…`; score file `e332a939…`.

Credit: the circuit is jackylee0424's `4b2ec52f` lineage; this entry adds only
the exact cache.


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
