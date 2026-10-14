# Overnight ECDSA research cycle

Window: **14 October 2026 18:14:23 to 15 October 2026 04:14:23 Singapore time**
(10:14:23–20:14:23 UTC). The persistent goal is active. The cycle finishes after
the window and after jobs finish or have a reproducible handoff. Finding an
original record is the objective, not an assured outcome.

## Starting evidence

- Project HEAD and fetched `origin/main`: `493655507943e7de62592c7cc4e3f0983ddd2ff6`.
  Local branch: `codex/ecdsa-research-recovery`. Existing compact changes and
  untracked qubit research output are preserved.
- Official API refreshed at the start: 1,560 submissions, 1,219 eligible records.
  Public leaders remain Q693, T761,156 and product939,681,128.
  Strict targets: Q692, T761,155, product939,681,127.
- Passing public reproduction remains Q1234/T761,658/product939,885,972.
  This is historical complete evidence, not a newly rerun benchmark.
- Compact reciprocal remains **failed full validation**, with no qualified score.
  All three preserved source hashes match the prior manifest on the server and
  in the new isolated compact checkout.
- Workspace include audit reports no missing active source includes; the five
  leaderboard admission tests pass. Missing historical artifacts remain missing.

## Isolation and capacity

Server alias `smu_server`, hostname `LHC-104-070`; ECDSA stays under
`/home/hclau/ecdsa_research`. At 10:17:29 UTC there were 144 available CPU affinity
lanes, load approximately 35, 277 GiB available RAM and 4.7 TiB free disk. Two
unrelated 18-thread jobs together used about 210 GiB. No scheduler was found.
These observations are not a reservation; refresh before launches.

New detached worktrees under `/home/hclau/ecdsa_research/overnight-20261014/`:

| Area | Baseline | Assignment |
|---|---|---|
| `qubits/base` | `c95b9325` clean | Identical failing-point replay |
| `qubits/compact` | `c95b9325` plus preserved compact changes | Paired diagnosis, then width |
| `toffoli` | `c5bb1ec8` clean | Complete fold constructor and cleanup |
| `product` | `c5bb1ec8` clean | Exact simplification and width/gate tradeoffs |

Only one large low-width job may run at once, initially with a 128 GiB virtual
memory limit. Smaller gate experiments use at most 16 GiB each. Builds use four
threads and numerical libraries one. Every long job needs `nohup`, a unique log,
PID, exit marker, source/patch hashes and exact settings. Original worktrees,
logs and streams remain preserved. The chemistry checkout is not changed.

## Research leads and limits

Three research agents own the isolated tracks. Only the coordinator pushes
project checkpoints. Their patches and compact evidence belong under
`experiments/overnight-20261014/`; large generated files remain ignored.

The refreshed public product leader's own note reports census-based cuts and
nonce selection, and describes failures on independent packets. The Q693
author likewise reports rare approximation failures. Those author reports are
research leads, not a diagnosis of our compact modification. We will not adopt
sample-only gate deletion or tune hash-derived test packets. Paired replay is
needed to establish inherited versus introduced defects.

Initial gate hypotheses are joint constructor synthesis and exact Boolean
simplification after the existing bound passes. A source change can expose
inherited approximation errors by changing the default packet. Such a failure
still disqualifies the candidate; a component saving alone earns no score.

## Checkpoint discipline

Refresh public comparisons before record claims. Keep protected files unchanged
inside every candidate. Preserve exact patches, domains, tests, counterexamples,
logs, stream hashes and resource use. Full unchanged benchmark success is
required before adding any original candidate to README result plots or tables.
Fetch and review staged changes before normal fast-forward project pushes.

No new original candidate has qualified at cycle start. Track-specific reports
will record experiments and terminal status as evidence becomes available.
