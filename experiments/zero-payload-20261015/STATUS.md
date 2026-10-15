# Quantum zero-payload wrapper: proved helper, failed integration

Completed 15 October 2026. **No qualified resource score.** The reversible
equality helper passes its finite all-measurement proof, but the full wrapper
exposes a failure of its assumed nonzero division contract.

## Implementation and helper proof

The wrapper uses separate flags for physical zero encodings0 andp, a quantum
AND ladder for exact equality, and measurement-based scratch cleanup with its
conditional phase correction. It maps a zero division payload to x, expecting
the oracle to return1; multiplication maps zero to1, expecting x. It then
restores the original zero encoding and uncomputes the flags.

The helper exhausts174760 cases at widths1–8: every input word, every equality
pattern and both initial flag values. All measurement outcomes pass in2750
BDD batches. Removing a measurement phase correction is rejected by the
negative test. This proves the tested helper domain, not the full arithmetic
oracle or wrapper. Direct wrapper gates add2552 Toffolis across both calls,
before allocation-plan changes or disabling shortcuts.

Both control and wrapper disable `LF_SEAMS`, `SL_RT0` and `LF_T6_SEEDFUSE`,
using the existing explicit coordinate operations. They inherit the preserved
wide dynamic-pool parent. Source changes remain inside `src/point_add/`;
protected simulator, evaluator, curve reference, Cargo files and toolchain
match B3.

## Complete fixed-input diagnostics

| Variant | Family | Shots | Wrong values | Phase shots | Final dirty batches |
|---|---|---:|---:|---:|---:|
| Control | Independent | 256 | 0 | 0 | 0 |
| Control | Structured | 256 | 128 | 122 | 0 |
| Control | Preserved candidate | 9024 | 5 | 4 | 0 |
| Wrapped | Independent | 256 | 0 | 0 | 0 |
| Wrapped | Structured | 256 | 254 | 135 | 0 |
| Wrapped | Preserved candidate | 9024 | 5 | 7 | 0 |

The wrapper introduces wrong values on126 of the128 zero-slope inputs. The
old five random-packet failures remain. Final clean-ancilla counts are not a
proof that every intermediate release was clean; the observer below finds a
flag that failed to uncompute before reuse.

Diagnostic peak widths are1535 (control) and1534 (wrapped). Independent256
executed T totals are193278173 and193921692. These failed-circuit counts are
not scored resources and are excluded from performance plots.

The control's BDD phase witness is native-verified. The wrapper's BDD reports
nonzero phase at measurement709221 / operation8770285, but its native witness
runner exits101 on wrong point values before completing the certificate. Do
not describe that incomplete run as a native-verified phase counterexample.

## Verified oracle-interface counterexample

A separate raw observer uses the first preserved zero-slope input with all-zero
measurement outcomes. It matches the protected simulator in every quantum
word, classical bit, phase and executed Toffoli count.

The zero detector correctly sets flags[1,0]. After substitution, both division
input registers contain
`0x238cf0d6ea5553feef21463b70e36e06d696732ae22bfc153ad1bebd73c2efe1`.
The denominator is restored exactly, but the payload output is
`0x3ffffffffffffffffffffffffffffffffffffffffffffffffffd38e34e38e2a1`,
**not1**. XORing1 therefore fails to restore zero, and the zero flag remains1
after attempted uncomputation. Both final point coordinates are wrong.

The actual production oracle on this substituted input does not satisfy the
contract required by the algebraic wrapper. The small-field model and equality
proof remain valid within their stated assumptions; they cannot qualify this
integration. The observation is one fixed input, not a general classification
of the oracle's defects.

Next run an equal-input division probe on the explicit-interface control
without the two held zero flags. This distinguishes an inherited correlated-
input defect from an allocation-dependent change. Then trace the first
arithmetic divergence before changing the wrapper or its expected constant.
Do not search alternative substitute constants merely to pass these packets.
The independent zero-multiplier and rail failures remain unresolved.

## Evidence and terminal status

Control PID3179293 exited0; wrapped PID3179294 exited101 only at the final
phase-witness assertion, after generation and all fixed replays; observer
PID3188447 exited0. No job from this cycle remains active. Unrelated census
and guard-sweep work was left untouched.

All81 artifacts, three source patches and the external runner patch pass
[local verification](local-verification.json).
[Receipt](evidence/receipt.json) · [Analysis and interface values](evidence/analysis.json).
Control stream: `1d9372a5ddd7ee92aedd62f82539d97d92700e3d7bc5267535835bea68e1b7d1`.
Wrapped stream: `116ccf31c929da1147489130e552fbd348063f0d458527e1a158a2555aa8aaed`.

Public refresh at13:22 Singapore:1567 submissions,1225 eligible records and46
frontier points. The Toffoli and product targets remain unchanged.
