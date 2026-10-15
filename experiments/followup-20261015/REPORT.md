# Follow-up: exact two-gate simplification, failed qualification

**Later terminal result:** while this follow-up was running, the final overnight
bank-swap v2 circuit completed with a full **Q692** local benchmark pass, one
qubit below the public Q693 minimum. Its gate count is much higher, and ordinary
submission packaging remains unqualified.
[Passing width result and limitations](bankswap-terminal/RESULT.md).
The failed qualification described below concerns the separate B3 gate candidate.

15 October 2026, Singapore. **No Toffoli or product record from the B3 candidate.** A new conservative
support pass removes two provably redundant Toffolis from public B3, but its
unchanged full benchmark fails. Exact paired replay confirms every observed
failure is also present in unchanged B3 on the same inputs and measurement
transcript. No challenge submission was made.

## Candidate and proof

Base: `b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7`. The
[reapplicable patch](candidate-source/candidate.patch) changes only
`src/point_add/mod.rs` and adds `src/point_add/guarded_zero.rs`. It preserves every
public fingerprint assertion and applies after the bound rewrite tables.
The inherited identity tail and nonce are unchanged.

The pass tracks conservative conditions under which each quantum wire can be
one. Classical conditions refer to immutable values, including snapshots and
measurement outcomes. Joins deliberately forget facts; an unsupported classical
expression becomes a fresh atom. A CCX is removed only when its complete guard
and quantum-control support are contradictory. This does not change phase,
measurement order, classical state, or quantum storage.

In the complete B3 stream, the two removed gates are at zero-based operations
**5,378,815** and **11,653,340**. Their respective controls **q712** and **q1150**
are provably zero. Both occur in measurement-conditioned cleanup regions.
[Exact source-bound controls and preceding touches](guarded-zero-explanation.json).
The initial search description considered guard/control contradictions in
general; these actual hits have the stronger unconditional zero-control fact.

Independent SSA Boolean-cone checks prove both toggles zero, with 2,288 and
1,090 saved equations. Cone boundaries are arbitrary Boolean inputs, rather
than sampled arithmetic values. A separate equation replay reports UNSAT for
the proposed toggle and SAT for its negation, checking consistency. These are
trusted Z3 results, not exported formal proof certificates.
[Equations](proofs.json), [independent replay](proof-replay.json).

Validation before full evaluation:

- Six support-analysis tests pass, including exhaustive scalar checks of 400
  generated small programs and conditions changed after being captured.
- Four Boolean-cone tests pass, including wrong-witness, forgotten-boundary,
  changed-condition and resource-limit negative controls.
- Two native Rust tests pass. The equivalence fixture checks dirty input values,
  incoming phase, nested conditions, measurement outcomes, and a nonremovable
  Toffoli over 16 measurement seeds and 64 lanes. [Native log](tests.log).
- Streaming comparison of every operation confirms that the generated output
  differs from B3 **only by those two CCX deletions**. All other operations,
  including the final identity tail, are identical.
  [Whole-stream verification](guarded-zero-stream-verification.json).

Candidate stream SHA256:
`52895ef965870babb9198ab8c3825fa0829cb8e90a1a048ab9ced7b985a78b3f`.
Patch SHA256:
`1879a2e7f315375b98afb4b1c4522188188572a218f4b64c6293ae2caf06120a`.
The two removed emitted gates are a circuit simplification, **not a rounded
mean executed saving or a valid scored result**. Peak referenced width stays
1,235. No performance plot or README record table includes this candidate.

## Full benchmark and identical-input comparison

The unchanged official benchmark tested all **9,024 shots**, exiting 1 with
**16 value mismatches, 9 phase-garbage batches, and 0 ancilla-garbage batches**.
The first value mismatch is shot 338. There is no qualified score.
[Full source, protected-file, stream and log receipt](full-benchmark-receipt.json).

An external diagnostic then used the same candidate-derived point packet and
continuous official measurement transcript for both baseline and candidate.
It first verifies identical measurement/reset operations. It compares every
final quantum slot, classical slot and phase, not just point coordinates.

