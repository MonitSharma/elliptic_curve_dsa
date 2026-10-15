# Widening the leapfrog walk on the wide circuit

15 October 2026. Diagnostic only: **no qualified score, no candidate passes a
fresh test set.** Every variant is a private copy of
`dynamic-pool-20261015/wide-b3`. Changes are confined to the leapfrog steps
table, the YP8 anchor table, the recipe's YP8 window lengths and the walk qubit
cap, as recorded in each variant's `manifest.json` and `table.patch`. Each
variant is censused on 262,144 fresh inputs (`evidence/table.md`).

## Result

| Variant | Rows 2–136 | Tail | Anchors | Window | Q | Diag. mean T | ΔT | Failed batches /packet |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| parent (wide) | — | cliff | — | — | 1464 | 753,727 | — | 7.16 |
| `mid2` | +2 | cliff | +0 | +0 | 1464 | 758,411 | +4.7K | 7.30 |
| **`smooth`** | +0 | smoothed | +0 | +0 | 1464 | **753,764** | **+37** | **5.77** (3 replicates) |
| `smooth-win2` | +0 | smoothed | +0 | +2 | 1464 | 754,569 | +0.8K | 5.37 |
| `mid2-smooth` | +2 | smoothed | +0 | +0 | 1464 | 758,449 | +4.7K | 4.85 |
| **`mid2-smooth-anch2`** | +2 | smoothed | +2 | +0 | 1464 | **758,446** | **+4.7K** | **4.18** (3 replicates) |
| `mid2-smooth-anch2-win2` | +2 | smoothed | +2 | +2 | 1464 | 759,252 | +5.5K | 4.34 |
| `mid4-smooth-anch4` | +4 | smoothed | +4 | +0 | 1468 | 763,076 | +9.3K | 4.78 |
| `mid6-smooth-anch6` | +6 | smoothed | +6 | +0 | 1472 | 767,661 | +13.9K | 5.37 |
| `smooth-x2` | +0 | smoothed, +2 park | +0 | +0 | 1474 | 759,157 | +5.4K | 5.30 |
| `mid2-smooth-x2` | +2 | smoothed, +2 park | +0 | +0 | 1474 | 763,841 | +10.1K | 4.68 |
| `mid4-smooth-x2` | +4 | smoothed, +2 park | +0 | +0 | 1474 | 768,478 | +14.8K | 5.03 |
| `mid4-smooth-anch4-x2` | +4 | smoothed, +2 park | +4 | +0 | 1474 | 768,466 | +14.7K | 4.17 |

"Smoothed" replaces rows 137/138 (`6 6 6 6 5`) with `9 9 8 7 6` and
`7 7 6 6 5`, removing the 3-bit drop after tick 136. Park rows must stay
`6 6 6 6 5` (`leapfrog.rs` `n2_loan_out` asserts 5-wire parked rails); the first
attempt that widened them failed construction and is archived in
`evidence/superseded-park/`.

**Replicates and noise.** Raising the walk cap from 1536 to 1800 or 2200 does
not bind: peak stays 1464, and both caps reproduce the `smooth` and
`mid2-smooth-anch2` streams **byte for byte** (`fbc66dbd…`, `54c83c02…`). Their
censuses are therefore independent replicates. `smooth` gives 5.27, 5.99, 6.06
and `mid2-smooth-anch2` gives 3.65, 4.51, 4.37 failed batches. Single-census
differences below about ±0.8 are noise.

## What the walk lever can and cannot do

1. **Tail smoothing is free and real:** about −1.4 failed batches for +37 T.
2. **Rails must widen with their YP8 anchors.** Widening rails alone (`mid2`)
   does nothing. With anchors shifted (`anch2`) it gives a further
   −1.6 batches for +4.7K T. A longer window does not help.
3. **More bits do not keep helping.** +4 and +6 bits, at +9.3K and +13.9K T,
   are no better than +2. One plausible explanation is that windows anchored too
   far above typical magnitudes lose precision. Another is that wider rails
   consume room that other plans size against. Neither is confirmed.
