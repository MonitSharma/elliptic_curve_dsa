# Guard-bit sweep on the wide B3 research base

Completed 15 October 2026. Diagnostic only: **no qualified score.** This sweep
asks whether widening B3's named guard or compare windows can lower the
fresh-input failure rate cheaply. It cannot: the dominant failures lie elsewhere.

## Setup

- **Base:** a private copy of `dynamic-pool-20261015/wide-b3` (cap1536, stream
  `95e771ba…`), at `/home/hclau/ecdsa_research/guard-sweep-20261015/base`. The
  other agent's checkout was not modified.
- **Override mechanism:** `build()` deliberately clears the process environment
  and installs a fixed recipe (`mod.rs`, `clear_process_env`). The recipe pins,
  for example, `FOLD_GUARD=20` and `ERASE_COMPARE=20`, not the 25/24 in the
  visible `env_raw` table. A research-only hook (`add-override-hook.py`) reads
  `GUARD_SWEEP_OVR` before the clear and applies it after the recipes. With the
  hook unused, the stream stays byte-identical to its parent (control below).
- **Earlier attempts:** two runs using `HEO_PIN_*` produced only parent-identical
  streams, because the environment is cleared. They are archived as superseded
  (`evidence/superseded/`) and contain no result.
- **Measurement:** each variant is generated, then censused on 131,072
  independent shots (2,048 batches, 6 threads) with the
  [failure census](../failure-census-20261015/STATUS.md) tool.

## Result

| Variant | Change | Stream | Q | Diag. mean T | Value /10⁴ | Phase-only /10⁴ | Failed batches /packet |
|---|---|---|---:|---:|---:|---:|---:|
| control | none | `95e771ba` (parent) | 1464 | 753,725 | 6.41 | 0.61 | 6.33 |
| walkg2, walkg3, bguard6, joint2, fitk23 | `PP_WALK_GUARD_BITS` 2/3, `I12_B_GUARD` 6, `PP_JOINT_GUARD` 2, `HEO_FIT_K` 23 | `95e771ba` (**inert**) | 1464 | 753,723–753,728 | 6.4–8.2 | 0.8–1.5 | 6.8–8.2 |
| fold22 | `FOLD_GUARD` 20→22 | `d86664da` | 1464 | 753,807 | 9.00 | 0.76 | 8.61 |
| fold24 | `FOLD_GUARD` 20→24 | none, exit 101 | — | — | — | — | — |
| erase24 | `ERASE_COMPARE` 20→24 | `dbfd41dc` | 1464 | 753,758 | 7.25 | 0.76 | 7.23 |
| flag24 | `PP_REPLAY_FLAG_COMPARE` 20→24 | `724b2ef6` | 1464 | 753,772 | 6.79 | 0.99 | 6.75 |
| chunk25 | `PP_REPLAY_CHUNK_COMPARE` 21→25 | `a5f331a7` | 1464 | 755,606 | 6.33 | **0.15** | 5.65 |

**Noise floor.** Six runs of the byte-identical parent stream on different
input labels give 7.3 ± 0.7 failed batches per packet. Only differences well
outside that band are meaningful.

- `fold24` fails construction at `y15_onefold.rs:3784`: the window bound
  `wf < Y15_WIN` is exceeded. The failure log is preserved.
- No tested knob reduces the deterministic **value** failure rate. Raising the
  fold guard or erase window adds Toffolis without measurable benefit.
- `chunk25` is the only lead. It reduces **phase-only** failures from about
  0.9 to 0.15 per 10⁴ shots, for +1,881 T. Phase-only failures are the minor
  family, so it does not change qualification prospects.

## Walk model: withdrawn

> **Correction (later the same day):** the classical model in `walk_model.py`
> used `pingpong.rs`'s `PP_WIDTH_SCHEDULE` recurrence. The submission runs the
> **leapfrog** walk (`LEAPFROG_SUBMISSION = true`), with a different tick
> structure and its own fitted rail table. The model's conclusion, that value
> failures arise outside the walk, is **withdrawn**. An exact gate-inert trace
> shows that 84% of value failures start in leapfrog walk rails, whose widths
> were fitted with an explicit 0.077%-per-walk drop budget.
> [Trace](../trace-value-20261015/STATUS.md).

The script and its output (`evidence/walk-model.jsonl`) are kept as a record of
the superseded analysis.

## Implication

The wide candidate's 7.4K Toffoli headroom below the public record cannot be
spent on these guard knobs to buy honesty. The value-failure source has since
been located: the fitted leapfrog walk envelope
([trace](../trace-value-20261015/STATUS.md)). The 186 failing inputs with exact scalars
are in `../failure-census-20261015/evidence/inputs/wide-failures.tsv`, a ready
fixture for the rail tracer.

## Provenance

Binary `f764bd79…` (hook build). Pins, statuses, generation logs, census
results and stream hashes for every variant are in `evidence/`. Sweep PID
3192716; all processes have exited. Peak usage was 6 parallel generations of
about 4 GB each, plus 6-thread censuses.
