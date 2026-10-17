# PRODUCT179 product candidate: generating; gate and search armed

17 October 2026, Singapore. **No score yet.** Public 4b2ec52f plus the fixed
exact cache chain 1–179 (PRODUCT95's 95 stages, then 96–123 and 124–179, each
continuation declared before generation with a fixed endpoint). Checkpoint
packets so far: 115.47 T saved at stage 102 (PRODUCT95: 112.47, PLAIN67:
102.47 on the same fixed packets; diagnostic only).

- **Phase A** (`chain-a.sh`, unattended): freeze the stage-179 endpoint,
  universal certificate for stages 96–179 (4 workers), native port with byte
  identity, then the gate declared in `GATE-DECLARATION.json` (label
  `product179-gate-20261017-v1`, 32,768 batches, parent = the official
  PLAIN67 record `f2279f98…`).
- **Phase B** (`chain-b.sh`, user-approved 17 Oct): only if the gate passes,
  generate the search scripts from the verified PRODUCT95 ones
  (`make_phase_b.py`, dry-tested on PRODUCT95 data), qualify the filter,
  accept, run the lane-0 control, then launch the ascending search.
  **Threads: the user authorized about 96** (4 workers × up to 24), sized at
  launch from the 5-minute load so that 8 cores plus all other users' load stay
  free; at least 100 GB RAM must be available. This is a recorded exception to
  the usual ~64-thread limit.
- PRODUCT95's search was stopped by the user after 5.5M nonces (no pass);
  its gate verdict stands and it is superseded by this candidate.
