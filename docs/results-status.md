# Results and submission status

Updated 15 October 2026. **We have one new complete local width result and no
submission-ready original circuit yet.** The three objectives remain independent:
a lower-Toffoli result would count even if its product were worse.

**Current research priority:** lower executed Toffolis and lower Q × T.
Width-only optimization and Q692 submission engineering are deferred; existing
width results and failures remain preserved.

**Honest correctness (parallel Claude agent):** we keep the no-nonce rule, so a
circuit must pass a *fresh* hash-derived test set on its own. A census of
262,144 independent inputs per stream gives these fresh-pass probabilities:

- the public B3 Toffoli record about 2–6×10⁻⁹ (two independent censuses);
- the C5 product baseline about 1.5×10⁻⁸;
- the best of the 29 streams built today about 10⁻³.

A gate-inert trace places 155 of the wide circuit's 186 value failures in the
leapfrog walk rails, whose width table was fitted with a stated 0.00077-per-walk
drop budget.

| Walk widening (diagnostic only) | Q | Diag. T | Failed batches/packet |
|---|---:|---:|---:|
| Wide parent | 1464 | 753,727 | 7.16 |
| +2 rail bits only | 1464 | 758,411 | 7.30 |
| Smoothed tail only | 1464 | 753,764 | 5.77 (3 replicates) |
| +2 rail bits and anchors, smoothed tail | 1464 | 758,446 | 4.18 (3 replicates) |
| +4 / +6 rail bits and anchors, smoothed tail | 1468 / 1472 | 763,076 / 767,661 | 4.78 / 5.37 |

Tail smoothing is free; rails must widen with their YP8 anchors; more than
+2 bits stops helping (the tail cliff returns, and non-walk failures rise with
width). Convergence-aware envelopes with a rebuilt tail descent eliminate
unconverged walks and halve walk failures (762,908 T, 3.79), but non-walk
failures rise, so every walk-only lever plateaus at about 3.7–4.2. A constant ~1.1 batches of non-walk failures remains.
None of these is close to the < 0.1 expected failed batches needed.
[Census and figure](../experiments/failure-census-20261015/STATUS.md) ·
[trace](../experiments/trace-value-20261015/STATUS.md) ·
[widening](../experiments/widen-walk-20261015/STATUS.md).

**Latest arithmetic diagnosis:** the equal-input division failure reproduces
without wrapper flags. Forward tick120 first violates its exact payload update;
an extra fold bit doubles rather than fixes the error. Exact arithmetic points
to a negative result wrapping inside the truncated fold window. All64 evidence
artifacts are verified. This identifies a repair target, not a new resource result.
[No-wrapper control and fold-boundary evidence](../experiments/equal-division-20261015/STATUS.md).

**Latest wrapper integration:** the equality helper passes exhaustive small-width
phase checks, but the full wrapper introduces126 new structured value failures.
A verified interface observation finds division y=x returning a non-unit value,
violating the wrapper's assumed contract. Its native phase certificate is
incomplete because point values are already wrong. All81 artifacts are preserved
and verified; no new Toffoli or product score qualifies.
[Failed integration and exact evidence](../experiments/zero-payload-20261015/STATUS.md).

**Latest exact diagnosis:** reverse tick1 requires the opposite comparison
borrow from the earlier forward witness. Both reconstructed carries are correct
on the observed input, so a constant-predictor change cannot repair both phase
errors. All57 source/state artifacts are verified. An algebraic zero-payload
wrapper passes42576 finite divide/multiply cases; it has no quantum implementation
or measured resource result yet.
[Diagnosis and next exact design](../experiments/y15-carry-source-20261015/STATUS.md).

**Latest comparison-policy experiment:** removing statistical Y15 comparison
seeds uniformly passes independent256 in narrow and wide circuits, but retains
the same value failures and native-verified phase counterexamples. Diagnostic
Toffolis increase and peak widths are unchanged. The wide fixed-packet phase
count fell from5 to1, with changed measurement events; no record qualifies.
Both runs and57 evidence artifacts are terminal and locally verified.
[Candidate results](../experiments/y15-unseeded-20261015/STATUS.md).

**Latest diagnosis:** exact observation at forward tick124 separates the two
suspected approximations. The rebuilt carry is correct; a source-bit borrow
predictor incorrectly distinguishes equal comparison operands and adds phase.
The intended measurement flip and complete simulator-state agreement are
verified. All83 artifacts preserve the successful observation and earlier
failed/misaligned attempts. This is a diagnosis, not a new resource record.
[Exact carry evidence](../experiments/joint-carry-20261015/STATUS.md).

