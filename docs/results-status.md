# Results and submission status

**Active run, 15 October 2026, 22:39 Singapore:** public records refreshed
and unchanged. User priority is product, then Toffolis, then qubits;
submission mode is **queue**. Four isolated experiments are in progress,
with two complete local passes queued below. Public refresh at
16 October 01:46: Q678, T753771/Q1464 and product939347948 unchanged
(1571 submissions,1230 eligible).
[Run log](../experiments/autorun-20261015-2239/LOG.md).

**New lowest local T,16October01:45:** unchanged benchmark passes9024shots,
allchannels0, **T753721/Q1468**. Nonce644 lowest from1;731 screened. Final
fixed16384 paired census passes670candidate versus674parent failed batches,
5.76599 versus5.80042 per packet, dirty0. Every pre-tail record matches the
frozen stream. Fullsource/stream archived and owned tree removed. Queued only.
[Benchmark evidence](../experiments/wide15-record-20261016/STATUS.md) ·
[Queue](../experiments/autorun-20261015-2239/READY.md).

**New complete local pass, 16 October 00:09 Singapore:** the wide four-stage
candidate passes the unchanged benchmark: **T753745/Q1464**, all 9024 shots,
zero value/phase/ancilla failures. Nonce92 is lowest from1;164 screened. The
fixed final16384-batch paired census passes674candidate versus678parent
failed batches,5.8004 versus5.8348 per packet, zero dirty. **Queued, not
submitted.** [Benchmark evidence](../experiments/wide-record-20261015/STATUS.md) ·
[Queue](../experiments/autorun-20261015-2239/READY.md).

**Frozen product candidates, not yet benchmarked:** product25 native27tests
and byte comparison pass at Q1234. Full32768 paired batches/source measure
58.15368 +/-0.44249 T saved,17.82724 failures/packet versus17.84445 parent,
zero dirty. Older compact11/four-stage gates also pass. These are
diagnostic savings, not completed benchmark scores. Search cost remains gated.
[Candidate evidence](../experiments/product-exact-20261015/STATUS.md).

**Search tools:** curve preparation now measures 9.39 microseconds per fresh
shot and agrees with the protected reference. The integrated scalar screen
is 4.23x faster on an identical test. The integrated SIMD/SHAKE exact bucket
screen passes protected replay controls but still projects63–84hours on64threads
at the old product failure rate. Zero-MR output slicing is faster but disabled
for rejection while the global RNG-independence proof remains unresolved.
The arithmetic model remains advisory; only exact simulation can reject a
nonce. [Curve evidence](../experiments/scalar-fast-20261015/STATUS.md) ·
[SHAKE evidence](../experiments/shake8-20261015/STATUS.md).

**New diagnosis:** all 31 saved failures previously lacking walk-rail events
are localized to payload folds (29) or square merged windows (2), with
production-wire observations and unchanged protected-simulator agreement.
The tested window widening costs about 1065 T and is unsuitable for the
current records. No cheap exact repair is qualified.
[Source-bound report](../experiments/failure-floor-20261015/STATUS.md).

Updated 15 October 2026, 19:19 Singapore. **Our T753,771/Q1464 submission is
officially scored and is the current public Toffoli minimum.** The service
rejected it solely because its product did not improve the scalar best.
The separate Q692 width pass remains local and unsubmitted.

| Objective | Current public record | Our status |
|---|---:|---|
| Minimum peak qubits | 678 (refreshed16October00:19) | Q692 complete local pass; width work deferred |
| Minimum rounded mean executed Toffolis | **753,771 at Q1464** | **753721/Q1468 local pass queued**;753745/Q1464 alternative; official753771, `3f32acd2` |
| Minimum Q × T | 939,347,948 at Q1234/T761,222 | Our product 1,103,520,744 is 17.48% worse |

Official source: `5a7c390233c72133df9b591c92e43422c5892142`, from our candidate
`7ff2ba53`. The official score exactly matches the complete local benchmark.
The gain over the previous B3 Toffoli minimum is 7,385 (0.97%), for 229 more
qubits. Next strict targets are T753,770 or product 939,347,947.
[Official result](https://api.ecdsa.fail/api/submissions/3f32acd2-71bf-4cc7-bae6-7407be97fe3b) ·
[source-bound report and evidence](../experiments/nonce-screen-20261015/STATUS.md) ·
[refreshed frontier](frontier-results.md).

**Earlier product study, 22:07 Singapore: blocked by search cost.** On the public
tip `4b2ec52f`, the record circuit fails 17.69 batches per packet on fresh
inputs, and its fresh mean (761,221.70 T) already sits at the strict threshold.
A lowest-pass screen would need about 1.6×10⁸ nonces, about 58 days on 64
threads. The width-free cache saves only 2.2 ± 1.2 T there. No candidate was
built. [Measurements, search-cost figure and unblock plan](../experiments/product-tip-20261015/STATUS.md).

**Current research priority:** lower executed Toffolis and lower Q × T.
Width-only optimization and Q692 submission engineering are deferred; existing
width results and failures remain preserved.

**Current disclosed-failure-rate policy:** nonce screening is allowed only
after freezing the circuit and measuring a fresh-input failure rate no worse
than the beaten record and never over 18 batches per packet. Our submitted
stream has 159 failed batches on 262,144 independent shots: 5.47 expected failed
batches per packet, compared with B3's 17.73. Nonce 375 is the lowest passing
nonce from 1, with 593 screened. The scored packet passes all 9,024 shots;
random and structured counterexamples remain disclosed.

**Earlier correctness diagnostics:** the experiments below predate the final
frozen submission. Their unqualified status applies to those exact circuits,
not to the later official score. A census of 262,144 independent inputs per
stream gave these fresh-pass probabilities:

- the former public B3 Toffoli leader about 2–6×10⁻⁹ (two independent censuses);
- the C5 product baseline about 1.5×10⁻⁸;
- the best of the earlier 29-stream census about 10⁻³ (the final stream is about 0.4%).

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

Tail smoothing costs about 37 Toffolis; rails must widen with their YP8 anchors; more than
+2 bits stops helping (the tail cliff returns, and non-walk failures rise with
width). Convergence-aware envelopes with a rebuilt tail descent eliminate
unconverged walks and halve walk failures (762,908 T, 3.79), but non-walk
failures rise, so every walk-only lever plateaus at about 3.7–4.2. A constant ~1.1 batches of non-walk failures remains.
None reaches the < 0.1 expected failed batches needed for a high fresh-pass probability.
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

Our wide smooth Leapfrog with nonce 375 has both a complete local pass and
matching official evaluation: **Q1464/T753,771/product 1,103,520,744**. It is
the public Toffoli minimum in the refreshed 1,569-submission snapshot, with a
score-only rejection rather than a correctness rejection.

Our original bank-swap v2 circuit passed all 9,024 shots at Q692,
rounded mean T1,481,382,858 and product 1,025,116,937,736. All value, phase and
ancilla failure channels were zero. Independent review rechecked its source,
stream, protected evaluator and score; it did not rerun the entire evaluation.
An earlier public refresh reported a minimum of 680 qubits (679 at 22:07), below
our preserved local result. Our pass is not an official leaderboard entry or
an all-input correctness proof. The later Toffoli submission is a different circuit.

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
- Our Q1464/T753,771 star uses official metrics, including the explicit
  score-only rejection reason. It belongs to the public frontier.
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
been made from those earlier failed cycles. The later frozen smooth circuit
was submitted and officially scored as `3f32acd2`.
