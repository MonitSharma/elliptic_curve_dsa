# Rail controls and square integration: terminal research results

**No qualified resource score.** This continuation separates rail truncation,
walk convergence and structured arithmetic defects. All submissions are isolated
B3 checkouts; only `src/point_add/` changes. Existing fixed packets and the
protected simulator are retained. No nonce or packet tuning is performed.

All jobs in this cycle are terminal. **143 archived artifacts, five checkout
patches and the external research-crate patch are verified locally.** Protected
files match B3 in all five checkouts. [Terminal receipt](evidence/receipt.json)
· [Evidence archive](evidence.tar.gz) · [Integer certificates](analysis.json).

| Variant, planner allowance 1267 | Known15 wrong | Independent256 wrong | Structured256 wrong | Old packet9024 wrong |
|---|---:|---:|---:|---:|
| Original rails, tick104 repair | 15 | 0 | 189 | 16 |
| +1 interior rails, prior cycle | 11 | 0 | 189 | 10 |
| +1 rails plus exact square | 11 | 0 | 128 | 10 |
| +3 interior rails | 10 | 0 | 189 | 8 |
| +3 rails and two extra rounds | 7 | 0 | 189 | 5 |

All have clean final quantum scratch in these tests. Independent256 has zero
phase failures in each variant. Other families retain phase errors. These are
fixed correctness diagnostics, not evaluated Toffoli/product records, and
measurement events across arithmetic rewrites are unaligned.

The two extra rounds remove old-packet failures 421, 553 and 6972 relative to
the +3-margin 138-round source. The five remaining inputs are 562, 720, 2777,
3447 and 8322. The square repair and longer walk have been tested separately;
their benefits are not yet established together in one final source.

The scratch-only control and pre-Y33 observer are terminal, exit 0 (PIDs
3086738 and 3086739). Raising the planner allowance to 1267 without changing
rail widths leaves 16 wrong values on the old 9,024-input packet. The +1
interior-width variant at the same allowance leaves ten. Its failing set is
a strict subset: six failures disappear and no new failing input appears.
Both pass independent256 and leave 189 wrong structured values.

The observer matches the unchanged simulator in every quantum slot, bit,
phase and executed count on all 9,551 inputs. Eight of the ten remaining packet
failures have exact forward-rail integer counterexamples. The other two are
shots 421 and 6972, whose endpoint rails are (-1,-3) and (-3,1), respectively,
rather than the required ±1. Raw and optimized streams have the same ten
wrong-value inputs. This does not establish phase equivalence across optimized
streams; measurement events across arithmetic variants are unaligned.

`analysis.json` independently certifies the rail maps and input geometry. The
structured set has 128 cases P=-2A with zero multiplication operand, plus 128
zero-slope cases. All 128 P=-2A outputs are wrong in y; 61 zero-slope outputs
are wrong. In each zero-multiplicand case, the input slope equals the classical
offset's tangent slope, 3 a² / (2 b) mod p. This motivates a separate reversible
exception treatment; it is not an implemented repair.

## Completed square proof and phase attempts

Square integration (PID 3090482, exit 0) applies the archived exact uniform +2
square contract to the +1 rail / cap1267 source. Its three production component
tests pass: 245,760 native cases, 15,360 fixed-input/layout all-measurement
proofs, and a meaningful dirty-loan phase fault. These are finite component
proofs, not universal-input point-addition correctness. The complete ordinary
build/replay fixes all 61 zero-slope value failures. The 128 P=-2A y failures
and phase errors remain.

Larger margin/convergence (PID 3093742, exit 0) builds both predetermined
variants normally. The second appends two width-six rows to make 140 rounds
and preserve the odd terminal target. Each generation exits 0.

The initial external full-stream phase runner fails compilation (PID 3096286,
exit 101); its source and log are preserved. An explicit index-type fix in a
separate runner passes all four kernel tests. Both the 64-unique-input audit
(PID 3098264) and the first-fixed-input audit (PID 3100124) finish exit 0 but
reach the frozen kernel's XOR term cap. **Both audits are inconclusive.** The
native all-zero-measurement checks have clean phase and correct values, but do
not establish correctness for other measurement outcomes or locate a phase
fault. No counterexample origin was obtained.

## Next research steps

Combine the independently validated square repair with the longer walk, trace
the five remaining fixed packet failures on that exact source, and distinguish
further truncation from fold/endpoint failures. Instrument the phase engine's
cap location before increasing resources or changing its representation.
The zero-multiplicand exception needs its own reversible treatment; see the
[algebraic design and implementation obligations](exceptional-multiplication.md).

Each job used four build threads, one library thread and a 16 GiB process limit.
Dedicated targets, logs and PID records are under
`/home/hclau/ecdsa_research/rail-control-20261015/`.