4. **A non-walk floor remains.** In both traced variants, 32 failures out of
   about 262K shots show no walk-rail event, about **1.1 failed batches per
   packet** that walk widening cannot touch. These are likely the payload-fold
   failures the other agent is studying (`equal-division-20261015`).

## Traces (gate-inert; byte-identical streams; independent256 clean)

- **`trace-smooth/`, the variant's own 131 failures:** 53 divide and 43
  multiply rail first-violations, 3 walk endpoints, 32 with no walk event. The
  tick-136 cluster is gone (1 left). Remaining rail failures spread over ticks
  30–137.
- **`margin-smooth/` and `margin-mid2-smooth-anch2/`:** the margin observer
  (`trace-value-20261015/value_trace_margin.rs`) records the exact value's
  needed bits minus the rail width at every forward tick, for those failures
  plus 8,192 independent random inputs (`random8192.tsv`, sha `fff9a490…`,
  seeded `ecdsa-research-margin-random-v1`).
  - **Typical walks have room.** Excluding fixed seed tick 0, the summed chance
    of coming within one bit of overflow is about 0.16% per walk. Failures are
    rare slow walks that run at the edge for many ticks.
  - **At the failure tick the exact value really does exceed the rail,** in
    72 of 96 (smooth) and 42 of 52 (anch2) first rail violations, almost always
    by 1 bit (occasionally 2–3).
  - **Paired comparison on the same 8,192 inputs:** +2 bits with anchors fixes
    4 of 5 walk failures (1764, 2575, 4026, 4774), introduces 1 (3808, tick 134),
    and only delays 1 (6932, tick 93 → 102). The two non-walk failures (1591,
    1614) are unchanged.
  - The greedy per-tick allocator in `margin_analysis.py` is **not usable as
    is**: it extrapolates the fixed tick-0 seed rows. Its +17–21K T estimate is
    not a result.
- **`superseded/trace-mid2-smooth-parent-inputs`** was mis-fed the parent's
  186 inputs. It is preserved but superseded.

## Where this leaves the honest route

Best variant under the record: `mid2-smooth-anch2`, about **4.2 expected failed
batches per fresh packet**, P(pass) ≈ 1.5%, at 758,446 diagnostic T (2.7K under
761,156). The honest-pass zone needs < 0.1. Decomposition:

- non-walk value failures, about 1.1;
- phase-only failures, about 0.3;
- residual slow walks, about 2.8.

Uniform widening has plateaued, so the next steps are targeted:

1. Repair the non-walk floor (payload fold boundary; coordinate with the
   other agent).
2. Make slow walks finish. The paired evidence shows they lag
   progressively, so try a convergence-aware envelope shape rather than
   uniform bits.
3. Find why +4/+6 regress before buying more width.

## Why +4/+6 regress (traced on each variant's own census failures)

| Variant | Walk-rail first | Endpoint (not converged) | No walk event | Total /262K |
|---|---:|---:|---:|---:|
| +2 bits, anchors | 52 | 5 | 32 | 89 |
| +4 bits, anchors | 69 | 11 | 38 | 118 |
| +6 bits, anchors | 77 | 7 | 57 | 141 |

Two effects, both measured:

1. **The tail cliff came back, an artifact of this experiment's builder.** As
   width grows, mid-walk failures vanish (at +6 almost none before tick 130),
   but they pile up at ticks 130–137 as source-rail corruption with a correct
   target (48 of 77 at +6). That is the original tick-136 signature. The
   smoothed rows 137/138 were fixed at 9/7 bits while +k raised row 136, so at
   +6 row 136 ends at 14 bits and row 137 starts at 9.
2. **Non-walk failures rise with rail width:** 32 → 38 → 57. Wider rails
   appear to degrade other approximate stages, plausibly the per-tick fitted
   profiles (`I35_PROFILE`, `PP_N_BADJ`, fold/compare windows) tuned to the
   original widths. The walk cap is not the limit: caps 1800 and 2200 give
   byte-identical streams.

