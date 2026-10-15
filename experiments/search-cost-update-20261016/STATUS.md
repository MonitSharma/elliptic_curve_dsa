# Search-cost update — research projection

The historical search-cost figure is preserved. This new figure uses the
integrated exact screener's completed1024-nonce measurements:38.37 seconds at
two workers and6.538 seconds at16 workers. The original128-nonce protected
comparison used284.85 thread-seconds. All screened decisions in those control
populations are exact; these timings are not resource records.

Curves use p=(1-lambda/141)^141 and mean search length1/p, with ideal scaling
to64 threads. Actual64-thread throughput has not been measured. Changing the
failure rate also changes early-rejection work, so the constant-cost curves
are planning estimates. The compact11 census point supplies its observed
failure rate; timing was measured on the original public product source,
and compact11 throughput remains unmeasured. No product search was launched.

Provenance: completed bucket-screen logs and terminal checkpoint archive in
`../prefilter-20261015/`; compact11 full fresh32768-batch paired census in
`../product-exact-20261015/`. Numeric inputs and assumptions are in `data.json`.
The faster zero-MR value tools are excluded because the source-bound global
RNG-independence proof remains unresolved. No heuristic prediction rejects a
nonce without full exact simulation.
