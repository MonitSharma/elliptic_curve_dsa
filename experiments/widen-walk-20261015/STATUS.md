# Widening the leapfrog walk table on the wide circuit (in progress)

15 October 2026. Diagnostic only: **no qualified score.** These are private
copies of `dynamic-pool-20261015/wide-b3`. Only
`leapfrog_data/pack_t0hat_tail0_138_steps_k770_lw2.txt` changes. Each variant is
censused on 262,144 fresh shots (`evidence/table.md`).

| Variant | Q | Diag. mean T | ΔT | Failed batches /packet | P(pass fresh) |
|---|---:|---:|---:|---:|---:|
| parent (wide) | 1464 | 753,727 | — | 7.16 | 6.4e-4 |
| `mid2`: +2 bits, ticks 2–136 | 1464 | 758,411 | +4.7K | 7.30 | 5.6e-4 |
| `smooth-x2`: tail cliff smoothed, +2 park ticks | 1474 | 759,157 | +5.4K | 5.30 | 4.5e-3 |
| `mid2-smooth` | 1464 | 758,449 | +4.7K | 4.85 | 7.2e-3 |
| `mid2-smooth-x2` | 1474 | 763,841 | +10.1K | 4.68 | 8.6e-3 |
| `mid4-smooth-x2` | 1474 | 768,478 | +14.8K | 5.03 | 6.0e-3 |

"Smooth" replaces rows 137/138 (`6 6 6 6 5`) with `9 9 8 7 6` and `7 7 6 6 5`,
removing the 3-bit cliff after tick 136. The final park rows must stay
`6 6 6 6 5` (`leapfrog.rs` `n2_loan_out` asserts 5-wire parked rails). A first
attempt that widened them failed construction and is archived in
`evidence/superseded-park/`.

**Findings so far:**

- Smoothing the tail cliff is the only effective change, and it is nearly free:
  `mid2-smooth` vs `mid2` is −2.45 failed batches for +38 T.
- Widening mid-walk rails costs about 2.3K T per bit and does **not** reduce
  failures, so the mid-walk errors are not table-width overflows.
- Extra park ticks cost about 5K T each for little gain.
- The untested `smooth`-only variant (no mid widening, no extra rows) should
  give about 4.9 failed batches at about 753.8K T. **Build it next.**

**Partial trace** (`trace-mid2-smooth/`, PID 3227601, exit 0, final stream
byte-identical, observer equal to the protected simulator). The prepare script
fell back to the *parent's* 186 failing inputs instead of this variant's own
123 (`fails.tsv`). It is valid as a measurement of mid2-smooth on those inputs:

- 71 of the 186 parent failures are fixed.
- Of the remaining 115, 81 still start at forward walk rails (39 divide,
  42 multiply), 3 at walk endpoints, and 31 with no walk-rail event.
- Independent256 shows no events.

The `fails_tsv` branch of `trace-value-20261015/prepare.py` is now fixed.
`run-next.sh` builds the smooth-only variant, then traces that variant's own
value failures. It is ready but not yet run, because the server was
unreachable at about 17:00 Singapore.

**Why widening alone may fail: a hypothesis to test.** The rails carry a parked
low bit (value = 2·register + 1), so one register wraparound shows up as a value
delta of exactly 2^(w+1). That is the most common case among the parent's 98
target-delta first violations: 43 at w+1, plus 23 sign-bit flips at w. These
are real overflows. The YP8 deep/flat choice, however, reads a fixed bit window
whose position comes from a separate anchor table
(`leapfrog_data/yp8_L22_138_anch.txt`, "anchor = choice-step width − 3"). The
wide parent already carries +3 rail bits over B3 but uses B3's anchors, and
`mid2` widened the rails again without moving the window. A walk that lags its
envelope then chooses on truncated magnitudes. Such choices are always valid,
but they slow convergence, so the walk keeps drifting and overflows the wider
rail later. Queued tests (`variants.txt`, `prepare.py` arguments
`anch_delta win_delta`):

| Variant | Rows 2–136 | Tail | Anchors | Window |
|---|---:|---|---:|---:|
| `smooth` | +0 | smoothed | +0 | +0 |
| `mid2-smooth-anch2` | +2 | smoothed | +2 | +0 |
| `mid2-smooth-anch2-win2` | +2 | smoothed | +2 | +2 |
| `smooth-win2` | +0 | smoothed | +0 | +2 |

A local check confirms the transforms: anchors fall to 3 at tick 136, matching
row width − 3, and every `LF_YP8`/`LF_YP8_LATE` length shifts by the delta.

Per the independent audit (`trace-audit-20261015`), 55 of the parent's 155 rail
first-violations keep a correct target and corrupt the source rail; 30 of them
are at tick 136, which the tail smoothing addresses. The other 98 have ±2^k
target deltas, and widening their table rows did not help. Next, inspect the
mid-walk mechanism with the audit's prepared rail-delta observer. Candidates
are rail cuts (`Y42_RAIL_DIV`) and approximate chunk-boundary compares
(`LF_CMP_FROM`), not table width.
