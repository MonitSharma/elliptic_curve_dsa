# Toffoli/product continuation: integrated finite arithmetic repair

15 October 2026. **One inherited arithmetic counterexample repaired and integrated
on B3; no qualified Toffoli or product record.** All jobs in this cycle are
terminal. No challenge submission or official benchmark was run. Existing known
independent/structured failures prevent qualification.

The new result is integration and validation on the low-Toffoli B3 source,
revision `b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7`. The missing-borrow defect and
its finite 57-bit mitigation were previously established on C5 in the
[fold57 component work](../overnight-20261014/product/repair57-results.md).
They are not presented here as a new discovery or a universal arithmetic fix.

## Refreshed objectives

The public API was refreshed at **09:54 Singapore**, 15 October:
minimum rounded mean executed T remains **761,156 at Q1235**; minimum product
remains **939,396,074 at Q1234/T761,261**. Strict targets are T <= 761,155 and
Q × T <= 939,396,073. At Q1235 a product improvement needs T <= 760,644.
This is a public snapshot, not a new benchmark reproduction.
[Dated records and raw-input hashes](public-frontier.json) ·
[Public API](https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74/submissions).

## Diagnosis and integrated repair

The original raw B3 arithmetic reproduces all 16 value failures on the previous
cache candidate's preserved 9,024-input packet, before any simplification passes.
It also reproduces the independent packet's one failure and the structured
packet's 189 failures. Four separately instrumented raw builds are byte-identical.
The observation-only reset simulator matches the unchanged protected simulator
on every quantum slot, classical slot, phase and executed Toffoli count across
all 9,536 inputs.

Fourteen of the 16 failing packet inputs encounter nonzero reset operands at
rail-narrowing sites. This locates unsafe discards; it does not prove that each
discard is the first cause of that input's failure. Other failures occur without
such a reset. The division invariant `P_i = slope × R_i (mod p)` independently
locates the saved independent input 94's first payload error at tick 104:
the result differs from the field reference by **2^50**.

The repair widens that forward fold from 56 to 57 bits. A source-bound adapter
restores the original ordering of returned scratch after that body. It first
requires the exact captured entry allocator; the existing allocator API then
checks that all borrowed quantum and classical scratch was returned before
restoring the saved ordering. Live owners and all allocator assertions remain.
This gets complete raw construction past the old tick-111 allocator failure.

The raw streams have an identical prefix and suffix surrounding one local
edit: old operations `[3286418, 3290600)` become new operations
`[3286418, 3290801)`. Every operation outside that region is identical.
The complete raw change adds 201 operations and two emitted CCX, with unchanged
Q1235. **These are generation diagnostics, not scored resource metrics.**

## Validation and scope

Event-aligned raw replay uses shared measurement draws outside the changed block
and independent draws inside it. The following are correctness diagnostics:

| Preserved input family | Inputs | Original value failures | Repaired value failures | Newly failing values |
|---|---:|---:|---:|---:|
| Independent | 256 | 1 | **0** | 0 |
| Structured | 256 | 189 | 189 | 0 |
| Previous cache candidate's packet | 9,024 | 16 | 16 | 0 |

Independent input 94's phase changes from wrong to correct. No other compared
phase changes occur; neither side has dirty final quantum scratch. This is
finite agreement, not an all-input proof.

The archived, unchanged decision-diagram kernel also proves the corrected local
block on **16 literal incoming contexts**, including input 94. It quantifies all
53 measurement variables inside the balanced local region, checks all 1,235
quantum slots, and establishes zero incremental phase. Native replay agrees;
the kernel rejects an intentionally added phase fault. A native continuation through the
entire remaining raw circuit gives the correct point for each context.
The prior prefix measurements are fixed; this is a local forward-map/phase proof,
not a universal, inverse, or complete point-addition proof.

## Ordinary build and retained failures

The first integrated ordinary build preserves the frozen optimization tables
and fails their input binding: `y42_bound_pass` expects 11,258,786 operations,
while the repaired input has 11,258,987. Exit 101 and the exact failed source are
preserved. The dependent fixed replay stops at its prerequisite, exit 1.
Neither failure is reported as a circuit benchmark result.

A second variant omits the three optional old-stream-only passes
(`y42_bound_pass`, `square_guard`, `linear_restore`). Their code, tables and
binding assertions remain unchanged. No table is rebound to the corrected
circuit without a new proof. This variant completes ordinary generation and
changes only `mod.rs` and `y15_onefold.rs` under `src/point_add/`.

Fixed replay of that complete generated circuit gives:

| Input family | Value failures | Phase-failing shots | Dirty quantum batches |
|---|---:|---:|---:|
| Independent, 256 inputs | **0** | **0** | **0** |
| Structured, 256 inputs | 189 | 148 | 0 |
| Previous candidate packet, 9,024 inputs | 16 | 10 | 0 |

The last row is **not this source's official hash-derived benchmark packet**.
Its failures block qualification; no diagnostic count is promoted to a score.
These standalone phase counts use different internal measurement consumption
from the paired raw test and should not be compared as an aligned phase delta.

## Evidence and next work

[Terminal receipt](evidence/receipt.json) binds exact source patches, stream and
binary hashes, inputs, logs, proofs, resource preflights and process records.
Each of the seven isolated checkouts retains all 17 tracked files outside
`src/point_add/` byte-identically. Protected harness, evaluator, simulator,
reference curve, Cargo files, toolchain and historical results are unchanged.
Research replayers are outside submissions. All failed attempts remain archived.

The exact integrated source is preserved in the
[native unbound patch](evidence/sources/candidate-fold104-unbound-b3/tracked.patch).
Its complete stream SHA256 is
`de1db9a953572c79f51a4c333d2abae4e4998afd2adb2dd1dc556ee5293f3198`.
The repaired raw stream SHA256 is
`3e8d8b30f969011d24b4394f43d8fb2a5721ae497cbc32bb6e37ec4b7c7601da`.
Large streams and fixed packets remain under
`/home/hclau/ecdsa_research/arithmetic-repair-20261015/`; bounded evidence is here.

Next, prove safe ownership/width handling at the first nonzero rail discards
and repair the structured exceptional arithmetic. Retain this borrow repair
and the earlier exact cache savings separately. Re-prove any restored frozen
optimizations against the corrected source. Only after independent checks pass
should a final source run the unchanged official benchmark, with total executed
T and Q × T compared against freshly fetched public records.

The first top-level stage trace treated the square's deferred carry as an
ordinary field register and consequently printed spurious intermediate X
mismatches at the multiply boundary. Those lines are retained as a diagnostic
limitation, not used as failure attribution. Final outputs, byte-equal observer
builds, event-aligned replay and the later rail/payload invariant supply the
usable conclusions above.
