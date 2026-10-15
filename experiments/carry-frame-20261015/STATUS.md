# Carry predictor diagnosis and width-for-Toffoli control

15 October 2026. All jobs terminal. No qualified Toffoli/product record,
official benchmark, submission or new result-plot point.

## Exact source and operand evidence

Gate-inert source tracing reproduces the terminal parent stream byte for byte:
`7d4472c3bf0d5d4ee67e45e9d1f34c5e741014578a2bf17eeaa0cba06b4c83ee`.
The Hmr562/bit549 neighborhood comes from `pingpong.rs`'s split-carry cleanup
inside `add_consume_exact`, reached through the terminal `merged_rev2` cell.
The raw source position is7125269; the prior final-stream witness was7129563.

The independent pre-Y33 observer uses the first preserved zero-slope input,
replicated into64 lanes, with all measurement outcomes zero. It agrees on
every quantum/classical wire, phase and executed count with the protected
simulator, and returns the correct point. Before and after the fold:

    target = source = 2^254 - 2^32 - 977
    actual split carry = 0
    exact full comparison = 0

The17-bit window instead receives a predicted borrow of1 from a source bit,
and therefore returns1 on the equal operands. The fold leaves these operands
unchanged in this counterexample. This identifies the heuristic source seed
as the immediate defect; it does not establish that widening comparisons
after other folds is valid. Raw observation stream:
`f9f2a24bee31eed569f7f100d44357c36a5a4af634126f85df1bde799759ab85`.

## Terminal policy experiment

`unseeded-b3` removes that source-bit predictor throughout the terminal reverse
exact-overflow boundary and replaces its17-bit comparison with an unseeded
18-bit comparison. The policy is structural, with no test-packet or hash-tail
changes. It is still a truncated comparator, not a general exact repair.

An independent-word model exhausts582544 pairs at widths2..8. For independent
uniform n-bit operands and a k-bit window with its adjacent source-bit seed:

    seeded error probability          = 2^(-k-2)
    (k+1)-bit unseeded error probability = 2^(-k-2) - 2^(-n-1)

The widened policy also fixes every equality case in that model. These are
predicate-distribution results, not a claim about actual folded payloads.
[Exhaustive model](compare-model.json).

The candidate stream is
`b26a283aab80a23b36ba7ef75d3d35b5f25d97dde759270a53a45691603144d0`.

| Fixed packet | Shots | Wrong values | Phase failures | Dirty batches |
| --- | ---: | ---: | ---: | ---: |
| Independent | 256 | 0 | 0 | 0 |
| Structured | 256 | 128 | 129 | 0 |
| Old candidate | 9024 | 5 | 4 | 0 |

Value failure sets are unchanged. Phase events move with the circuit; count
differences are not aligned savings or proof of monotone improvement.
The full-stream exact BDD audit still finds a native-verified counterexample:
MR551447 / operation7127612, Hmr qubit1176, bit549, preceded by CX447→954.
Flipping only that outcome changes phase0 to all ones with correct values.
This earlier measurement needs source attribution before a further repair.

## Larger working allowance: failed construction

The predeclared cap1536 control changes only the dynamic walk allowance of
the unseeded candidate. It exits101 during generation at `y42_alloc_set`:
the payload operation changes the free-wire set. No stream or scored count
exists. The assertion and both sets remain in the archived log.

The dynamic normalization in `leapfrog.rs` still calls `y42_alloc_set` even
with the old bound allocation tables disabled. Investigate whether the wider
operation introduces fresh, subsequently returned wires beyond its snapshot.
Do not remove the assertion or discard unexpected live wires. A valid repair
must retain strict checks for old-wire leaks, duplicate frees and live fresh
wires while accommodating proven fresh idle capacity. This is the next
practical prerequisite for measuring the larger-width Toffoli tradeoff.

## Separate zero-input wrapper model

[A finite permutation model](zero-guard-model.json) verifies21288 cases and252
maps across seven small primes. Given canonical nonzero multiplier x and a
phase-correct canonical nonzero multiplication oracle, separate flags for the
two physical zero encodings0/p can map either zero to1, multiply, XOR x on the
flagged branch, restore the original zero encoding, and uncompute both flags.
This preserves both zero encodings and the nonzero multiplication permutation.
It is an algebraic design only: no quantum implementation, gate count or phase
proof. It does not handle x=0; the actual multiplication encoding, coordinate
seams and seed fusion need explicit contracts before integration.

## Evidence

Origin PID3122971, operand observer3126032 and unseeded candidate3128221
exited0. The cap1536 control3130991 exited101. Four isolated checkouts change
only `src/point_add/`; protected sources match B3. All91 artifacts, four patches
and the external proof-runner patch pass [local verification](local-verification.json).
[Receipt](evidence/receipt.json) retains sources, packets, stream/binary hashes,
logs, failure sets, tests and terminal statuses. Earlier width evidence and
all historical experiments remain intact.