A subsequent byte-identical observer attributes the wider circuit's phase
witness to division's joint carry cleanup. Both its truncated carry reconstruction
and comparison predictor require investigation. All 35 observer artifacts are
verified; this is source attribution, not a correctness repair or score.
[Phase source](../experiments/wide-phase-20261015/STATUS.md).

**Latest wider-circuit experiment:** a strict allocator repair passes six
tests and preserves the old stream exactly. A larger allowance reduces fixed
diagnostic executed Toffolis by about2.21%, but worsens the product and leaves
arithmetic/phase failures. All55 artifacts and two patches are verified;
no new resource score qualifies.
[Terminal evidence](../experiments/dynamic-pool-20261015/STATUS.md).

**Latest carry diagnosis:** an exact native observation identifies a false
source-bit borrow prediction on equal operands. A wider unseeded terminal
comparison preserves prior value results but leaves another phase witness.
The larger-width Toffoli control fails construction before producing a stream;
neither experiment supplies a qualified resource result. All91 evidence
artifacts and four source patches are locally verified.
[Carry experiment](../experiments/carry-frame-20261015/STATUS.md).

**Latest phase continuation:** source tracing identifies a terminal overflow
comparison. A structural capacity reservation enables exact overflow cleanup,
with174760 finite primitive cases and2732 all-measurement proofs passing.
The full candidate retains another phase counterexample and the prior value
failures; diagnostic peak1282 is not a scored width or product result.
[Source attribution and terminal evidence](../experiments/phase-origin-20261015/STATUS.md).

**Latest integration:** square and longer-walk repairs coexist, passing all
256 independent inputs and all zero-slope values. Five old-packet rail
overflows and 128 zero-multiplicand failures remain. An exact full-stream
decision-diagram check of the prior square-room circuit now provides a
native-verified single-measurement phase counterexample. These are correctness
diagnostics, with no new qualified Toffoli or product result.
[Terminal source and evidence](../experiments/repair-integration-20261015/STATUS.md).

**Latest cache continuation:** larger immutable symbolic expressions increase
the paired saving from 74.91796875 to 101.109375 executed Toffolis per shot,
using one more cache qubit (diagnostic Q1240). Both fixed 256-shot packets
preserve every state and phase, including inherited failures. This is a component
improvement with no qualified score.
[Completed cache evidence](../experiments/cache-retention-20261015/STATUS.md).

Complemented-control caching passes native proof and full replay but adds no
measured saving. Larger retention on idle wires regresses from 4.015625 to
3.0625 saved Toffolis per shot; the older narrow configuration remains preferred.
[Complemented-cache](../experiments/cache-polarity-20261015/STATUS.md) ·
[Idle-cache](../experiments/cache-idle-20261015/STATUS.md).

**Latest controlled continuation:** three extra interior rail bits plus two
more walk rounds reduce the old packet's wrong values to five, with all 256
independent inputs passing. A separate exact-square integration fixes all 61
zero-slope wrong values; 128 P=-2A failures and phase defects remain. The
square's native/all-measurement component contracts pass at cap1267. Two
full-stream phase audits are inconclusive due to complexity limits. These are
partial correctness repairs, not qualified Toffoli or product results.
[Terminal controls and proof evidence](../experiments/rail-control-20261015/STATUS.md).

**Earlier rail-headroom continuation:** a broader interior-width repair with
additional scratch passes independent256 and leaves 10 wrong values on the
preserved 9024-input packet, down from 16. Known15 leaves 11; structured256
still leaves 189. Diagnostic Q1267 is not a qualified resource record. A
scratch-only control is needed to isolate the cause of the finite improvement.
[Terminal headroom evidence](../experiments/rail-margin-20261015/STATUS.md).

**Earlier rail continuation:** fourteen of sixteen packet failures now have
exact forward-rail counterexamples. The widened choice primitive passes its
finite exhaustive/phase proof, but the full tick-109 repair moves the known
overflow to tick 110 and still fails the final point. No Toffoli or product
result qualifies. The refreshed public product is 939,347,948 at Q1234/T761,222.
[Completed experiment and evidence](../experiments/rail-repair-20261015/REPORT.md).

**Earlier repair continuation:** the known B3 tick-104 borrow counterexample is
fixed in an integrated prototype. The native variant passes 256 fixed
independent inputs, but retains failures on the preserved 9,024-input candidate
packet and structured inputs. This is a partial arithmetic repair with a local
measurement-phase proof, not a new resource result.
[Terminal experiment and evidence](../experiments/arithmetic-repair-20261015/REPORT.md).

## What has passed a complete benchmark

