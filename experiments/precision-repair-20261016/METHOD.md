# Public-4b fold precision study

This is a research experiment, not a scored result or a submission. The source
is public revision `4b2ec52fc55da796aa8f5ef851290297e8706424`. It is independent
of the earlier unsmoothed wide-source study. The forward 57-bit prefix here
extends through tick 99, rather than tick 55.

The gate-inert observer records the actual physical payload-window, overflow,
sign, shift and reverse-source wire IDs immediately before and after each of
263 production folds. It emits no circuit operations. Its generated final
stream must reproduce SHA256
`2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e`.
The instrumented raw body is observed before the later optimization passes;
this boundary is explicit and is not claimed to be the final circuit.

For each input, let `L` be the actual low `w` bits, `E` the three overflow
bits, `N` the three sign bits, `s=3+extra` and `f=2^32+977`. The forward
quotient digit is the unique `m` in `[0,2^s)` such that
`m*f = L+E+(E-N)*(f-1) (mod 2^s)`. Uniqueness follows because `f` is odd.
The forward correction is `C=E+(E-N-m)*(f-1)`.

For reverse folds the actual six source wires give `b`; with sign bits `n_i`,
`k=sum_i ((b XOR (63*n_i)) << i)`, `m=(L-k) mod 2^s`, and
`C=E+(E-N+m)*(f-1)`. For both directions, the observer checks the actual
written window against `(L+C) mod 2^w`, including every passing control.
The discarded signed carry is `floor((L+C)/2^w)`. This identifies a concrete
finite-precision event without treating the absence of such an event as proof
of point-addition correctness.

Each observed raw simulation is compared against the unchanged protected
simulator on every quantum wire, classical bit, phase flag and executed
Toffoli total. The final frozen stream is also simulated to label value
failures. That label excludes phase and garbage failure counts and must not
be presented as a complete fresh failure-rate census.

Training inputs are the preserved 4096 random 64-shot batches, SHA256 recorded
in `fold-risk-summary.json`. These are not an official scored or nonce
packet. A new measurement seed separates this observation from prior traces.
The ranked family is declared in `PREDECLARED-FAMILY.json` before building:
one extra precision bit at the highest-risk 1, 4, 8 or 16 fixed fold sites,
with a deterministic tie break. Each choice changes the same positions for
all inputs. This is a capacity increase, not an all-input exactness proof.
A complete candidate would need an independent fresh paired census,
including both newly passing and newly failing inputs, plus full Q and T
measurement before any claimed improvement or search.

All existing operation-table assertions remain intact. In particular,
`square_finish::run` requires exactly 11,453,250 incoming operations and the
SHA3 digest `4291f6ff7082084c23ae69a58dbfcb1237b1b0d1e9a76e8351a676e7ff00730a`.
An upstream precision change is expected to reject. Rejection is preserved;
the table is not bypassed, disabled or rebound to an unproved stream.
