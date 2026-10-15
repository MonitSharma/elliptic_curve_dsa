# Equal-input division: inherited failure and negative fold boundary

Completed 15 October 2026. **Component diagnosis only; no qualified score.**

The no-wrapper control reproduces exactly the division failure previously
seen with the zero-payload wrapper. Holding its two flags is therefore not
necessary to trigger this failure. A uniform extra forward fold bit does not
repair it: the first error remains at tick120 and doubles in magnitude.

## Isolated arithmetic probe

The raw control stream is unchanged by read-only instrumentation. The probe
runs the existing coordinate prefix, verifies an empty classical-condition
stack at both division boundaries, then sets only the simulated payload to
one of four predeclared values. No gates or wrapper flags are added. The
denominator is the first preserved zero-slope input's post-coordinate value:

`0x238cf0d6ea5553feef21463b70e36e06d696732ae22bfc153ad1bebd73c2efe1`.

Each case uses64 identical lanes and all-zero measurement outcomes. The
observer and unchanged protected simulator agree in all quantum words,
classical bits, phase and executed Toffoli count. The denominator is restored
exactly in every case. These injected inputs test division as a component;
they are not complete on-curve point-addition benchmarks.

| Payload | Original control | Uniform forward fold57 |
|---|---|---|
| x | Wrong; exactly the prior wrapper's non-unit output | Wrong; changed output |
| 0 | Correct value0 | Correct value0 |
| 1 | Wrong inverse value | Same wrong value |
| p−1 | Wrong negative inverse value | Same wrong value |

All observed phases are0 because the assigned measurement outcomes are zero.
This is not a phase proof.

## First observed divergence

Exact modular checks cover131 ordinary forward payload ticks for y=x, before
the N2 batch. Ticks0–119 match their stated field update. At tick120:

- Target T=229 and source S=p+217, with p the secp256k1 modulus.
- The signed source coefficient is−5 and the shift is3.
- The correct result is `(T−5S)/8 mod p = p−107`.
- Original56-bit fold returns `2^53−107`, an error of2^53 modulo p.
- Uniform57-bit forward folds return `2^54−107`, an error of2^54 modulo p.

The source register is unchanged across this tick. Its physical value p+217
is outside the canonical field range, even though earlier observed updates
remain correct modulo p.

## Exact boundary calculation

The complement signs for coefficient−5 are(+,-,-), with complement weight6.
The unsigned summed word is `2^256 + 5f − 862`, where f=2^32+977, so its top
overflow is1. The production fold equation with quotient m=0 gives−856.
Wrapping that result in a56- or57-bit window and dividing by8 reproduces
both observed outputs exactly. Full field reduction would give p−107.

This calculation strongly identifies a negative-fold boundary problem; it
does not directly observe the internal quotient or borrow wires. Merely
increasing a truncated window preserves this counterexample and increases
its numerical error. A general repair must handle the borrow across the
window or establish and maintain a representation invariant that excludes it.
[Exact arithmetic calculation](evidence/fold-counterexample.json).

Next instrument the tick120 fold's input, quotient and borrow state to verify
that internal path, then derive a reversible correction with a component
phase proof. Also retain the independent failures for payload1 andp−1; this
single correlated-input diagnosis does not explain all division errors. Do
not tune substitute constants or select hash packets to avoid them.

## Evidence

Observer PID3199075 and uniform-fold control PID3201429 exited0. Both sources
are isolated checkouts; changes are confined to `src/point_add/` and protected
files match B3. Both emitted streams are raw pre-Y33 diagnostic streams, not
new final candidates. All64 artifacts, two patches and the external runner
patch pass [local verification](local-verification.json).

[Receipt](evidence/receipt.json) · [Original analysis](evidence/observer-analysis.json) ·
[Uniform-fold analysis](evidence/fold-analysis.json).
All jobs in this cycle are terminal. Existing root edits, track submodules,
width evidence and unrelated server workloads remain preserved.
