# First divergence of the wide circuit's deterministic value failures

Completed 15 October 2026. Observation only: **no qualified score, no source
repair.** This experiment traces the 186 deterministic value failures from the
[failure census](../failure-census-20261015/STATUS.md) of the wide cap1536
circuit (`95e771ba…`) to the first leapfrog walk tick where an exact field check
fails.

## Observer and controls

- **Private copy:** `/home/hclau/ecdsa_research/trace-value-20261015/observer-b3`,
  copied read-only from `dynamic-pool-20261015/wide-b3`
  ([patch](evidence/observer.patch), `9f19cad1…`).
- **What it marks:** `value_trace.rs` extends `rail-repair-20261015/rail_trace.rs`.
  It records the walk rails before and after every `fwd_tick` and `rev_tick`
  (1,116 marks: 140 forward and 139 reverse ticks in each of the divide and
  multiply legs). It runs on the raw pre-Y33 op stream in the observation
  simulator. Three checks:
  - **Forward:** the observed rails must equal exact modular arithmetic of
    the entry rails under the observed tape letter.
  - **Reverse:** every `rev_tick(t)` must restore the rails observed at the
    matching `fwd_tick(t)` entry.
  - **Endpoint:** after the last forward tick, both rails must be ±1.
- **Gate-inert:** the build then continues normally. Its final `ops.bin` is
  **byte-identical** to the parent (`95e771ba…`). The observation simulator
  equals the protected simulator on every qubit, bit, phase and executed Toffoli
  count in every batch.
- **Controls:** all 186 inputs fail on the raw stream too. None of the 256
  independent inputs fails, and none produces any event (no false positives).

## Result

| First divergence | Inputs | Share |
|---|---:|---:|
| Forward walk rail, **divide** leg | 83 | 45% |
| Forward walk rail, **multiply** leg | 72 | 39% |
| No walk-rail event (unlocalized: not proven outside the walk) | 31 | 17% |

No reverse-restoration or endpoint fault occurs *first*; those appear only
downstream of a forward error.

> **Correction (independent audit, `trace-audit-20261015`):** the first analyzer
> counted a zero difference as a power of two, and the earlier claim that "153 of
> 155 are exact ±2^k" was wrong. The correct split of the 155 first forward
> violations: **98** have a nonzero ±2^k target delta, **55** have a correct
> target with a changed source rail, and **2** have other target deltas.
> `analyze.py` is now fixed (zero excluded, families kept apart). A power-of-two
> delta is consistent with truncation but does not by itself prove a range
> overflow.

**Two distinct sub-families:**

1. **Mid-walk target overflow (ticks 27–129, 83 inputs).** The updated target
   rail exceeds its fitted width. The difference is typically 2^(w+1)
   (35 cases), 2^w (11) or 2^(w−1) (8), so the result needed one or two more
   bits than the envelope provides.
2. **Late-tail corruption (ticks 130–137, 72 inputs).** Tick 136 alone accounts
   for 40, at rail width 5. In 30 of those the *source* rail changes while the
   target is correct. These are slow-converging walks whose values are still too
   large for the narrowing tail rails and terminal fusions. This is consistent
   with the earlier finding that two extra walk rounds (`margin3` → `margin3-tail2`)
   cut value failures from 10.8 to 6.9 per 10⁴.

## Root cause in the source

The leapfrog envelope is the first column of
`leapfrog_data/pack_t0hat_tail0_138_steps_k770_lw2.txt`. Its header states:

> Peel fit: R=138, fit-sample budget 0.00077 per walk (1555 walks dropped of
> 17766 dumped, 4000000 walks)

The widths were fitted to **deliberately drop about 0.08% of walks per leg**,
leaving the remainder to the ground validation nonce. The measured
first-divergence rates on the wide circuit, about 3.2×10⁻⁴ (divide) and
2.7×10⁻⁴ (multiply) per shot, are this designed-in budget. Extra width from
cap1536 has absorbed part of it.

## Correction to an earlier claim

The [guard sweep](../guard-sweep-20261015/STATUS.md) walk model used
`pingpong.rs`'s `PP_WIDTH_SCHEDULE`. The submission instead runs the leapfrog
walk (`LEAPFROG_SUBMISSION = true`), whose rails come from the table above. That
model's conclusion, that the walk is not the main failure source, is
**withdrawn**: this exact trace shows that 84% of value failures start in
leapfrog walk rails. The guard-knob results (no reduction from
`FOLD_GUARD`/`ERASE_COMPARE`/other guards) still stand.

## Next repair (not yet done)

Refit the leapfrog envelope and tail with a tiny drop budget, for example
≤10⁻⁶ per walk. Concretely:

- widen the mid-walk rails by about 2 bits;
- extend or widen ticks 130–139, including the terminal fusions that assume
  convergence;
- measure the complete cost with the census.

A rough upper estimate for +2 bits on every walk tick in both legs is a few
thousand Toffolis, inside the wide circuit's 7.4K margin below the record. This
estimate is unverified. The 31 failures with no walk-rail event need a separate
payload-replay observer.

## Provenance

PID 3203337, exit 0. Build 1m, generation and observation 1:44, 3.99 GB RSS.
`evidence/` holds the compressed trace log, all first-divergence events,
`first-divergence.json`, the packets, manifest, patch, and binary and stream
hashes. Reproduce with `run.sh` (calls `prepare.py`) and analyze with
`python -X utf8 analyze.py evidence/events.txt 186 out.json`.