Our original bank-swap v2 circuit passed all 9,024 shots at Q692,
rounded mean T1,481,382,858 and product 1,025,116,937,736. All value, phase and
ancilla failure channels were zero. Independent review rechecked its source,
stream, protected evaluator and score; it did not rerun the entire evaluation.
The 12:30 Singapore public refresh now reports a minimum of 682 qubits, below
our preserved local result. Our pass is not an official leaderboard entry or
an all-input correctness proof. Public Toffoli and product records are unchanged.

Generation used the external streaming path; the unchanged protected evaluator
processed the complete resulting circuit. The original ordinary submission
build remains unqualified. Its operation vector alone needs 128.94 GiB and its
local evaluation took 1:56:33.

[Original result and patch](../experiments/followup-20261015/bankswap-terminal/RESULT.md) ·
[Independent verification](../experiments/verification-20261015/independent-verification.json)

We also reproduced the existing public C5 (Q1234/T761,658) and B3
(Q1235/T761,156) circuits with complete local passes. Those are other
contributors' designs. Independent input sets expose inherited arithmetic and
phase failures despite their passing default packets.

## The newer Q692 version is a different circuit

The other research chat reduced costs and packaged v6 on the current public
source. Its ordinary and streamed builds produced identical bytes, and the
normal benchmark ran within its tested 128 GB virtual-memory limit. Peak
resident memory was 74.56 GiB; local runtime was 47:58.34.

However, the complete 9,024-shot benchmark **failed**: three value mismatches,
two phase-failure batches and three ancilla-failure batches. Its score is
unqualified. It does not inherit the original circuit's pass.

The unchanged protected loader reports Q692 and 1,413,812,844 operations.
The source emits 479,915,092 Toffolis. These are diagnostic generation counts,
not a scored mean or a replacement for the original passing result. The
45-minute official workflow also still needs runner-specific verification.

The terminal evidence has been copied into this publication snapshot, leaving
the active research directory untouched:
[receipt](data/q692-normal-v6-snapshot.json) ·
[complete failed log](data/q692-normal-v6-failed.log).
Diagnosis and arithmetic repair continue separately. No later prototype is
promoted here without complete passing evidence.

## Gate savings that have not qualified

The following are diagnostic comparisons, **not leaderboard results**.
The savings compare baseline and candidate on identical inputs with aligned
original measurement events.

| Experiment | Evidence | Outcome |
|---|---|---|
| C5 cache, Q1234 | 9,536 paired shots; three fewer executed Toffolis per shot | Full benchmark failed: 12 value mismatches, nine phase batches |
| B3 cache, Q1235 | 9,536 paired shots; about four fewer executed Toffolis per shot | Full benchmark failed: 16 value mismatches, 11 phase batches |
| Wider B3 cache, Q1239 | 512 paired shots; mean saving 74.91796875 Toffolis per shot | Independent/structured correctness failures retained; no full passing benchmark |
| B3 guarded-zero rewrite | Two emitted CCX deletions proved exact | Full benchmark failed; emitted savings are not a scored mean |

All compared states and phases match the corresponding baseline in these paired
tests; the observed failures are inherited. The wider design is useful evidence
that spending extra qubits can reduce executed gates. Repairing the arithmetic
may cost gates, so only a complete repaired benchmark can establish a net record.

[Toffoli cycle](../experiments/toffoli-readiness-20261015/REPORT.md) ·
[Product cycle](../experiments/product-focus-20261015/REPORT.md) ·
[Guarded-zero cycle](../experiments/followup-20261015/REPORT.md)

## How to read the figures

- Public points require official positive integer metrics with consistent
  product arithmetic, and either acceptance or an explicit score-only rejection.
- Our Q692 point requires the complete local pass and its preserved source,
  stream and verification receipt. It is styled separately from public scores.
- Failed candidates, generated counts, component tests and paired savings
  never appear as scored performance points.
- The gold frontier contains only public records. The local Q692 result is
  shown alongside it; it has not been merged into the public leaderboard.

The source data, rendering scripts, PNGs and SVGs are tracked. The figures can
be regenerated offline with `python scripts/frontier_plot.py`.

## What remains

Repair the lower-Toffoli arithmetic and retain exact gate savings; continue
product optimization separately. Preserve the original width result and its
successor's failed evidence, with further width work deferred. Each final candidate needs a complete
unchanged benchmark, relevant independent checks, preserved source/stream
provenance and a fresh comparison with the relevant public record.

The product and Toffoli cycles reported here are terminal. The Q692 arithmetic
diagnosis belongs to the separate active chat. No challenge submission has
been made from these cycles.
