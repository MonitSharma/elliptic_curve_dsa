# Wide `smooth` circuit — officially scored public Toffoli minimum

15 October 2026. **Complete local pass of the unchanged official benchmark:
1,464 qubits × 753,771 executed Toffolis** (score field 1,103,520,744).
The previous public Toffoli minimum was 761,156 (B3, Q1235). This entry is 7,385 T
lower (−0.97%). It was **submitted at 19:13 Singapore on 15 October 2026** as
[`3f32acd2`](https://api.ecdsa.fail/api/submissions/3f32acd2-71bf-4cc7-bae6-7407be97fe3b).
**Official evaluation finished at 19:15:55 Singapore**, confirming **Q1464,
T753,771, product 1,103,520,744**, exactly matching the local score.
Its status is `rejected` with reason `score did not improve current best`.
This is a score-only rejection: the 19:19 public refresh places it at the
lowest Toffoli coordinate and on the public Pareto frontier. The product leader
remains 939,347,948; this entry's product is 17.48% worse and was not promoted.
Official source: `5a7c390233c72133df9b591c92e43422c5892142`.

This is the first experiment under the **disclosed-failure-rate standard** the
user adopted on 15 October 2026 (see `AGENTS.md`). That standard replaces the
earlier no-nonce rule. An identity-tail nonce may be searched only on a frozen
circuit whose fresh-input failure rate is at or below that of the record it
beats. The nonce, the census and the number of nonces screened are published.

## Result

| | Public B3 (previous low-T) | Our official entry |
|---|---:|---:|
| Peak qubits | 1,235 | 1,464 |
| Local reproduced mean executed T | 761,155.566 | **753,770.963** |
| Official rounded T | 761,156 | **753,771** |
| Fresh-input failed batches per 9,024-shot packet | **17.73** | **5.47** |
| P(pass a fresh packet) | 5.9×10⁻⁹ | 3.8×10⁻³ |
| Identity-tail nonce | 1,013,008,676,774 (ground, count undisclosed) | **375** (lowest passing from 1; 593 screened) |

Official benchmark (`benchmark.sh`, unchanged harness, bubblewrap sandbox):
all 9,024 shots OK; 0 classical mismatches, 0 phase-garbage batches,
0 ancilla-garbage batches. Stream SHA-256
`01aad987cfe03e7ca97df6f3dcd26085a21a5836aa6e661ec8fbd9c9c1b63740`,
10,518,003 ops. Protected files (evaluator, simulator, circuit, curve,
`benchmark.sh`, Cargo files, toolchain) match public B3 byte for byte
(`evidence/protected.sha256`).

## Circuit

The circuit is the wide B3 derivative censused in
[failure-census-20261015](../failure-census-20261015/STATUS.md), plus the
nearly free tail smoothing from
[widen-walk-20261015](../widen-walk-20261015/STATUS.md). It contains:

- public B3 (`b3c9fdd6`, jackylee0424 and krishparadox lineage);
- our 14–15 October repair lineage: exact square +2 producer, tick-104
  57-bit fold window, the terminal exact overflow route, shared exact split
  scopes and the reworked ping-pong divider. Three hash-bound rewrite tables
  (`y42_bound_pass`, `square_guard`, `linear_restore`) apply only to B3's
  stream and are disabled;
- strict fresh-wire allocator restoration
  ([dynamic-pool-20261015](../dynamic-pool-20261015/STATUS.md)), so the walk
  cap can rise to 1,536 qubits; the peak is 1,464;
- the smoothed tick-137/138 walk tail (`9 9 8 7 6`, `7 7 6 6 5` in place of
  `6 6 6 6 5`), +37 T for about −1.4 failed batches;
- `TAIL_NONCE = 375`.

Server branch `research/toffoli-smooth-n375`, commit `7ff2ba53` on `b3c9fdd6`
(local only, not pushed). Only `src/point_add/` differs.
Patch: `evidence/candidate-7ff2ba53.patch.gz`.

## Screen

`screen/` is a research crate built against the protected library. It reuses
the census crate's copies of the evaluator loader, curve, Fiat-Shamir seed and
`run_tests`, all verbatim. For each nonce it rewrites only the 96-op X;X tail,
exactly as the submission's `apply_tail_nonce` does. It hashes the fixed
prefix once and runs the evaluator's batches in order through one simulator
that shares the packet XOF, stopping at the first failing batch. The selected
nonce is then re-run with the verbatim `run_tests`.

**Policy, declared before running:** screen nonces 1, 2, 3, … in ascending
order and select the lowest passing nonce. No nonce was chosen for its T.

Checks:

1. **B3 reproduction.** On the public B3 stream (`0f10de57…`), `@official` and
   the screener at B3's own nonce both pass, with mean 761,155.565714. This
   equals the official score exactly (`evidence/validate/`).
2. **Self-checks at start-up.** The prefix-hash seed equals the verbatim seed,
   and a changed nonce leaves qubit count, bit count and registers unchanged.
3. **Early-abort statistics match the census.** Mean first failing batch over
   failing nonces: B3 8.18, against 7.95 predicted from 17.73 failed batches;
   smooth 24.22, against 24.37 predicted from 5.77 (`evidence/control/`,
   `evidence/smooth/`). None of 128 B3 nonces pass.
4. **Screen outcome.** 593 nonces screened in 118 s on 32 threads. Every nonce
   from 1 to 374 fails; 375 is the only pass. Its verbatim re-check passes all
   9,024 shots with total T 6,802,029,174, identical to the official
   benchmark.

## Fresh-input census of the final stream

Census crate, label `final-n375`, 4,096 batches (262,144 shots), 32 threads:
159 failed batches (138 wrong-value shots, 24 phase-only shots, 0 dirty), so
**5.47 failed batches per packet**, with a fresh-input mean T of 753,763.5. The
earlier three replicates on the same circuit with B3's nonce gave 5.27, 5.99
and 6.06. The tail is an identity, so these measure the same circuit.

## Caveats (disclose with the submission)

- The circuit is **not correct on every input**. About 5.5 of 141 batches fail
  on a random packet, mostly deterministic wrong values from walk-rail
  overflow, plus a floor of about 1.1 batches outside the walk
  ([trace](../trace-value-20261015/STATUS.md)). It passes the scored packet
  because of the disclosed nonce. Its failure rate is about a third of the
  incumbent record's.
- Structured inputs P = −2A and zero-multiplicand cases fail (128 of 256 in
  the structured family). The benchmark's random sampling reaches them with
  negligible probability; B3 shares this limitation.
- Peak width rises from 1,235 to 1,464, so Q × T is about 17% worse than the
  product record. This is a Toffoli-only record candidate.

## Files

- `screen/` — screener source (`src/screen.rs` is new; `main.rs` and
  `official.rs` are the census crate's verbatim evaluator copies).
- `run.sh`, `run-benchmark.sh` — server launchers (nohup, PID, logs).
- `evidence/` — score, benchmark log and status, protected and input hashes,
  per-nonce screen logs, B3 control, B3 validation, final census, the
  candidate patch and its diff against B3.
- `SUBMISSION-NOTE.md` — draft note for `ecdsafail submit`.

## Submission-readiness audit — 15 October 2026, 18:58 Singapore

Read-only inspection confirmed that server commit `7ff2ba53` is on the stated
branch with a clean working tree. Its production-code diff matches the saved
benchmark-time diff; all ten changed paths are inside `src/point_add/`. The
saved benchmark log and source patches match the server copies, and the stream
and score hashes match the benchmark receipt. All nine checked protected files,
including the manifest, also match the current public source `4b2ec52f`.
This audit verifies the existing pass; it is not a new benchmark execution.

A fresh public API snapshot still contains 1,568 submissions, with minimum
Toffoli 761,156 and minimum product 939,347,948. Recounting the saved census gives
159 failed batches, 138 value-failing shots, 99 phase-failing shots (24 phase-only;
75 also value-failing), and zero dirty-ancilla shots. All nonces 1–374 have
recorded failures; 375 is the only pass among 593 recorded nonce evaluations.

The current official CLI source requires a public note of at least 5 KiB, plus
`--model` and `--harness`. The previous 2.7 KiB draft was too short; the expanded
note meets that requirement. Use `--note-file` and the prepared
`DEPENDENCIES.json`, which attributes direct baseline submission
`26dd1d00-8e45-4f13-adcf-5eac665ca15f`. The existing candidate directory contains
the required manifest and editable path; a new CLI clone is unnecessary. The
CLI archives the current `src/point_add/` contents and the service evaluates
them remotely. It does not require a GitHub push or upload the research repo.
The measured server tarball is 2,627,466 bytes, below the CLI's 25 MiB limit.

The benchmark currently uses scalar product promotion and has claimed-score
prefiltering disabled. This candidate targets the Toffoli coordinate; it may
receive official metrics without promotion to the product-leading source.
The CLI itself was not installed or executed during this audit; its public
source was inspected. No API key was accessed, and no submission was made.

`evidence/readiness.json` records the checks and refreshed record IDs;
`evidence/server-readiness.json` binds them to the server source and artifacts;
`evidence/manifest.sha256` hashes the experiment files. A narrow `.gitignore`
exception now includes `evidence/score.json` in an ordinary research commit.
The experiment also has a `.gitattributes` exception to preserve the exact
bytes covered by its hash manifest across Windows and Linux checkouts.

## Submission — 15 October 2026, 19:13 Singapore

At the user's request, the official ECDSA.fail CLI was installed on `smu_server`
and authenticated using the local ignored `.env`. The credential was not printed
or copied into this repository. The unchanged, clean `7ff2ba53` candidate was
uploaded with the exact `SUBMISSION-NOTE.md`, `DEPENDENCIES.json`, model
`Claude Opus 5.5`, and harness `Claude Code`. The CLI's `submit --help` was checked.

- Submission: `3f32acd2-71bf-4cc7-bae6-7407be97fe3b`.
- Validation job: `81895a54-d8c4-479b-ae39-ea62654e8e85`.
- Initial response: submission `validating`, job `queued`; no official score yet.
- B3 dependency declaration was recorded; attribution judgment is pending.
- Receipt: `evidence/submission-response.json`.
- Latest public status snapshot: `evidence/submission-status.json`.

**Terminal result (checked 19:19 Singapore):** the service returned official
metrics Q1464/T753,771 and score 1,103,520,744. The source commit created for
this submission is `5a7c3902`. The sole rejection reason is not improving the
scalar product. The initial response above remains preserved as an earlier
receipt; `submission-status.json` now contains the completed result. No second
submission was made. B3 dependency attribution is a separate judgment and is
not inferred from the scoring status.

The service evaluates the editable source against public base `4b2ec52f`.
No local circuit edits, nonce changes or new research calculations were made.
An initial shell wrapper failed parsing before it issued any upload; the saved
wrapper then performed one successful submission. The CLI's runtime was unpacked
from the official Bun release using Python because the server lacks `unzip`;
system packages were not changed.

Server directory: `/home/hclau/ecdsa_research/nonce-screen-20261015/`.
