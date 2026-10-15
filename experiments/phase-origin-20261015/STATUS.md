# Phase source attribution and terminal exact-flag route

15 October 2026. All experiments terminal, no qualified resource record.

## Source attribution

Gate-inert caller/backtrace instrumentation reproduces the previous square-room
stream **byte for byte**, SHA256
`48e2f0d8ad9bdc492415ec2700fe5dda9edc0e6f1b3a21eb935ef61ecc3953a4`.
The witnessed Hmr neighborhood is emitted at raw operation6995342 by:

`n2_pay_rev_last → merged_rev → merged_rev2 → cells::flag_erase → erase_with_compare`.

This is the terminal reverse multiplication payload kernel. Its exact overflow
route is requested, but `merged_split` returns None under the available room,
so it falls back to a truncated flag comparison. The instrumented Hmr matches
qubit1191, bit515 and the preceding CX1191→207 of the final-stream witness.
There is one matching source observation. [Generation/backtrace](evidence/generation.log.gz).

The unchanged exact BDD/witness runner also confirms a phase counterexample
on the current **combined** source: measurement551602, operation7130181.
All-zero outcomes give phase0; flipping that one outcome gives all-one phase
with correct output values on the first fixed zero-slope input replicated64
times. This binds the failure to the current source independently of the old
square-room stream. All indices are zero-based.

## Structural candidate

`terminal-b3` starts from the combined square/140-round repair. Only the
terminal reverse payload kernel receives a temporary capacity reservation:

    cap = max(previous_cap, active + 1 + m_fold_need(true) + 2)

This follows `merged_split`'s existing bound: the derived room makes its split
at most N-2, retaining at least two top bits for exact overflow erasure. There
are no packet-derived settings, identity-tail changes or protected-file edits.
The candidate asserts the exact split exists before emission.

At tick139, active=1207, fold_need=73, cap=1283, split=254. The builder observes
peak1282. These are diagnostic widths, not a scored result. Candidate stream:
`7d4472c3bf0d5d4ee67e45e9d1f34c5e741014578a2bf17eeaa0cba06b4c83ee`.

| Fixed packet | Shots | Wrong values | Phase failures | Dirty batches |
| --- | ---: | ---: | ---: | ---: |
| Independent | 256 | 0 | 0 | 0 |
| Structured | 256 | 128 | 118 | 0 |
| Old candidate | 9024 | 5 | 5 | 0 |

Wrong-value sets remain unchanged: the five rail cases and all128 P=-2A
zero-multiplicand cases. Phase measurements are not event-aligned across the
arithmetic change; the numerical count differences do not establish savings
or a monotone phase improvement.

The new full-stream BDD result is still nonzero. Its native-verified witness
flips measurement **551557** at operation **7129563**, Hmr qubit **562**, bit
**549**. Values remain correct, phase flips from0 to all ones. Immediately
before it are the retained top-frame's five phase corrections and unwind;
immediately after is a conditional comparison. This is consistent with the
remaining split-carry comparison in `add_consume_exact`, but that source
attribution still needs its own byte-identical observation. The helper's name
promises exact overflow cleanup; its lower split-carry cleanup remains
windowed. Do not treat the whole merged operation as exact.

## Independent primitive contract

The unchanged B3 `ripple_add_consume` and `erase_overflow_from_frame` sources
are byte-identical to the candidate. Exhaustive widths1..8 cover **174760**
integer operand/carry-in cases. Every batch passes the frozen BDD kernel for
all measurement outcomes (**2732 proofs**) and agrees with the protected
native simulator. The consumer XORs the overflow into an external output with
a deterministic dirty pattern; this pattern is not an exhaustive independent
dirty-output dimension. All source wires, sums, carry-in and scratch match the
integer specification. Removing the source-top phase correction is detected.
Both tests pass. This finite primitive contract does not prove the surrounding
fold, truncated boundary comparison, or full point addition.

## Evidence and next action

Source trace PID3114272, combined audit3116092, terminal candidate3117084 and
component proof3118818 all exited0. Three isolated checkouts retain only
`src/point_add/` edits. All71 artifacts, three patches and the external proof
runner patch pass [local hash verification](local-verification.json).
[Receipt](evidence/receipt.json) preserves source/protected hashes, packets,
binary and stream hashes, logs, tests and precise failure sets.

Next observe the new Hmr562/bit549 with preceding CX510→872, then address the
actual split-carry predicate across the fold. A full-width comparison after
the fold is not automatically valid because the fold changes low target bits.
Preserve the exact overflow route and consider retaining the needed carry or
pre-fold information with a proved cleanup contract. Rail and zero-multiplicand
repairs remain independent requirements. No official benchmark or submission
was run; plots remain unchanged.
