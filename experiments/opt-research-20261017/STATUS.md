# Gate-level search for further exact savings on PLAIN67: diagnostic, no candidate

17 October 2026, Singapore. **No resource result, no candidate.** A new
research tool (`tool/`, built on the server at
`/home/hclau/ecdsa_research/opt-research-20261017/tool`) profiled the final
PLAIN67 stream (`f2279f98…`, Q1234) and tested four exact optimization
families. None produced a provable saving. The tool never edits a submission.

## Profile (65,536 fresh shots, label `prof-v1`)

Mean executed Toffoli 761,120.56; 148 failed batches of 1,024 (λ ≈ 20 on this
small sample), 0 dirty. The two modular-division walks hold about 700k of
the T (ops 0–5.4M and 12.5M–17.9M); the middle (square and glue) about 40k.

| Toffoli class (empirical, over 65,536 shots) | Sites | T per shot |
|---|---:|---:|
| Executed, never fires, a control never 1 | 2,082 | 1,919 |
| Executed, never fires, both controls often 1 (exclusive) | 489 | 485 |
| Executed, never fires, other | 675 | 631 |
| AND always equals one control (acts as a CNOT) | 822 | 762 |
| Fires in < 0.1% of executions | 22,862 | 20,974 |
| Everything else | 788,751 | 736,349 |

Removing or weakening a gate because it *rarely* fires would be a census-style
cut and is not allowed. Only gates that provably never fire (or provably act
as a CNOT) for every input and measurement outcome would be exact.

## Families tested

1. **Local truth-table proofs** (`prove`): backward liveness slice from each of
   the 4,068 candidate sites, cut where at most 20 or 24 resources are live,
   every live value and measurement outcome free. **0 proven.** The exclusive
   sites are adder carries inside the walks whose impossibility depends on
   value ranges of the walk registers (algorithmic invariants or rare events),
   not on local structure.
2. **Compute/uncompute Toffoli pairs** (`pairs`): 5,122 pairs with unchanged
   controls, all under different condition stacks (the authors' guard trees);
   no same-context pair exists for measurement-based uncomputation.
3. **Guard sinking** (`sink`): a Toffoli into a fresh ancilla whose every
   reader shares an extra stable condition bit. **0 candidates** among 501,719
   fresh-target Toffolis.
4. **Width** (`liveness`): 1,234 qubits are simultaneously live for about
   321,000 ops, so no relabelling can remove a qubit. Consistent with the
   earlier Q1233 loan analysis (more than 750 T of paid rules).

## What this implies

The remaining width-free exact savings at Q1234 are the cache continuation
(PRODUCT95, +10.6 T over PLAIN67, now qualifying) and possibly deep
walk-level algorithmic work. Proving the walk invariants would need an
inductive range argument over the leapfrog walk, not local slicing.

Files: `tool/src/{main,prove,io}.rs`. Server outputs: `plain67.stats4`
(per-op counters), `prove-cap20.tsv`, `prove-cap24.tsv`, `excl.tsv`.
