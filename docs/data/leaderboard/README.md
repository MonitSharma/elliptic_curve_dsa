# Public leaderboard snapshot

Retrieved **17 October 2026, 12:36 Singapore time** from the public
[ECDSA.fail API](https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74/submissions).
The website was also inspected: 45 current frontier points, 1,061 historical
frontier advances, product 939,223,314, minimum width 676, and minimum Toffolis
753,694. Historical advances are different from current nondominated pairs.

- `submissions.json.gz`: complete original API response, including all submission
  notes, losslessly compressed with a fixed gzip timestamp.
- `benchmark.json`: original benchmark metadata, including current best metrics,
  scalar mode, and promoted source revision.
- `snapshot.json`: retrieval time, source URLs, and SHA-256 hashes of the
  **uncompressed original responses**.
- `frontier.json`: generated compact records for the 45 nondominated pairs.
- `summary.json`: generated counts, objective leaders, highlighted submissions,
  preceding product record, and strict gate thresholds for beating the product.

The full responses are saved here so a clone can regenerate the figures without
the ignored local `research-output/` folder or a network connection. Existing
14 October evidence remains in that folder and is historical.

## Regenerate

From the repository root, with the research requirements installed:

```bash
source ./activate.sh
python scripts/plot-leaderboard-records.py
```

To replace this snapshot with fresh public data and regenerate the analysis:

```bash
python scripts/plot-leaderboard-records.py --refresh
```

Review the dated README, narrative report, and this snapshot description after a
refresh. The script regenerates figures, the frontier table and JSON summaries;
it does not rewrite historical prose or local benchmark scores.

## Inclusion and interpretation

Include an accepted submission, or a rejection whose reason is exactly
`score did not improve current best`, only when it has positive official Q/T
metrics and an official score. Every included record must satisfy `score = Q × T`.
Exclude failed, cancelled, differently rejected, pending and claimed-only entries.
Require the best derived product and metrics to match the benchmark metadata.

Sort by increasing qubits, then Toffolis, then creation time and submission ID.
Keep a pair only when its Toffoli count strictly decreases; identical resource
pairs receive one earliest representative. The current data give 1,584 total
records, 1,241 eligible scores and 45 distinct frontier pairs.

The frontier is drawn as a step function: at a fixed qubit budget, the best known
Toffoli count is constant until another measured circuit fits. The full view uses
a logarithmic Toffoli axis. The close-up uses a narrow linear range, explicitly
marked as enlarged, so small improvements remain visible. Q means peak logical
qubits; T means rounded mean **executed** Toffolis, not emitted gates or depth.

Product history is the strict running minimum of eligible scores, ordered by
submission creation time and shown in Singapore time. It records when entries
were submitted, rather than their later promotion times. The full plot starts
at zero; the recent-record detail is explicitly enlarged. The 91.27% baseline
reduction belongs to the cumulative challenge history, not one contributor.

Official finite-packet success and resource Pareto membership do not establish
all-input circuit correctness. Submission notes preserve the authors' disclosures
and attribution; the plot refresh does not rerun the official circuit benchmark.