| Input family | Shots | Unequal full-state batches | Value failures in each | Phase-failure batches in each | Dirty-ancilla batches in each |
|---|---:|---:|---:|---:|---:|
| Candidate's actual official packet | 9,024 | 0 | 16 | 9 | 0 |
| Independent fixed B3 domain | 256 | 0 | 1 | 1 | 0 |
| Structured fixed B3 domain | 256 | 0 | 189 | 4 | 0 |

The additional domains are the established independent/structured diagnostic
packets; they are independent of stream hashes, not newly selected packets.
The structured set includes admissible `P=-2A` and zero-slope pairs. These
**9,536 paired shots** support the exact rewrite argument but do not prove the
underlying approximate point-addition algorithm correct.
[Paired totals, binary/source bindings and packet hashes](paired-receipt.json).

The earlier launch attempt compiled successfully but exited 127 before invoking
the builder because the official shell script uses a fixed `target/release`
path while Cargo used a separate build folder. Its evidence is retained under
[failed-launch](failed-launch/receipt.json). A symlink to this candidate's own
build cache corrected the launch setup; protected files and candidate source
were not edited. The actual source was benchmarked once, without packet or nonce
search. Historical result rows remain preserved; only the normal new FAIL row
was appended in the isolated server checkout.

## Other completed and bounded research

- Two structural scans cover the complete C5 and B3 streams. The selected
  commuting shared-control, control-fusion, phase-pair and unconditional
  measurement-absorption families yield no usable sites. This is a scoped
  negative, not a circuit optimality proof.
- B3's conditional-clean-boundary audit still needs 1,235 simultaneously live
  intervals. Its first peak is operation 1,444,982. The same audit supplies the
  two zero-control leads above. [Receipt](b3-lifetimes.json).
- Moving unconditional measurements/resets to earlier depth-zero boundaries
  yields 95,225 scheduling opportunities, but still needs 1,235 qubits. No
  rescheduled candidate was emitted. [Summary](early-measurement-summary.json).
- Reapplying the public product, affine, quadratic, truth and interned passes
  after the final public rewrite tables removes only one CCX in total. No
  separate candidate or benchmark was made from that diagnostic.
  [Complete pass log](final-pass-audit.log).
- The first bounded-cone whole-stream search produced no proof: 534 SAT queries,
  81,758 cone-limit results and 5 solver-unknown results. Limits and unknowns are
  inconclusive. [Complete search receipt](b3-resubstitution-v1-result.json).
- A second local-cone trial was stopped after roughly 15 minutes with no proven
  replacement; its last flushed query was operation 4,166,100, with 3,620 SAT
  results and 609 cone limits. It is an incomplete search, not a full-stream
  negative. [Partial receipt](proof-search-v2-partial.json). SAT at an abstract
  cone boundary need not be a reachable point-addition counterexample.

Numerical signatures only proposed identities for solver checking. They were
never used to delete a gate, choose a benchmark packet, or select a nonce.

## Implication and remaining work

The public records were refreshed at the start and end of this follow-up. They
remain Q693, T761,156, and product 939,396,074. Strict targets are Q692,
T761,155, and product 939,396,073. [Dated official snapshot](../../docs/data/latest-leaderboard.json).

The immediate obstacle in this B3 experiment is **inherited correctness**, not
failure to find any exact gate reduction. Further tiny semantics-preserving cuts
carry those defects forward. The next substantial task is repairing the already
localized fold/overflow and structured-input defects, preserving the associated
phase corrections and allocator assertions, then assessing complete resource
cost. A passing hash-selected packet alone would not repair the algorithm.

The pre-existing 692-qubit bank-swap benchmark completed during final collection.
It was not restarted or interrupted. A new read-only review verified its complete
passing result and all source/stream/evaluator bindings. Its source belongs to
the overnight experiment; the terminal evidence was collected in this follow-up.
[Reviewed result](bankswap-terminal/RESULT.md).

Server workspace: `/home/hclau/ecdsa_research/followup-20261015`. Raw local logs:
`research-output/followup-20261015`. The large circuits stay on the server.
All newly launched jobs for this follow-up are terminal, including the explicitly
stopped local-cone trial. The chemistry repository and unrelated workloads were
not modified. [Artifact/source manifest](manifest.json).
