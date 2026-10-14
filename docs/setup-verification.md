# Setup and result verification provenance

This document separates the initial Mac installation from subsequent research.
For the runnable CPU-server procedure, use [SERVER_HANDOFF.md](SERVER_HANDOFF.md).
Linux execution is not yet verified here.

## Initial installation snapshot

Verified on2026-10-14T11:12:40.088941+08:00 (Asia/Singapore).

- Repository: https://github.com/Layr-Labs/ecdsafail-challenge.git
- Root base commit: `b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7`.
- Rust1.93.0; rustc254b59607; cargo083ac5135.
- Python3.13.7; Bun1.4.3; ecdsafail v2026.10.13-1.
- Activation worked in bash and zsh; optional Python compatibility checks passed.
- Official locked release build and macOS-confined benchmark passed.
- All9,024 forward shots passed; output, phase and ancilla failures were zero.
- Mean executed T761155.566; peakQ1235; rounded product940027660.
- Operations11,668,991.

At initial setup, candidate source and protected files were unchanged and the
harness appended one results row. Later research adds circuit prototypes and
additional harness-appended rows; that initial statement does not describe the
current dirty checkout. Protected files remained unchanged throughout the campaign.

Evidence: `research-output/baseline-score.json`,
`research-output/benchmark-20261014-110947.log`, and
`research-output/setup-manifest.json`. Subsequent Z3 installation is pinned in
`requirements-research.txt`; it was not part of the initial installation snapshot.

## First root experiment

The exact implication cleanup saves1.493462T on the candidate's paired canonical
packet, but the complete official run fails11 classical checks and9 phase batches.
The incumbent fails identically on that packet; ancilla failures are zero.
`EXPERIMENTAL_FINAL_CLEANUP` remains false. The root default was restored and
reproduced the passing Q1235/product940027660 baseline.

See [optimization-iteration-1.md](optimization-iteration-1.md),
`research-output/canonical-inheritance.json`, source/stream archives, and
`research-output/iteration-1-logs/`. The latter preserves important logs originally
under `.tools/`, which is excluded from the transfer archive.

## Three-track campaign

Independent starting revisions:

| Track | Base | Current status |
|---|---|---|
| Qubits | `4ef906688f6dfb422aa8dd10d3d07265839e2f3c` | DefaultQ694; tested693-wire reciprocal component only |
| Toffolis | `b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7` | Phase-reader fixtures pass; zero savings on full incumbent stream |
| Product | `c5bb1ec876db859a3f9f8a9052c140a145df834e` | Official baselineQ1234/T761658/product939885972 reproduced |

The product benchmark passed all9,024 output/phase/ancilla checks. Its compressed
ops SHA256 is `49b35cf7640ebd529d76894eb8bef93ebf57e7e970fe14b3c27c8c5feb6e73e4`.
After the inactive research helper changes, the default compact stream was rebuilt
byte-identically. Logs: product `research-output/official-baseline.log`,
`default-byte-rebuild.log`, and `default-byte-identity.log`.

Qubit fixtures pass12 tests (one existing research test ignored). The compact
reciprocal covers512 cases and903,168 independent measurement-phase coefficients;
columns10 and85 each save104 emitted Toffolis per V-form call. Its arithmetic
identity is solver-proved on the specified domain at widths2–8,16,24. These are
component results, not a new complete693-Q circuit or an official score.

Both gate tracks' two native phase-reader fixtures and stale-control negative
control pass; their full-stream scans find zero savings. Partial guard transplants
were not qualified or installed. No nonce search, account login or public submission
was performed. All delegated agents were blocked by usage limits before research;
the primary agent did this iteration.

Machine-readable status: `research-output/parallel-20261014/campaign-status.json`
and each track's `research-output/track-result.json`. Full interpretation and next
work: [parallel-campaign.md](parallel-campaign.md).

## Limits

The scorer checks forward outputs, phase and ancillas; it does not run the
forward/reverse identity test claimed in the archived upstream README. Separate
component/paired inverse tests supplement it. Reported population failures in
inherited approximate circuits limit what one passing packet establishes.

Local hardware:36GiB RAM,12 logicalCPUs. The low-Q stream's vector alone is59.4GiB;
full low-Q official verification was not performed on this Mac. Plan larger-memory
server execution, initially one heavy benchmark at a time.
