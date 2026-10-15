# Results and submission status

Updated 15 October 2026. **We have one new complete local width result and no
submission-ready original circuit yet.** The three objectives remain independent:
a lower-Toffoli result would count even if its product were worse.

## What has passed a complete benchmark

Our original bank-swap v2 circuit passed all 9,024 shots at Q692,
rounded mean T1,481,382,858 and product 1,025,116,937,736. All value, phase and
ancilla failure channels were zero. Independent review rechecked its source,
stream, protected evaluator and score; it did not rerun the entire evaluation.
This is one qubit below the refreshed public minimum, but it is not an official
leaderboard entry or an all-input correctness proof.

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

Preserve the original width result; repair and qualify its submission-oriented
successor; repair the lower-Toffoli arithmetic and retain exact gate savings;
continue product optimization separately. Each final candidate needs a complete
unchanged benchmark, relevant independent checks, preserved source/stream
provenance and a fresh comparison with the relevant public record.

The product and Toffoli cycles reported here are terminal. The Q692 arithmetic
diagnosis belongs to the separate active chat. No challenge submission has
been made from these cycles.
