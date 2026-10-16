# Actual current-source attribution, per-phase addendum

The final `2a522394...` circuit reproduces every original quantum and classical
bit, phase, Toffoli count and census failure mask on the same 431 value-failure
witnesses in their 413 original 64-lane contexts. No new inputs were sampled.

An earlier local mismatch can cancel before a correct stage output. The original
whole-circuit first-event latch could therefore hide a later mismatch in another
phase. Its log and checkpoint remain preserved. The addendum records the first
payload mismatch separately in each actual source phase and snapshots both N2
parked rails at all source loan sites.

The 55 failures missed by the advisory rail classifier now separate into 34 exact
fold boundary losses (13 forward, 21 reverse), 14 dirty-loan first-add failures,
3 exact C130 square-window losses, and 4 unresolved cases. These remain 54 batches
in the fixed 4096-batch cohort, or 1.85888671875 expected batches per 141-batch
packet. This is a diagnostic cohort category, not a universal failure floor.
The older roughly 1.1 estimate concerned the unsmoothed b3 source.

The addendum archive SHA256 is
`57f220bd0c5d293940db47fbb700537ba3439a8e5b32076c38fca99b0f4ef108`.
All 17 members verify locally and its base checkpoint SHA256 matches
`ff142400c88f8b6f33aff4afdee6f5621378292a2c75c9e90415813eca337382`.
See `PHASE-ATTRIBUTION.json` for all cases, source bindings and limitations.

The separate seed-boundary replay is active. It compares actual entry and exit
against the finite 53-bit source formula, without assuming the first payload's
T=2S relation. Its raw observer reproduces `ff516396...`, and both seed boundaries
map uniquely into the actual final circuit. No repair is proposed from that
unfinished diagnostic.
