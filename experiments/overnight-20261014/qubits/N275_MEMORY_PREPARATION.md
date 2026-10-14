# Prepared generation and memory measurement

The coordinator authorized full generation after the independent phase
checks passed. `qubit-n275-v2-full-build.sh` launched14:05:36UTC as
PID2502104 with a128GiB virtual cap. Its dedicated log is
`/home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/n275-v2-full-build.log`.
The unchanged evaluator subsequently launched under the separately
authorized256GiB allocation; its result remains pending.

Generation plus bounded metadata completed exit0 at14:29:18UTC.
Observed N is3832705108, max referenced Q is692, classical bits2390621,
compressed size5184686203 bytes. Operation storage is214631486048 bytes
(199.89GiB), so a16GiB margin gives215.89GiB. A256GiB virtual cap has been
requested after fresh capacity inspection;128/192GiB cannot fit. The
full generated stream SHA256 is
`ad1205994a3927ba76e90a086eadcf800d5876efe36425495cc8e83e21c6a26f`.
Generation took21:41.19 at1191232KiB peak RSS; bounded scanning took1:24.41
at6912KiB peak RSS. All counts are diagnostic until the full benchmark passes.
The full-N reservation verified capacity3832705108, matching the unchanged
loader. Its separate metadata is preserved in `n275-reserved-metadata.json`.

The isolated launcher verifies frozen base revision, all six changed-source
hashes, exact changed-path set and patch hash. It uses the existing protected
builder unchanged, a dedicated Cargo target, four build threads and one
library thread. The source's previously tested exact stream serializer writes
`evidence/n275-v2-ops.bin`; its protected-builder placeholder `ops.bin` is not
the generated circuit and must not be mistaken for the evaluation input.

The follow-up external scanner retains only3.5MB of records and measures the
actual op count and maximum referenced qubit IDs, matching the protected
`circuit::analyze_ops` rule. These are diagnostic generation measurements,
not a score. It also records emitted operation-type counts and compressed
size, without retaining the operation vector or touching the evaluator.

The metadata tool's small standalone probe completed exit0 at13:48:57UTC,
PID2481269. Actual `sizeof(Op)=56`, alignment8. A capacity17 request returned
capacity17. Source SHA256:
`5e527d37d2e1a08b48301ddbdb3c7302bd4f30b4e013bc6ffac88986f56fa5c8`.
The protected loader reserves `Vec::with_capacity(N)` before decoding and
does not grow the vector. Actual full-N capacity can be measured using the
tool's optional `--reserve` after allocation approval; the default generation
wrapper leaves this disabled until the observed N is known.

The frozen N275-v2 exact serializer fixture passed before generation:
PID2499578, exit0,462 physical operations, byte-identical complete output
to the unchanged harness writer. Protected builder SHA256 is
`ac013f1d851156a117c7d41ddb16cb5bb014ed4e6ed4679df143207b46852f33`;
unchanged point-add builder/serializer SHA256 is
`a30fa3fb745ebd518ad939e6cae9253c8167e58187a2bebdbf0285e77b95889e`.
The optional exact-stream flag changes raw storage, not op emission:
`B::raw` sends the same Op to the writer instead of pushing it to the Vec,
and source reads of Vec length outside that branch are diagnostics.

The original1128046998-op compact diagnostic held58.832GiB of operation
storage and measured58.855GiB peak RSS, about23.7MiB above that storage.
The new source may emit substantially more operations. Memory scenarios
below are arithmetic bounds, not measured new counts:

| Emitted ops | Op-vector storage |
| ---: | ---: |
| 1.5 billion | 78.23 GiB |
| 2.0 billion | 104.31 GiB |
| 2.5 billion | 130.39 GiB |
| 3.0 billion | 156.46 GiB |

After generation, use observed `N*56`, referenced classical-bit count and
fresh server capacity to choose the selected-batch evaluator allocation.
Reserve additional virtual-address and simulator overhead; do not assume
the prior128GiB cap fits. Root may authorize128–192GiB only after the count
receipt, with no concurrent large evaluator. The coordinator chose the
unchanged official benchmark after count/memory inspection, with native
peak recorded by `/usr/bin/time`, then independent original-counterexample
replay if needed. Fresh phase/hash packets come from the unchanged evaluator;
no packet or nonce tuning or extra export pass is planned.

The fresh trusted harness compiled exit0 at14:15:08UTC, PID2514018, in
`harness-n275-v2`. It is a clean c95b9325 worktree with only output paths
`results.tsv`/`score.json` sparse-excluded, so scorer output starts fresh.
The protected-source/Cargo/toolchain manifest verifies byte identity; no
historical result is edited. Evaluator binary SHA256:
`892c6c0c8ab7546dcee4fb08deb8146d4ca250b8ea941d02ce9bc43711ccb4dc`.
The prepared official-evaluation wrapper requires an explicit approved
memory cap, complete generation metadata, at least16GiB beyond operation
storage, clean historical output paths and exact source/binary attestation.
It creates an absolute `ops.bin` symlink to the full generated stream and
captures both native exit status and fresh scorer artifacts. Cycle PID2532160
launched after14:39:57UTC capacity inspection; official wrapper2534318 and
native evaluator2534382 are active. The256GiB cap fits199.89GiB operation
storage plus16GiB margin. All runtime thread settings are1. The launch
receipt states that the pending run is not a qualified record.