## Convergence-aware envelopes

**Shape data.** The margin observer now also prints, per walk leg, the maximum
excess in each 10-tick bin (`WALKBINS`), and full trajectories for failing
inputs (`TRAJ`). It ran on `smooth` over four independent 8,192-input chunks:
32,768 walks, 65,527 legs, chunk hashes in `evidence/random-chunks.sha256`.
`shape_analysis.py` (output `evidence/shape-smooth.json`) shows:

- ticks 0–49 never come within 2 bits of overflow;
- P(excess ≥ 0) rises steadily from about 2×10⁻⁵ per bin at ticks 60–69 to
  about 9×10⁻⁵ at ticks 120–139.

That is lag accumulating. With trajectories held fixed, late-weighted
envelopes looked far better than uniform ones (+3 from tick 70: 0 of 65,527
legs fail, at about 3.7K T).

**Tapered designs** (deltas fall to 0 by tick 136 to keep the tail descent; anchors follow):

| Variant | Rows | T | Failed batches /packet |
|---|---|---:|---:|
| `env-greedy` | +1 on 80–99 and 110–133 | 754,527 | 5.30 |
| `env-late2` | +2 on 70–129, taper | 755,970 | 5.44 |
| `env-late3` | +3 on 70–129, taper | 757,099 | 4.68 |
| `env-late4` | +4 on 90–129, taper | 756,895 | 4.78 |
| `env-ramp` | 1→2→3 from tick 50, taper | 757,143 | 4.78 |

The model over-predicted. Paired failure locations explain why.

| Ticks | `smooth` | `env-late3` |
|---|---:|---:|
| 70–129 (widened) | 66 | **20** |
| 130+ (taper) | 17 | **33** |

Widening rescues slow walks only temporarily: they still lag and then fail in
the narrow tail.

**Rebuilt tails** (`prepare.py` tail mode `t:W-n0-n1-n2-nb/...`; inserted
ticks get anchors n2−3):

| Variant | Rows / tail | Q | T | Failed batches /packet |
|---|---|---:|---:|---:|
| `smooth-hold2` | +0; each descent row held twice | 1474 | 759,190 | 5.89 |
| `late3full-tail3` | +3 on 70–136; 3-row descent to park | 1474 | 762,908 | 3.79 |
| `late3full-tail3hold` | same, each descent row held twice | 1484 | 768,464 | 3.86 |

The trace of `late3full-tail3` on its own failures splits them as follows:

| Family | `smooth` | `late3full-tail3` |
|---|---:|---:|
| Walk-rail | 96 | **43** |
| Endpoint | 3 | **0** |
| No walk event | 32 | **45** |

So **slow walks can be made to finish**: no endpoint failures, walk failures
more than halved. But the residual moved to unwidened ticks 30–69 (22 of 43,
mostly multiply), and the non-walk family grew. Extra ticks beyond a proper
descent buy nothing.

**Conclusion.** Every walk-only lever plateaus at about 3.7–4.2 expected
failed batches, P(pass) ≈ 2%.

| Variant | Diag. T | Margin under the record |
|---|---:|---:|
| `mid2-smooth-anch2` (best under the record) | 758,446 | 2.7K |
| `late3full-tail3` | 762,908 | over |

What remains is about half non-walk failures, which grow when rails widen,
plus early-tick walk failures that appear only after the late ticks are
widened. The next lever is not more walk width. It is the room-sensitive,
per-tick fitted profiles that widening disturbs, and the non-walk (payload)
failures.

## Provenance

Server `/home/hclau/ecdsa_research/widen-walk-20261015/`, all variant, trace
and margin runs exit 0. Launchers: `run.sh` (variants), `run-trace.sh`,
`run-next.sh`, `run-margin.sh`. Local `evidence/` holds per-variant manifests,
patches, build and generation logs, census tables, compressed trace logs and
first-divergence analyses. Large source copies and binaries remain on the
server only.
