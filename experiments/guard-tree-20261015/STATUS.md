# Exact guard review and cubic substitution: terminal negative results

15 October 2026, night. **No resource improvement, candidate qualification or
nonce search.** Work stayed in this experiment directory and its matching server
directory. Coordinator source files were not changed.

The coordinator's lazy AND pass was independently strengthened in three safe
ways: permit arbitrary descendants and extra uses of the unchanged measurement
outcome; reconstruct original controls from stable exact value-holder aliases;
and permit a dirty target `g XOR f` rather than requiring the measured wire to
hold only `f`. A further version snapshots a per-operation producer guard before
that old classical bit can change. The producer must be outside an enclosing
condition stack; its snapshot and scratch flags are initialized unconditionally.

Seven native tests pass, including all basis inputs and measurement assignments,
dirty new classical scratch, an original control measured before its use but
retained in another alias, arbitrary dirty quantum target, producer guard mutated
before the first read, and a deliberately missing phase guard. The dirty-target
fixture was corrected to explicitly initialize its independent sixth input bit;
the corrected test passes.

On the official wide stream, every version still selects only three sites.
Complete paired checks of 256 independent inputs under four measurement seeds
(1,024 shots) show identical **every quantum word, every old classical bit,
phase and RNG byte consumption**, with new flags clean at the end and unchanged
Q1464. **Measured executed Toffoli savings are zero.** No census or score is
claimed for these variants.

The exact proof is pointwise on arbitrary input basis states and measurement
outcomes. Let `f=a*b`, `g` be the pre-existing target and `v` indicate whether a
guarded read caused the AND to be computed. All active reads see `g XOR f`;
before the first active read they are inactive. At HMR outcome `m`, original
phase is `m(g XOR f)` and candidate phase is `m(g XOR v*f)`. Guarding one exact
`m*f` CZ twin by `v` leaves **`m*g` in both circuits**. Hence the target need
not be clean. Old HMR/R operations and their draws remain in their original
relative order, so arbitrary original classical uses and descendants are
unchanged. Reconstructed hosts are restored immediately; cross-site host reads
of another modified target are rejected. The guarded-producer extension captures
its original enabled predicate, and requires the exact twin's value-context to
equal producer-context plus the HMR outcome.

A separate generic phase substitution allows Z/CZ-only AND uses. It substitutes
`CZ(AND(a,b),z)` with the exact cubic phase, expanding affine forms and reducing
duplicate Boolean variables. It removes the clean AND producer and its exact
HMR twin while retaining every measurement. A native all-input, both-outcome
fixture with an affine changed control passes. **The wide stream admits zero
strictly cost-positive sites**, so this pass gives no measured improvement.
Additional exhaustive affine-polynomial tests are prepared locally but were not
part of the completed server run. They must not be reported as executed.

## Public carry-tree source binding

An isolated detached worktree of `4b2ec52f` dumps the exact input immediately
inside `square_finish::run`, using the unchanged build serializer. This is a
research pre-table component stream, **not a complete final candidate**:

```text
11,453,250 operations
raw SHA3-256: 4291f6ff7082084c23ae69a58dbfcb1237b1b0d1e9a76e8351a676e7ff00730a
```

This exactly matches the public table binding. The server retains
`before-square-finish.bin`, source patch, generation/build logs and stream hash.
The decoded region is in [public-region.log](evidence/public-region.log).

The actual first public tree deletes the composite carry construction at
5,499,253–5,499,256: one CCX into clean918, XOR379 into918, and fanout into381
and967. The first guarded reader is5,499,325; intervening conditional HMRs
create measurement values1651–1654. Symbolic inspection shows967 initially
holds a nonconstant value, whereas918 is clean. This is not a sole AND leaf.

The rewrite also **adds** a conditional HMR967 at its first reader; the protected
simulator draws an RNG word even when the condition is zero. Consequently its
full semantic proof requires explicit treatment of extra draws, reused classical
outcome1655 and the larger carry cone. The current strict unchanged-draw lazy
proof does not establish this public tree. No speculative alpha-port was made.

## Preserved attempts and limits

The initial full vector-of-aliases snapshots grew to35GiB and were stopped by
terminating only this experiment's process. Its tests/build/partial transform
logs are retained. A bounded alias-pair implementation finished in about30s at
about3.4GiB. The subsequent eligibility filter snapshots only producers with no
intermediate target write before HMR. An inspection launched before the dump was
ready failed; its log is retained, then the completed source-bound dump was
successfully inspected. No unrelated process was changed.

Server directory: `/home/hclau/ecdsa_research/guard-tree-20261015`.
All jobs are terminal. Native tests, source snapshots, complete paired logs,
dump source and hashes remain there and in the evidence archive. Prepared source
and observed source revisions are distinguished by the archived manifest.
