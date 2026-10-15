# Exact SIMD census accelerator — validated

This external research runner preserves the existing labelled census inputs,
measurement draws, all quantum/classical words, phase, garbage checks and executed
Toffoli counts. It changes no submission files or official evaluator.

All 128 output rows are byte-identical to the old runner on each of the public
product source and the frozen four-stage source (91,691 classical bits). Direct
protected-simulator comparisons cover every state word, phase and Toffoli count
for 64 batches per source. A threaded partial run (first17/count11/workers3)
also matches every old-runner row, with full protected-state checks.

The 4096-batch throughput run takes40.41 seconds with four workers after shared
curve-table initialization. Its first128 rows reproduce the reference exactly.
This is a research throughput measurement, not a benchmark resource record.
The resulting failure sample is a tool-validation cohort, not a candidate gate.

The C backend retains the previously validated exact SIMD semantics and adds
per-lane popcounts of the actual classical guard for CCX/CCZ, matching the protected
counter. All R/HMR draws remain, including inactive branches. Input curve
preparation uses the separately pinned and validated public-scalar backend.

Frozen executable: `/home/hclau/ecdsa_research/simd-census-20261016/bin/simd_census_v1`.
Arguments: `OPS LABEL FIRST COUNT WORKERS OUT VERIFY_FIRST_BATCHES`.
Use final0 after validation to omit redundant protected replay. `FREEZE.json`
binds the executable, sources, external library and validation streams. Existing
live censuses are preserved; future declared samples may use this exact runner
without changing labels or batch IDs. The official benchmark remains mandatory.
